# youtube-best-download

## English

Download YouTube and Bilibili videos with `yt-dlp`, prioritizing the best available quality while preferring MP4/M4A when that does not reduce quality.

The skill can:

- detect YouTube, `youtu.be`, Bilibili, and `b23.tv` links
- use YouTube cookies for age-restricted videos
- use Bilibili cookies for logged-in/high-quality formats such as 1080P, 4K, and 60fps
- merge streams with `ffmpeg`
- copy the finished video to a mounted phone folder under `/var/minis/mounts/`
- delete the Minis workspace copy by default after a successful copy

### Main Command

```bash
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py 'VIDEO_URL'
```

Useful options:

```bash
--keep-workspace    Keep the Minis workspace copy
--no-copy           Only download to workspace
--mount minis       Copy to a specific mounted folder
--cookies PATH      Override platform cookie file
```

### Main Files

- `SKILL.md`: Minis skill instructions and trigger metadata.
- `scripts/youtube_best_download.py`: Download automation script.

## 中文

使用 `yt-dlp` 下载 YouTube 和 B 站视频，策略是：**最高画质优先，尽量 MP4/M4A，但不为了 MP4 牺牲画质**。

这个技能可以：

- 自动识别 YouTube、`youtu.be`、哔哩哔哩、`b23.tv` 链接
- 使用 YouTube Cookie 下载年龄限制视频
- 使用 B 站 Cookie 获取登录后可用的 1080P、4K、60fps 等高画质
- 用 `ffmpeg` 合并音视频流
- 将成品复制到 `/var/minis/mounts/` 下的手机挂载目录
- 成功复制后默认删除 Minis 虚拟机工作区副本

### 主要命令

```bash
python3 /var/minis/skills/youtube-best-download/scripts/youtube_best_download.py '视频链接'
```

常用选项：

```bash
--keep-workspace    保留 Minis 工作区副本
--no-copy           只下载到工作区，不复制到手机
--mount minis       指定手机挂载目录
--cookies PATH      指定 Cookie 文件
```

### 主要文件

- `SKILL.md`：Minis 技能说明和触发元数据。
- `scripts/youtube_best_download.py`：自动下载脚本。
