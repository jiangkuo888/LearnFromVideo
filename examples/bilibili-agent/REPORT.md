# LearnFromVideo 真实视频验证

日期：2026-11-05，北京时间。历史验证版本：0.1.0。

输入：[BV1hfxp6HEs7](https://www.bilibili.com/video/BV1hfxp6HEs7/)，GilbertWuu《如果你对 Agent 一知半解，那看这条视频就对了！》。

## 已完成

- 独立 Git 项目与 Python CLI，迁移来源快照和 Hypit 原许可证。
- 普通直连遇到 HTTP 412；已有浏览器可正常播放，因此通过该页面当前可访问的播放信息与字幕获取证据。浏览器导出函数与 import-browser 命令亦已实际运行。
- 标准 HTTP Range 分段获取完整音视频，合并为 H.264/AAC MP4；ffprobe 检查到 1920×1080，时长 1101.926168 秒。
- 完整文件 SHA-256：`53fb20acba746b27584047445fd3d2332ea147da2f5ed35025f96ee8d45380fa`。
- 导入 524 段平台中文自动字幕，归一化并分块，保留原始字幕与识别误差。
- 通读完整字幕，实际审阅 37 张全片概览帧与 15 张补查帧，裁切 11:51–12:05 的回看片段；没有逐帧观看整个视频。
- 本地词项检索已返回原始片段和可跳转时间链接。
- 生成学习笔记、9 条有时间范围和画面引用的结论；证据结构校验通过。
- 应用视频中的先执行后封装、知识与来源分离、保存项目状态等方法。
- 全局安装显示名称为 LearnFromVideo 的 `learn-from-video` 技能。自带工具运行时已通过 doctor，并独立完成本地视频副本的 prepare，输出在 runs/skill-replay。

## 可复查位置

| 资料 | 路径 |
|---|---|
| 可阅读的学习成果 | examples/bilibili-agent/NOTES.md |
| 完整证据与学习结构 | runs/bilibili-agent-v2/ |
| 字幕与片段索引 | transcript.md、transcript.json、chunks.json（位于证据目录） |
| 概览与回看画面 | frames/、revisit/（位于证据目录） |
| 证据引用校验 | validation.json（位于证据目录） |
| 命令执行记录 | logs/verification.json |
| 当前项目状态 | docs/项目状态.md |
| 技能源文件 | skills/learn-from-video/SKILL.md |
| 安装后的技能入口 | <skills-directory>/learn-from-video/SKILL.md |

技能调用名：`$learn-from-video`。本次会话无法证明新会话的自然语言自动发现；该项保持待测。

## 验证范围

7 项功能测试覆盖 B 站/VTT 字幕读取、非法时间戳拒绝、HTTP 分段内容精确重组、目录越界引用拒绝、引用时间范围校验、实践状态与学习校验的区分、检索与来源时间链接。技能 frontmatter 与目录规范校验通过。

`validation.json` 的 passed 仅表示结构与引用有效。learning.json 的 practice=passed 仅指将方法应用于本项目并跑通当前学习流程，不代表已复现作者的其他案例。

## 尚未验证或实现

- YouTube 真实下载未实测；底层适配来自 yt-dlp。
- 可选 faster-whisper 路径已实现，本次使用平台字幕，未实际运行本地 ASR。
- 没有复现视频中的健康报告、日历写入、邮件发送或定时任务。
- 浏览器备用获取由调用 Agent 的浏览器工具执行，CLI 不自动接管浏览器。
- 没有跨视频语义知识库或独立无人值守问答服务；当前推理由调用工具的多模态 Agent 提供。

原始媒体、字幕全文和签名媒体地址保存在本地忽略目录，不包含在 Git 交付物中。学习笔记可以脱离媒体阅读，核验原始帧需保留本机 runs 目录。
