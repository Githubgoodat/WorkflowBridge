# 离线 CI 配置示例

`offline.workflow.yml` 是供仓库维护者审阅的 Windows、Python 3.13 测试配置；当前仓库未启用自动 CI，文件在此目录不会触发 GitHub Actions。

如维护者以后决定启用，可审阅后将它复制到 `.github/workflows/offline.yml`，再按仓库权限和 GitHub 的工作流要求发布。它先安装 `requirements.txt`，随后调用 `python tests/run_offline.py`；测试入口会隔离本地数据并阻止真实网络和子进程。

配置示例没有微信、Bark 或其他账号凭据，不要求仓库 Secrets。CI 的通过也不能代替真人手机送达验收。
