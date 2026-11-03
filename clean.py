import os
import sys
import shutil
import subprocess
from pathlib import Path

# ==================== 核心路径与配置 (完全对齐原附件) ====================
BASE_DIR = Path(__file__).resolve().parent
WORK_DIR = BASE_DIR / "workspace_clean"
OUTPUT_DIR = BASE_DIR / "output_clean"

OUT_WIDTH = 1920
OUT_HEIGHT = 1080
OUT_FPS = 30

# 原视频边缘裁剪比例 (原附件核心参数：顶部切 6%，底部切 17.5% 彻底去除所有硬字幕与水印)
CROP_TOP_RATIO = 0.06
CROP_BOTTOM_RATIO = 0.175
CROP_LEFT_RATIO = 0.02
CROP_RIGHT_RATIO = 0.02
# =======================================================================


def run_cmd(cmd: list, desc: str = "") -> subprocess.CompletedProcess:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    if res.returncode != 0 and desc:
        print(f"  ⚠️ [{desc}] 执行异常:\n{res.stderr[-300:]}")
    return res


def get_media_duration(media_file: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(media_file.resolve())
    ]
    res = run_cmd(cmd)
    try:
        return float(res.stdout.strip()) if res.returncode == 0 and res.stdout.strip() else 0.0
    except ValueError:
        return 0.0


# ==================== 功能 1: 按照粘贴链接下载 ====================
def download_source_video(url_or_path: str, work_dir: Path) -> Path:
    """
    完全对齐原附件下载逻辑：
    1. 若传入的是本地路径或已存在文件，直接复用。
    2. 若是网络链接，自动调用 yt-dlp 合并下载最佳 mp4 视频流。
    """
    local_p = Path(url_or_path)
    if local_p.exists() and local_p.is_file():
        print(f"📂 检测到本地源视频文件: {local_p.name}")
        return local_p

    output_tmpl = str((work_dir / "download_raw.%(ext)s").resolve())
    final_mp4 = work_dir / "download_raw.mp4"

    if final_mp4.exists():
        final_mp4.unlink()

    print(f"🌐 正在通过 yt-dlp 下载链接视频: {url_or_path} ...")
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", output_tmpl,
        url_or_path
    ]
    res = run_cmd(cmd, "yt-dlp 下载")
    if res.returncode != 0 or not final_mp4.exists():
        raise RuntimeError(f"yt-dlp 视频下载失败。\n提示：若为抖音等反爬风控平台，建议直接复制链接在浏览器保存到当前目录执行，或检查网络环境。")

    print(f"✅ 视频下载完成: {final_mp4.name} (时长: {get_media_duration(final_mp4):.2f}s)")
    return final_mp4


# ==================== 功能 2: 去除所有字幕/水印并高清化 ====================
def clean_watermark_and_subtitles(input_path: Path, output_path: Path):
    """
    直接继承附件第 340-362 行的视觉重构与硬字幕消除滤镜：
    1. crop 裁切掉原片顶部 6%（台标/网页标题栏）及底部 17.5%（彻底清除全部中文/双语硬字幕）。
    2. lanczos 高阶算法放大插值重构。
    3. 保留原始音轨，高质量导出。
    """
    print(f"\n✂️ 正在清除字幕与水印 (裁剪顶部 {int(CROP_TOP_RATIO*100)}% + 底部 {int(CROP_BOTTOM_RATIO*100)}%): {input_path.name}")

    filter_complex = (
        f"[0:v]crop=iw*(1-{CROP_LEFT_RATIO}-{CROP_RIGHT_RATIO}):"
        f"ih*(1-{CROP_TOP_RATIO}-{CROP_BOTTOM_RATIO}):"
        f"iw*{CROP_LEFT_RATIO}:ih*{CROP_TOP_RATIO},"
        f"scale={OUT_WIDTH}:{OUT_HEIGHT}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={OUT_WIDTH}:{OUT_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"fps={OUT_FPS}[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path.resolve()),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",
        "-c:a", "copy",
        str(output_path.resolve())
    ]

    res = run_cmd(cmd, f"去字幕与水印处理 [{input_path.name}]")
    if res.returncode == 0 and output_path.exists():
        print(f"🎉 处理完成！已输出无字幕/无水印成片: {output_path.resolve()}")
    else:
        print(f"❌ 视频处理失败: {input_path.name}")


# ==================== 主流程控制 ====================
def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("      🎬 视频下载与字幕/水印纯净清除工具 (原版算法内核)")
    print("=" * 65)
    print(" 1. 🌐 [链接下载并清除] 输入视频链接，自动下载并切除硬字幕与水印")
    print(" 2. 📂 [同目录批量清除] 仅处理脚本当前目录下的所有本地视频文件")
    print(" 0. 退出程序")
    print("=" * 65)

    choice = input("请输入选项 (0-2): ").strip()

    if choice == "1":
        user_url = input("\n请粘贴视频链接: ").strip().strip('"')
        if not user_url:
            print("❌ 链接不能为空！")
            return

        try:
            downloaded_video = download_source_video(user_url, WORK_DIR)
            out_file = OUTPUT_DIR / f"clean_{downloaded_video.stem}.mp4"
            clean_watermark_and_subtitles(downloaded_video, out_file)
            if downloaded_video.exists() and downloaded_video.parent == WORK_DIR:
                downloaded_video.unlink()
        except Exception as e:
            print(f"❌ 执行失败: {e}")

    elif choice == "2":
        # 仅扫描同级目录下的本地视频文件，忽略已导出的成品
        video_exts = {".mp4", ".mov", ".mkv", ".flv", ".avi"}
        local_videos = [
            f for f in BASE_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in video_exts and not f.name.startswith("clean_")
        ]

        if not local_videos:
            print(f"\n⚠️ 未在同级目录 {BASE_DIR} 下检测到可处理的视频文件！")
            return

        print(f"\n📂 扫描到 {len(local_videos)} 个本地视频文件，开始批量清除字幕与水印：")
        for idx, vid in enumerate(local_videos, 1):
            print(f"\n[{idx}/{len(local_videos)}] 正在处理: {vid.name}")
            out_file = OUTPUT_DIR / f"clean_{vid.stem}.mp4"
            clean_watermark_and_subtitles(vid, out_file)

        print(f"\n🎉 同目录下所有视频已全部处理完成，输出目录: {OUTPUT_DIR.resolve()}")

    elif choice == "0":
        sys.exit(0)
    else:
        print("⚠️ 输入无效，程序退出。")


if __name__ == "__main__":
    main()