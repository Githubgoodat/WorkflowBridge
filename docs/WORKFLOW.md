# 任务状态接入

主窗口只读取明确指定目录中的自有任务元数据，不读取 Codex/Grok 的聊天数据库、登录配置或 transcript，不调用对话模型。需要正文问答时，另见 [微信问答](WEIXIN_QUESTIONS.md)。

默认数据目录下有两条独立队列：

- `cache/workflow-inbox`：状态快照与独立的提问事件元数据，由主窗口跟进。
- `cache/workflow-questions`：执行者主动创建的问题及本人回答，由微信问答窗口管理。

采用 `--data-dir` 时，以窗口实际显示的路径为准，不把两个收件目录混用。

## Codex 状态观察器

本工具保留的 hook 事件有 `UserPromptSubmit`、`PreToolUse`、`PermissionRequest`、`Stop`、`Interrupt`、`SessionEnd`。Codex 版本须支持这些配置并信任准确的观察项，参见 [官方 hooks 说明](https://learn.chatgpt.com/docs/hooks)。实际覆盖范围仍应在所用桌面或 CLI 版本上逐项验收。

从源码目录生成一份新审阅文件，替换下列示例路径：

```powershell
.\.venv\Scripts\python.exe tools/prepare_codex_hooks.py `
  --inbox 'C:\WorkflowBridge\data\cache\workflow-inbox' `
  --output '.\codex-hooks.workflow-bridge.generated.json'
```

生成器使用当前 Python 和观察脚本的绝对路径。它只创建新文件，不覆盖、不安装、不信任，也不会读取真实 Codex 配置。Windows 命令使用 PowerShell 的 `&` 和单引号；如果所选执行 shell 不同，应按那个 shell 的语法改造并实测。移动源码或 Python 环境后要重新生成。

独立发行包应使用带控制台和 JSON 输出的 `WorkflowBridge-CLI.exe`，而非 GUI 启动器：

```powershell
& 'C:\WorkflowBridge\WorkflowBridge-CLI.exe' --prepare-hooks `
  --standalone-exe 'C:\WorkflowBridge\WorkflowBridge-CLI.exe' `
  --inbox 'C:\WorkflowBridgeData\cache\workflow-inbox' `
  --output '.\codex-hooks.workflow-bridge.exe.generated.json'
```

生成命令会直接运行 `WorkflowBridge-CLI.exe --hook --inbox ...`。请亲自审阅，再合并到自己使用的 Codex hook 配置中。已有其他工具的 hooks 必须保留，各事件的数组追加本观察器，不能整份覆盖。随后在支持的 Codex CLI 中打开 `/hooks`，审阅并信任准确命令；命令改动后须重新审阅。不要通过绕过信任检查来安装。

进行一次普通交互，再核对主窗口是否出现对应项目、事件和时间。“文件已生成”或“已信任”均不等于事件已经抵达。

观察器读取最多 64 KiB 的标准输入，只输出 `{}`，无法写入也不阻断 Codex；不提供批准、拒绝或继续执行的决定。输入中的问题、答案、工具参数、工具输出和 transcript 路径不会进入状态文件。

## Grok 显式协作上报

Grok 必须在本机有权运行命令。云端智能体不能直接写入你的 Windows 文件夹，也不能因需要通知而放宽原有审批。

让它在你交给它的任务中主动调用工具，例如：

```powershell
.\.venv\Scripts\python.exe tools/workflow_event.py `
  --inbox 'C:\WorkflowBridge\data\cache\workflow-inbox' `
  --task-id sample-task --phase-id phase-1 --project '示例项目' --event running

.\.venv\Scripts\python.exe tools/workflow_event.py `
  --inbox 'C:\WorkflowBridge\data\cache\workflow-inbox' `
  --task-id sample-task --phase-id phase-1 --project '示例项目' --event phase-ended
```

EXE 版使用 `WorkflowBridge-CLI.exe --event` 加相同参数，不再传入 `.py` 路径。

`--event` 支持 `running`、`needs-input`、`phase-ended`、`interrupted`、`failed`。一个任务沿用独立稳定的 task-id，每个新阶段换 phase-id。project 只填简短项目名，不在编号中放正文、路径或凭据。

输出 `{"accepted":true}` 只代表本机写入，不代表手机收到、阶段实际成功或项目完成。Bot 忘记上报、失去权限或异常退出时会缺少事件；这是一套协作约定，不是其原生状态订阅。

## 状态怎样解释

| 观察到的事件 | 可作的判断 |
| --- | --- |
| UserPromptSubmit / PreToolUse | 观察到任务有新活动 |
| PermissionRequest | 曾记录到授权请求，仍需回 Codex 确认实际情况 |
| Stop | 本轮结束待查看，不代表全部工作或测试完成 |
| Interrupt / SessionEnd | 本轮中断或会话结束，不代表成功 |
| GrokNeedsInput | Grok 自报需要输入 |
| GrokPhaseEnded | Grok 自报本阶段结束 |

提问事件元数据从 `PreToolUse` 的准确工具名识别同步 `request_user_input` 和异步 `request_user_input_async`（含 `functions.` 前缀）。异步提问不代表任务暂停；工具调用前的观察也不能证明问题已成功显示。纯文本回答中提出的问题无法仅凭元数据识别。

Codex 的授权提醒保留 30 秒观察期，另有约 3 秒扫描间隔。同轮次出现不早于授权的明确提问时，可合成一条提醒并保留“也记录到授权请求”的事实；不同问题和迟到的独立事件仍可能分别通知。普通运行状态不能证明审批已处理，不能据此取消提醒或批准操作。

同来源、任务、轮次和结束状态的重复上报去重；新阶段仍可通知。元数据扫描、有限队列、上游覆盖或缺少 hook 都可能丢失事件；面板不是任务验收依据。

启动和恢复时已有状态仅作基线，不补播旧通知。暂停停止扫描与新提示，丢弃尚未发出的候选；恢复建立新基线。超过十分钟无新状态只显示过期，不把沉默判断为失败。关闭程序后转发停止。

## 微信与 Bark

微信状态提醒要由本人扫码、发普通消息建立通信上下文、发送测试并启用保存。主窗口显示项目名和固定状态模板，不需要大模型。项目名会经过服务商，请为保密项目使用合适的短标签。

微信问答是另一项显式启用的通道，临时处理问题与回答正文；状态观察器不因此开始读取正文。

Bark 是可选的 iPhone 状态备用通道。仅支持官方 `api.day.app` 设备密钥或设备地址，密钥只填本机设置。微信停用或明确拒绝时，由启用的 Bark 接手状态；微信结果不明时不双发。Bark 不接收回答，也不自动发送问答正文。

没有渠道能够仅凭接口返回保证手机及时显示。微信上下文、网络、手机通知权限和服务可用性都影响送达；不要把 `ready`、尝试发送、接口受理或本机写入当作手机回执。故障排查见 [常见问题](TROUBLESHOOTING.md)。
