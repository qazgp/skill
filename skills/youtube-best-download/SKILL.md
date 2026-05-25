---
name: youtube-best-download
description: Download YouTube and Bilibili videos from youtube.com/youtu.be/bilibili.com/b23.tv links using yt-dlp. Trigger when the user shares a YouTube or Bilibili URL or asks to download/save online videos to phone storage. YouTube defaults to highest quality first while preferring MP4/M4A; Bilibili defaults to the best available H.264/AVC stream for compatibility; supports explicit codec preferences such as H.264/H.265/AV1; uses cookies for restricted/high-quality videos if available; copies output to mounted phone folder under /var/minis/mounts and deletes the Minis workspace copy by default.
version: 1.3.0
---
# Video Best Download

Use this skill whenever the user shares a YouTube or Bilibili link and wants it downloaded/saved.

## Policy / preference

- Default strategy:
  - **YouTube**: highest quality first, prefer MP4/M4A, but do not force MP4 at the cost of quality.
  - **Bilibili**: default to the **best available H.264 / AVC** stream for compatibility unless the user specifies another codec.
- YouTube default format selector:
  ```bash
  -f "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best"
  ```
- Bilibili default format selector:
  ```bash
  -f "bv*[vcodec^=avc1]+ba/best[vcodec^=avc1]/best"
  ```
- Explicit codec modes are supported when the user asks for compatibility or a specific encoding:
  ```bash
  --codec h264   # best available H.264 / AVC stream
  --codec h265   # best available H.265 / HEVC stream
  --codec av1    # best available AV1 stream
  ```
- H.264 format selector:
  ```bash
  -f "bv*[vcodec^=avc1]+ba/best[vcodec^=avc1]/best"
  ```
- Add `--merge-output-format mp4` so compatible streams become MP4. If the true best streams require another container, accept `.webm`/`.mkv` rather than lowering quality.
- Use cookies when present:
  - YouTube default: `/var/minis/attachments/uploads/shared-c02eab22.txt`
  - Bilibili default: `/var/minis/attachments/uploads/shared-5a43b52b.txt`
- For Bilibili, valid login cookies unlock 720P/1080P/4K/60fps when the account has access. Required key cookies usually include `SESSDATA`, `bili_jct`, `DedeUserID`, `buvid3`.
- After download, copy the file to the user's mounted phone folder under `/var/minis/mounts/`.
- Unless the user asks to keep both copies, delete the Minis workspace copy after successful phone copy to save space.

## Fast Path

Run the same script for YouTube or Bilibili URLs:

```bash
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py 'VIDEO_URL'
```

The script will:
1. Detect platform from the URL: YouTube, Bilibili, or generic.
2. Ensure `yt-dlp` and `ffmpeg` exist.
3. For YouTube, ensure Node exists and use yt-dlp EJS solver:
   `--js-runtimes node --remote-components ejs:github`
4. Use the platform's default cookies file if it exists.
5. Download into `/var/minis/workspace/video_downloads/<platform>/`.
6. Copy to the first mounted folder under `/var/minis/mounts/`.
7. Delete the workspace output by default.

Useful options:

```bash
# Keep Minis workspace copy too
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --keep-workspace

# Download only, do not copy to phone
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --no-copy

# Download the best H.264 version for compatibility (Bilibili default)
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --codec h264

# Download the best H.265/HEVC or AV1 version
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --codec h265
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --codec av1

# Specify a mounted folder name/path
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --mount minis
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --mount /var/minis/mounts/minis

# Override cookies
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --cookies /path/to/cookies.txt
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --bili-cookies /path/to/bilibili-cookies.txt
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py URL --youtube-cookies /path/to/youtube-cookies.txt
```

## If no mount exists

Tell the user to mount a phone folder:
[挂载外部文件夹](minis://settings/mount-external)

Then rerun the script or manually copy from workspace to `/var/minis/mounts/<name>/`.

## Manual Fallback

YouTube default:

```bash
yt-dlp --cookies /path/to/youtube-cookies.txt \
  --js-runtimes node --remote-components ejs:github \
  --no-playlist \
  -f 'bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best' \
  --merge-output-format mp4 \
  -o '/var/minis/workspace/video_downloads/youtube/%(title).120s [%(id)s].%(ext)s' \
  'YOUTUBE_URL'
```

Bilibili default H.264 compatibility mode:

```bash
yt-dlp --cookies /path/to/bilibili-cookies.txt \
  --no-playlist \
  --socket-timeout 30 --retries 5 --fragment-retries 5 \
  -f 'bv*[vcodec^=avc1]+ba/best[vcodec^=avc1]/best' \
  --merge-output-format mp4 \
  -o '/var/minis/workspace/video_downloads/bilibili/%(title).120s [%(id)s].%(ext)s' \
  'BILIBILI_OR_B23_URL'
```

Bilibili/YouTube H.264 compatibility mode:

```bash
yt-dlp --cookies /path/to/cookies.txt \
  --no-playlist \
  --socket-timeout 30 --retries 5 --fragment-retries 5 \
  -f 'bv*[vcodec^=avc1]+ba/best[vcodec^=avc1]/best' \
  --merge-output-format mp4 \
  -o '/var/minis/workspace/video_downloads/%(title).120s [%(id)s].%(ext)s' \
  'VIDEO_URL'
```

Then copy the result to `/var/minis/mounts/<mounted-folder>/` and remove the workspace copy unless the user wants both.
