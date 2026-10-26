# Windows 构建

在 Windows x64、Python 3.13 中创建一个干净的虚拟环境，避免把机器上的桌宠环境或模型包混入产物：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
.\.venv\Scripts\python.exe tests/run_offline.py
.\.venv\Scripts\python.exe -m PyInstaller --distpath dist --workpath build packaging/WorkflowBridge.spec
```

`dist/WorkflowBridge` 包含两个入口及共享的 `_internal` 目录：

- `WorkflowBridge.exe`：窗口、托盘和后台接收。
- `WorkflowBridge-CLI.exe`：标准输入/输出入口，供任务和 hooks 调用。

`WorkflowBridge.spec` 显式包含动态加载的四个工具模块与 qrcode，并排除桌宠、模型与科学计算模块。只有打包器及构建依赖需要在构建时安装；便携版用户无需 Python。

构建之后应在全新目录测试 `WorkflowBridge-CLI.exe --check` 和空配置 GUI 启动/正常退出。离线夹具或界面检查不能替代本人微信/Bark 的真实送达验收。

发布时保留完整 `_internal` 文件夹；随附本版本源码、README、CHANGELOG、CREDITS、AGPL LICENSE、`licenses` 及实际二进制所包含依赖的版权和许可。不得加入运行后的 `data`、微信绑定、Bark 密钥或真实问答/任务记录。创建 ZIP 后检查目录清单与 SHA-256。

官方打包器用法：[PyInstaller 使用说明](https://pyinstaller.org/en/stable/usage.html)、[spec 文件](https://pyinstaller.org/en/stable/spec-files.html)。
