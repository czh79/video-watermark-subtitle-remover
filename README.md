# 🧼 视频硬字幕 / 水印清除器

> 一条命令，把视频里烧进画面的字幕、台标、水印全部裁掉，再拉回 1080p 满屏。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-orange?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**中文** | [English](#-english)

---

## 为什么"裁切"是最实际的方案

去硬字幕这件事，理论上有三条路：

| 方案 | 效果 | 代价 |
|---|---|---|
| AI 修补（inpainting） | 理论上完美 | 极慢、画面抖动、需要逐帧对齐，工程上基本不可用 |
| 模糊 / 马赛克 | 字幕变一团糊 | 观感更差，一眼看出处理过 |
| **几何裁切** | 字幕彻底消失 | 损失少量画面边缘 |

**本项目走第三条路**，因为对绝大多数横屏内容（教程、影视、访谈）来说，字幕永远在固定区域，裁掉边缘 6%+17.5% 的画面几乎不影响主体，而且**没有任何 AI 伪影**。

裁完后画面比 16:9 更宽，再用 Lanczos 插值放大到 1920×1080 并居中补黑边，输出依然满屏。

## 核心能力

| 能力 | 说明 |
|---|---|
| **链接直接处理** | 粘贴 URL，yt-dlp 自动下载最佳 mp4 流（视频+音频合并） |
| **本地批量处理** | 扫描脚本同目录下所有视频，一次性全部清洗 |
| **精确裁切** | 顶部 6%（台标/网页标题栏）、底部 17.5%（双语硬字幕）、左右各 2% |
| **Lanczos 重构** | 高阶插值放大回 1920×1080，`force_original_aspect_ratio=decrease` + 居中补边，不拉伸变形 |
| **音轨原样保留** | `-c:a copy`，音频零转码零损失 |
| **高质量导出** | libx264 CRF 18 / preset medium |

## 裁切比例怎么调

四个常量在文件开头，按你的片源改：

```python
CROP_TOP_RATIO    = 0.06     # 顶部 6%  → 台标、标题栏
CROP_BOTTOM_RATIO = 0.175    # 底部 17.5% → 单行/双语字幕
CROP_LEFT_RATIO   = 0.02
CROP_RIGHT_RATIO  = 0.02
```

> 双语字幕（中英各一行）通常需要 0.17–0.20；单行字幕 0.10 就够。宁可先设保守值跑一个 30 秒片段试效果。

## 快速开始

```bash
git clone https://github.com/czh79/video-watermark-subtitle-remover.git
cd video-watermark-subtitle-remover
pip install -r requirements.txt
python clean.py
```

菜单：

```
1. 🌐 链接下载并清除   → 粘贴 URL，下载完直接清洗
2. 📂 同目录批量清除   → 处理当前目录下所有本地视频
```

输出在 `output_clean/clean_<原名>.mp4`。

## 已知限制

- **抖音 / TikTok 反爬**：yt-dlp 可能拿不到流。建议浏览器里另存到本地，再用模式 2 处理。
- **竖屏视频**：底部 17.5% 对竖屏来说太大，请改成 0.08 左右。
- **画面边缘有内容**：裁切是"一刀切"，如果主体贴边会被切到——这种片源不适合本项目。

---

## 🇬🇧 English

> Crop burned-in subtitles, logos, and watermarks out of a video and scale it back to a full-frame 1080p.

There are three ways to remove hard subtitles: AI inpainting (slow, flickers, rarely production-ready), blurring (looks worse than the subtitle), and **geometric cropping**. This project takes the third path — for typical 16:9 content the subtitle always occupies a fixed band, so cropping 6% top and 17.5% bottom removes it with zero artifacts on the rest of the frame.

The cropped frame is then Lanczos-upscaled to 1920×1080 with aspect-ratio preservation and letterboxing, so output stays full-frame without stretching.

### Features

- Paste a URL → yt-dlp fetches the best merged mp4 and cleans it in one go.
- Or batch-process every video sitting next to the script.
- Audio is stream-copied (`-c:a copy`) — no re-encode, no quality loss.
- Video exported at libx264 CRF 18.

### Usage

```bash
pip install -r requirements.txt
python clean.py
```

Output: `output_clean/clean_<name>.mp4`.

Tune `CROP_TOP_RATIO` / `CROP_BOTTOM_RATIO` at the top of the file for your source. Vertical video needs a much smaller bottom crop (~0.08).

### Limitations

Crop is all-or-nothing — if your subject sits against the bottom edge it will get clipped. Douyin/TikTok links are often blocked by anti-bot measures; download locally and use batch mode instead.

---

<div align="center">

有用就 **点个 Star** ⭐

</div>
