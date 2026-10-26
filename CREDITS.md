# 来源与致谢

## 提取来源与代码许可

WorkflowBridge 从 **[Githubgoodat/NenePet-Desktop](https://github.com/Githubgoodat/NenePet-Desktop)** 的工作流通知与微信问答模块拆分，提取基线为提交 [`bfebd57`](https://github.com/Githubgoodat/NenePet-Desktop/commit/bfebd57)。保留经过验证的事件格式、问答绑定、去重、有限等待和手机适配器；本次改造将它们与人物、桌宠窗口、Live2D、对话模型及语音服务分离。

NenePet-Desktop 的直接代码上游与灵感来源是 **[kuxiaowo/AIpet-Murasame](https://github.com/kuxiaowo/AIpet-Murasame)**，上游基线为 [`74599a3def49cf0d57a29f511dae8d063d695612`](https://github.com/kuxiaowo/AIpet-Murasame/tree/74599a3def49cf0d57a29f511dae8d063d695612)。更早项目 **[LemonQu-GIT/MurasamePet](https://github.com/LemonQu-GIT/MurasamePet)** 亦由上游列入致谢。感谢原项目与贡献者的工作。

本拆分项目继续采用 [GNU Affero General Public License v3.0](LICENSE)。已有版权、许可与来源说明保留；提供本工具网络服务或分发修改版本时，应依许可证履行相应源码义务。

## 微信协议

微信纯文本适配器参考腾讯开源 **[Tencent/openclaw-weixin](https://github.com/Tencent/openclaw-weixin)** 的协议与请求实现；腾讯 MIT 许可保留于 [licenses/weixin/LICENSE-Tencent-MIT.txt](licenses/weixin/LICENSE-Tencent-MIT.txt)。它不是腾讯提供的独立 SDK，不包含 OpenClaw，也不是 DeepSeek 官方微信 skill。

## Bark 协议与依赖

Bark 状态备用适配器依据 **[Finb/Bark](https://github.com/Finb/Bark)** 的公开推送 API 和 **[Finb/bark-server](https://github.com/Finb/bark-server)** 的响应约定独立实现；没有附带手机客户端或服务器代码。

源码运行依赖 PyQt5、Requests 和 qrcode；这些依赖适用各自许可证。它们不因本项目的许可证而改为本项目原创内容。打包发行二进制版本时，应随所包含的实际依赖版本一并保留其版权和许可证。

本独立包没有分发任何 Live2D、人物、字体、游戏原图或录音素材；原桌宠中的模型署名与素材权利不因拆分而转移。项目也不宣称 Codex、Grok、腾讯或 Bark 官方背书。
