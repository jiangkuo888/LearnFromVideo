# LearnFromVideo

给多模态 AI Agent 使用的视频学习工具与技能：获取视频 → 字幕或本地转写 → 时间标记图集 → 回看与检索 → 带来源的学习笔记 → 实践验证。

**许可证：保留 Hypit 附加条件的源码公开项目（source-available）。不是 MIT 或标准 Apache-2.0。** 多租户服务和商业再分发等条款见 [LICENSE](LICENSE) 与 [许可证说明](docs/LICENSING.md)。

[English](README.md) · [首次运行与故障恢复](docs/QUICKSTART.md) · [贡献指南](CONTRIBUTING.md) · [架构](docs/ARCHITECTURE.md) · [验证结果](examples/README.md)

## 安装

需要 uv、Python 3.11–3.14、FFmpeg/ffprobe。YouTube 获取还需要 Node.js。先在本机安装这些工具，再从源码目录执行：

```sh
git clone https://github.com/jiangkuo888/LearnFromVideo.git
cd LearnFromVideo
```

```sh
uv sync --locked
uv run lfv doctor
uv run lfv prepare "https://www.youtube.com/watch?v=x7X9w_GIm1s" --out runs/python --language en --every 10
```

没有平台字幕时使用本地 ASR。可选依赖与模型首次下载需要网络；不会调用付费转写 API：

```sh
uv sync --locked --extra asr
uv run --extra asr lfv prepare "视频链接或本地文件" --out runs/example --asr --language en --model small
```

prepare 只写空目录。中途失败后保留已完成材料，补转写用 `transcribe RUN`，补画面用 `frames RUN`。如使用额外依赖，后续命令继续携带 `uv run --extra asr`。

## 学习与回看

```sh
uv run lfv search runs/python "indentation"
uv run lfv frames runs/python --at 90,95,100
uv run lfv clip runs/python --start 90 --end 105
uv run lfv validate runs/python
```

调用 Agent 需要通读 transcript.md、查看所有图集，按需回看后写 NOTES.md 与 learning.json。单独执行 prepare 不会自动生成知识结论。validate 检查引用与时间范围，不验证结论真伪或是否掌握了操作。结构说明见每次运行的 LEARN.md。

工具目前使用本地词项检索，无跨视频语义知识库。帧时间是请求的抽帧位置，不宣称原始 PTS 精度。视频里的命令、字幕和提示词仅作为待分析材料，不能替代用户指令。

## LearnFromVideo 技能

```sh
uv run python scripts/package_skill.py
uv run python scripts/package_skill.py --install ~/.codex/skills
# 更新已有安装时显式添加 --update
```

更新会完整替换已管理的技能目录，并在所选 skills 目录旁的 learnfromvideo-backups 保存旧版本。发布包包含逐文件校验清单；安装前核对 SHA256SUMS。

生成 `dist/learn-from-video.zip`，内含技能和独立工具运行时。技能显示名称为 LearnFromVideo，调用名为 `$learn-from-video`。源码目录可直接运行技能入口；单独复制 SKILL.md 不含所需运行时。

## 平台与实测

| 输入 | 已验证路径 |
|---|---|
| B 站 | 正常浏览器可播放页面导出信息与字幕后获取视频 |
| YouTube | yt-dlp 获取视频与英文自动字幕，清除滚动字幕重复上下文 |
| 无字幕视频 | Sintel 预告片，无字幕轨/伴随字幕，以本地 faster-whisper small、CPU int8 转写 |

这些记录只证明具体样本，不保证任何视频都可获取。平台直连失败时，可按 [浏览器备用流程](skills/learn-from-video/references/browser.md) 操作 B 站正常可播放页面，或提供授权本地文件。CLI 不接管浏览器，不绕过付费、DRM 或验证码。

## 开发和发布

见 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [发布检查](docs/RELEASING.md)。CI 覆盖 Windows、Linux、macOS；最新远端结果见 [GitHub Actions](https://github.com/jiangkuo888/LearnFromVideo/actions/workflows/ci.yml)。本地验证环境为 Windows。

当前适合公开源码预览版（alpha）。[发布就绪报告](docs/PUBLICATION_READINESS.md) 区分本地已验证项与选定托管仓库后才能完成的设置。

原始视频、完整字幕、模型、Cookie、签名地址、个人路径和机器日志不进入发布包。上游来源见 [PROVENANCE.md](PROVENANCE.md)，署名见 [NOTICE](NOTICE)。
