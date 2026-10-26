"""Standalone desktop host for workflow events and the phone answer channel."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys


def dependency_check():
    """Import only this application, without creating state or using network."""
    from importlib import import_module
    result = {}
    for name in ("PyQt5.QtWidgets", "requests", "qrcode", "workflow_bridge.core.weixin_notify",
                 "workflow_bridge.core.workflow_questions", "workflow_bridge.ui.weixin_questions"):
        try:
            import_module(name)
            result[name] = True
        except ImportError:
            result[name] = False
    result["independent_of_pet"] = not any(name == "aipet" or name.startswith("aipet.") for name in sys.modules)
    return result


def create_host(app):
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QAction, QMainWindow, QMenu, QMessageBox, QStyle, QSystemTrayIcon
    from workflow_bridge.core.paths import get_data_dir
    from workflow_bridge.state import BridgeRuntime
    from workflow_bridge.ui.weixin_notify import WeixinNotifyController
    from workflow_bridge.ui.weixin_questions import QuestionChannelController
    from workflow_bridge.ui.workflow_assistant import WorkflowController
    from workflow_bridge.ui.bark_notify import BarkNotifyController
    from workflow_bridge.ui.phone_router import PhoneNotificationRouter
    from workflow_bridge.ui.shutdown import GracefulQuit, cancel_owned_threads, threads_busy

    class BridgeWindow(QMainWindow):
        def closeEvent(self, event):
            event.ignore()
            if self.tray.isVisible() and not self.runtime.closing:
                self.hide()
                if not self._hidden_tip_shown:
                    self.tray.showMessage("任务桥接仍在后台运行", "从托盘菜单选择“退出”可停止接收。")
                    self._hidden_tip_shown = True
            else:
                self.quit_coordinator.request()

    window = BridgeWindow()
    window._hidden_tip_shown = False
    window.setWindowTitle("任务桥接 · 微信与 AI 工作流")
    window.resize(950, 620)
    window.setWindowIcon(app.style().standardIcon(QStyle.SP_ComputerIcon))
    runtime = BridgeRuntime(app)
    window.runtime = runtime
    workflow = WorkflowController(runtime, parent=app)
    weixin = WeixinNotifyController(runtime, parent=app)
    bark = BarkNotifyController(runtime, parent=app)
    questions = QuestionChannelController(runtime, weixin, parent=app)
    router = PhoneNotificationRouter(weixin, bark)
    workflow.notification_ready.connect(router.enqueue)
    workflow.tracking_changed.connect(weixin.set_tracking)
    workflow.tracking_changed.connect(bark.set_tracking)
    workflow.tracking_changed.connect(questions.set_tracking)
    workflow.dialog.weixin.clicked.connect(weixin.open)
    workflow.dialog.bark.clicked.connect(bark.open)
    workflow.dialog.questions.clicked.connect(questions.open)
    for controller, label in ((weixin, workflow.dialog.weixin_status),
                              (bark, workflow.dialog.bark_status),
                              (questions, workflow.dialog.questions_status)):
        controller.status_changed.connect(label.setText)
        label.setText(controller.status_text)
    workflow.dialog.setWindowFlags(Qt.Widget)
    window.setCentralWidget(workflow.dialog)
    window.statusBar().showMessage("独立数据目录：" + str(get_data_dir()))
    toolbar = window.addToolBar("运行控制")
    pause = QAction("暂停 / 免打扰", window)
    pause.setCheckable(True)
    pause.toggled.connect(runtime.set_paused)
    toolbar.addAction(pause)
    exit_action = QAction("退出", window)
    toolbar.addAction(exit_action)
    help_action = QAction("使用说明", window)
    toolbar.addAction(help_action)
    def show_help():
        QMessageBox.information(window, "任务桥接",
            "1. 在“微信提醒”扫码并保存本人绑定。\n"
            "2. 给机器人发送一句话，然后在“微信问答”启用并保存。\n"
            "3. 执行者使用本程序的 --question、--event、--hook 接口。\n"
            "4. 微信发送“八位编号 A”或“回复 八位编号 你的回答”。\n\n"
            "请勿同时让桌宠使用同一个机器人接收消息。此工具不自动迁移桌宠账号、hooks 或队列。\n"
            "原生审批仍需在执行软件处理；等待进程已结束时不会自动唤醒。\n"
            "关闭窗口可进入后台；托盘“退出”会停止接收。完整说明见包内 README.md。")
    help_action.triggered.connect(show_help)
    tray = QSystemTrayIcon(window.windowIcon(), app)
    tray.setToolTip("任务桥接 · 微信提醒与问答")
    tray_menu = QMenu()
    def show_window():
        window.showNormal()
        window.raise_()
        window.activateWindow()
    tray_menu.addAction("打开任务面板", show_window)
    tray_menu.addAction("微信提醒设置", weixin.open)
    tray_menu.addAction("微信问答设置", questions.open)
    tray_menu.addAction("iPhone Bark 备用提醒", bark.open)
    tray_menu.addAction(pause)
    tray_menu.addSeparator()
    tray_menu.addAction(exit_action)
    tray.setContextMenu(tray_menu)
    tray.activated.connect(lambda reason: show_window() if reason == QSystemTrayIcon.DoubleClick else None)
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray.show()
    window.tray = tray
    runtime.notification.connect(lambda title, text: tray.showMessage(title, text) if tray.isVisible() else None)
    owners = (workflow, weixin, bark, questions)
    def prepare_exit():
        runtime.closing = True
        questions.shutdown()
        workflow.shutdown()
        router.shutdown()
        weixin.shutdown()
        bark.shutdown()
        for controller in owners:
            controller.dialog.hide()
        window.hide()
        cancel_owned_threads(owners)
    coordinator = GracefulQuit(app, prepare=prepare_exit,
        busy=lambda: threads_busy(owners), finalize_ui=tray.hide, cleanup=())
    window.quit_coordinator = coordinator
    exit_action.triggered.connect(coordinator.request)
    # Keep all Qt owners and plain routers alive for the full application run.
    window.controllers = owners
    window.router = router
    window.pause_action = pause
    window.tray_menu = tray_menu
    return window


def main(argv=None):
    parser = argparse.ArgumentParser(description="独立微信任务提醒与普通问答桥接")
    parser.add_argument("--data-dir", type=Path, help="独立数据目录，必须是本地绝对路径")
    parser.add_argument("--check", action="store_true", help="只检查独立依赖，不写数据或联网")
    parser.add_argument("--smoke-seconds", type=float, default=0, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.data_dir is not None:
        if not args.data_dir.is_absolute():
            parser.error("--data-dir 必须是绝对路径")
        os.environ["WORKFLOW_BRIDGE_HOME"] = str(args.data_dir)
    if args.check:
        result = dependency_check()
        print(json.dumps(result, ensure_ascii=False))
        return 0 if all(result.values()) else 1
    from PyQt5.QtCore import QLockFile, QTimer, Qt
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from workflow_bridge.core.paths import get_data_dir
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication([sys.argv[0]])
    app.setApplicationName("WorkflowBridge")
    app.setQuitOnLastWindowClosed(False)
    try:
        directory = get_data_dir()
        directory.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError):
        QMessageBox.critical(None, "任务桥接", "独立数据目录不可写或路径不安全，请用 --data-dir 指定本地绝对路径。")
        return 1
    instance_lock = QLockFile(str(directory / "bridge.lock"))
    if not instance_lock.tryLock(100):
        QMessageBox.information(None, "任务桥接", "这个数据目录已有实例运行，或上一实例仍在等待网络请求退出。")
        return 1
    window = create_host(app)
    window.show()
    if args.smoke_seconds > 0:
        QTimer.singleShot(int(min(args.smoke_seconds, 30) * 1000), window.quit_coordinator.request)
    try:
        return app.exec_()
    finally:
        instance_lock.unlock()
