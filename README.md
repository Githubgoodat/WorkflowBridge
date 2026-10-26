# WorkflowBridge · 任务桥接

当前版本 **0.1.0**。发行包与源码见本仓库的 Releases；版本变化见 [CHANGELOG.md](CHANGELOG.md)。

一个独立的 Windows 任务提醒与微信问答工具，从 [NenePet-Desktop](https://github.com/Githubgoodat/NenePet-Desktop) 的工作流模块拆出。无需启动桌宠、Live2D、语音服务或大模型，也不需要 NVIDIA 显卡。

- 跟进 Codex 生命周期事件，以及 Grok Bot 主动上报的任务状态。
- 将项目名和任务状态发到本人微信；可选同一台 iPhone 的 Bark 作为状态提醒备用通道。
- 执行者主动创建普通问题，在微信回复 `八位编号 A` 或 `回复 八位编号 A`，由仍在等待的原执行者取回答案后继续。
- 支持暂停；恢复后不集中补发暂停期间的旧事件。

这是一套合作协议：它不会读取聊天数据库，不接管已有的原生问题卡或系统操作审批，也不会在原任务已结束后自动唤醒它。

## 三分钟开始（Windows 便携版）

解压整个文件夹，双击 `WorkflowBridge.exe`（也可用“启动任务桥接.cmd”）。不必安装 Python、桌宠、Live2D 或显卡环境；`_internal` 文件夹必须和程序放在一起。

`WorkflowBridge.exe` 是配置与后台接收窗口；`WorkflowBridge-CLI.exe` 是给 Codex、Grok 和 hooks 调用的入口，支持下文的 `--question`、`--event`、`--hook`、`--prepare-hooks`。不要把问答命令交给无控制台的 GUI 入口。

如果要替换目前桌宠中的微信接收，先关闭桌宠微信问答或退出桌宠，再扫码配置此程序。当前账号、hooks 和队列不会自动迁移。

## 源码运行

环境：Windows 10/11 64 位、Python 3.10 或更高版本，建议 Python 3.11–3.13。先在此文件夹打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

默认数据目录是程序文件夹下的 `data`。需要放到别处时，使用一个自己的绝对路径：

```powershell
.\.venv\Scripts\python.exe main.py --data-dir 'C:\WorkflowBridgeData'
```

1. 在主窗口打开“微信提醒”，扫码并用本人微信确认。给机器人发一句普通文字，建立本人通信上下文，再发送测试；请亲自核对手机聊天记录是否收到。
2. 要收到状态通知，启用并保存微信提醒。需要手机回答时，另在“微信问答”中启用本人问答；启用后会持续接收本人消息、自动更新通信上下文。
3. 将主窗口显示的**状态收件目录**交给 hook 或协作上报工具；将问答窗口显示的**问答收件目录**交给发问工具。两个目录不能混用。

手机通知需要电脑和本程序持续运行。电脑睡眠或程序退出后，本机不会继续转发。微信接口受理也不等于手机实际送达；服务返回不明确时，不自动重发同一消息。

## 从宁宁桌宠迁移

默认完全独立：不读取、不复制旧桌宠的账号、配置、问答记录、任务事件或素材，也不修改你已有的 Codex hooks。

**同一个微信机器人只能交给一个本地接收器。** 如要用原来的机器人，先在桌宠中关闭微信问答或退出桌宠，再在本工具中重新扫码配置。不要让两个程序同时轮询同一机器人，否则回答可能被另一个程序取走。

迁移后，需要把执行者使用的问答工具和 `--inbox` 改为本工具的新路径。状态观察器也应切换到新目录；已有其他 hooks 保留，仅审阅并更新对应桥接项。不要把新程序直接指向旧桌宠的活动数据目录。

本机绑定使用当前 Windows 用户的 DPAPI 加密，复制数据文件到朋友电脑不能完成账号迁移；朋友应自行扫码。分享时不带 `data`、账号、设备密钥或真实问答记录。

## 给 Codex / Grok 的接入说明

任务开头可以这样要求执行者：

> 本轮需要我选择或澄清时，请阅读 WorkflowBridge 的 `docs/WEIXIN_QUESTIONS.md`，主动使用它的普通微信问答通道。只有原执行进程仍在等待且拿到 `answered` 时才继续；超时或通道不可用要如实报告，不自动替我选择。保持现有操作审批规则。

完整接入步骤、状态事件含义和安全的 Codex hook 生成命令见 [任务跟进](docs/WORKFLOW.md)。普通问题的创建、等待、领取和取消见 [微信问答](docs/WEIXIN_QUESTIONS.md)。

| 工具 | 用途 | 收件目录 |
| --- | --- | --- |
| `tools/workflow_hook.py` | Codex 元数据观察器，输出空 JSON，不作审批决定 | 主窗口的状态目录 |
| `tools/workflow_event.py` | Grok 显式协作上报 | 主窗口的状态目录 |
| `tools/workflow_question.py` | 新建普通问题、等待/领取/取消答案 | 问答窗口的专用目录 |
| `tools/prepare_codex_hooks.py` | 生成新文件供审阅，不安装、不信任、不覆盖已有配置 | 显式指定 |

`Stop` 只代表本轮结束，`phase-ended` 只代表执行者自报阶段结束；均不能证明整个项目完成或测试通过。超过十分钟无事件只显示状态过期，不会推断失败。

## 手机回答与服务边界

例如收到编号 `A1B2C3D4`，可回复 `A1B2C3D4 B`；不要只发 `B`，因为可能有多个项目同时等待。问题有效期为 60–900 秒，默认 10 分钟；原调用者必须保留等待进程或明确保存待答 checkpoint。答案属于普通输入，不会执行文本、批准命令或登录账号。

Bark 只发送项目名、来源和状态，不能接收回答，也不会自动接手正文问答。微信明确失败或停用时，可将后续状态提醒交给启用的 Bark；发送结果未知时不双发。具体限制与排查见 [常见问题](docs/TROUBLESHOOTING.md)。

## 测试与许可

测试使用生成或模拟的数据，不访问真实微信、Bark、聊天或绑定：

```powershell
python tests/run_offline.py
```

测试入口会使用独立临时数据目录，并以审计钩子拒绝真实网络和子进程。Windows、Python 3.13 的 [CI 配置示例](ci/offline.workflow.yml) 使用同一入口，依赖安装发生在审计之前；本版本只提供示例，仓库尚未启用 GitHub Actions。本地 357 项通过不代表手机已实测送达。Windows 二进制的构建方式见 [打包说明](packaging/README.md)。

源代码采用 [AGPL-3.0](LICENSE)。提取来源、上游项目与第三方协议致谢见 [CREDITS.md](CREDITS.md)。此独立包不包含人物模型、美术、语音或游戏素材。
