#!/usr/bin/env python3
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

BASE_WORKDIR = Path('/var/minis/workspace/video_downloads')
DEFAULT_YOUTUBE_COOKIES = Path('/var/minis/attachments/uploads/shared-c02eab22.txt')
DEFAULT_BILI_COOKIES = Path('/var/minis/attachments/uploads/shared-5a43b52b.txt')
MOUNTS = Path('/var/minis/mounts')
YOUTUBE_FORMAT = 'bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best'
BILI_FORMAT = 'bv*+ba/best'
H264_FORMAT = 'bv*[vcodec^=avc1]+ba/best[vcodec^=avc1]/best'
H265_FORMAT = 'bv*[vcodec^=hev1]+ba/best[vcodec^=hev1]/best'
AV1_FORMAT = 'bv*[vcodec^=av01]+ba/best[vcodec^=av01]/best'
MEDIA_EXTS = {'.mp4', '.mkv', '.webm', '.m4a', '.mp3'}


def run(cmd, check=True):
    print('+ ' + ' '.join(str(x) for x in cmd), flush=True)
    p = subprocess.run(cmd, text=True)
    if check and p.returncode != 0:
        sys.exit(p.returncode)
    return p.returncode


def ensure_tool(name, apk=None):
    if shutil.which(name):
        return
    if apk:
        run(['apk', 'add', apk])
    if not shutil.which(name):
        print(f'ERROR: missing tool {name}', file=sys.stderr)
        sys.exit(127)


def detect_platform(url):
    host = urlparse(url).netloc.lower()
    if 'youtu.be' in host or 'youtube.com' in host:
        return 'youtube'
    if 'b23.tv' in host or 'bilibili.com' in host:
        return 'bilibili'
    return 'generic'


def first_mount():
    if not MOUNTS.exists():
        return None
    dirs = [p for p in MOUNTS.iterdir() if p.is_dir()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.name)[0]


def latest_media(workdir, before):
    after = set(workdir.glob('*'))
    new_files = sorted([p for p in after - before if p.is_file()], key=lambda p: p.stat().st_mtime)
    if new_files:
        return new_files[-1]
    files = [p for p in workdir.iterdir() if p.is_file() and p.suffix.lower() in MEDIA_EXTS]
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime)[-1]


def codec_suffix(codec, platform=None):
    effective = codec
    if codec == 'auto' and platform == 'bilibili':
        effective = 'h264'
    return {'h264': '-H264', 'h265': '-H265', 'hevc': '-H265', 'av1': '-AV1'}.get(effective, '')


def copy_and_cleanup(output, args, workdir):
    print(f'WORKSPACE_FILE={output}')
    print(f'SIZE={output.stat().st_size}')

    if args.no_copy:
        return

    if args.mount:
        dest_dir = Path(args.mount)
        if not dest_dir.is_absolute():
            dest_dir = MOUNTS / args.mount
    else:
        dest_dir = first_mount()

    if not dest_dir or not dest_dir.exists():
        print('NO_MOUNT_FOUND: file kept in workspace. Mount a phone folder in Settings -> Mount External Folders.', file=sys.stderr)
        return

    safe_name = output.name
    safe_name = re.sub(r' \[[A-Za-z0-9_-]{10,14}(?:_p\d+)?\](?=\.[^.]+$)', '', safe_name)
    suffix = codec_suffix(args.codec, args.platform)
    if suffix and not safe_name.lower().removesuffix(output.suffix.lower()).lower().endswith(suffix.lower()):
        safe_name = safe_name[:-len(output.suffix)] + suffix + output.suffix
    dest = dest_dir / safe_name
    shutil.copy2(output, dest)
    print(f'PHONE_FILE={dest}')
    print(f'PHONE_SIZE={dest.stat().st_size}')

    if not args.keep_workspace:
        output.unlink()
        try:
            workdir.rmdir()
        except OSError:
            pass
        try:
            BASE_WORKDIR.rmdir()
        except OSError:
            pass
        print('WORKSPACE_DELETED=1')


def choose_format(platform, codec):
    if codec == 'h264':
        return H264_FORMAT
    if codec in {'h265', 'hevc'}:
        return H265_FORMAT
    if codec == 'av1':
        return AV1_FORMAT
    if platform == 'youtube':
        return YOUTUBE_FORMAT
    if platform == 'bilibili':
        return H264_FORMAT
    return 'bv*+ba/best'


def main():
    ap = argparse.ArgumentParser(description='Download YouTube/Bilibili at best quality and copy to mounted phone folder.')
    ap.add_argument('url')
    ap.add_argument('--codec', choices=['auto', 'h264', 'h265', 'hevc', 'av1'], default='auto', help='Codec preference. For Bilibili, auto defaults to best H.264/AVC; for YouTube, auto keeps best quality with MP4 preference.')
    ap.add_argument('--cookies', default='', help='Netscape cookies.txt path; overrides platform default')
    ap.add_argument('--youtube-cookies', default=str(DEFAULT_YOUTUBE_COOKIES), help='Default YouTube cookies.txt path')
    ap.add_argument('--bili-cookies', default=str(DEFAULT_BILI_COOKIES), help='Default Bilibili cookies.txt path')
    ap.add_argument('--mount', default='', help='Destination mounted folder under /var/minis/mounts or absolute path')
    ap.add_argument('--keep-workspace', action='store_true', help='Keep workspace copy after copying to phone')
    ap.add_argument('--no-copy', action='store_true', help='Only download to workspace')
    args = ap.parse_args()

    ensure_tool('yt-dlp', 'yt-dlp')
    ensure_tool('ffmpeg', 'ffmpeg')

    platform = detect_platform(args.url)
    args.platform = platform
    workdir = BASE_WORKDIR / platform
    workdir.mkdir(parents=True, exist_ok=True)
    before = set(workdir.glob('*'))

    cmd = ['yt-dlp', '--no-playlist']
    if platform == 'youtube':
        if not shutil.which('node'):
            run(['apk', 'add', 'nodejs'])
        cmd += ['--js-runtimes', 'node', '--remote-components', 'ejs:github']
        cookie_path = Path(args.cookies or args.youtube_cookies)
    elif platform == 'bilibili':
        cookie_path = Path(args.cookies or args.bili_cookies)
    else:
        cookie_path = Path(args.cookies) if args.cookies else None

    if cookie_path and cookie_path.exists():
        cmd += ['--cookies', str(cookie_path)]

    fmt = choose_format(platform, args.codec)
    cmd += [
        '--socket-timeout', '30',
        '--retries', '5',
        '--fragment-retries', '5',
        '-f', fmt,
        '--merge-output-format', 'mp4',
        '-o', str(workdir / '%(title).120s [%(id)s].%(ext)s'),
        args.url,
    ]
    run(cmd)

    output = latest_media(workdir, before)
    if not output:
        print('ERROR: download finished but no output file found', file=sys.stderr)
        sys.exit(1)
    copy_and_cleanup(output, args, workdir)


if __name__ == '__main__':
    main()
