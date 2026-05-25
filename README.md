# Minis Skills

A personal collection of reusable Minis skills. Each skill lives in its own directory under `skills/` and includes bilingual documentation.

个人 Minis 技能仓库。每个技能都放在 `skills/` 下的独立目录中，并包含中英文说明。

## Skills / 技能列表

| Skill | Description | 中文说明 |
| --- | --- | --- |
| [`input-image`](skills/input-image/) | Generate and edit images through the ai.input.im OpenAI-compatible image API. | 通过 ai.input.im 的 OpenAI 兼容图片接口进行文生图、图生图和图片编辑。 |
| [`youtube-best-download`](skills/youtube-best-download/) | Download YouTube and Bilibili videos at the best available quality, copy them to phone storage, and clean workspace copies by default. | 下载 YouTube 和 B 站视频，最高画质优先，保存到手机挂载目录，并默认清理虚拟机副本。 |

## Repository Layout / 仓库结构

```text
skills/
  input-image/
    SKILL.md
    README.md
    scripts/
  youtube-best-download/
    SKILL.md
    README.md
    scripts/
```

## Usage / 使用方式

Copy or sync a skill directory into Minis' skills folder:

```bash
cp -r skills/<skill-name> /var/minis/skills/
```

将某个技能目录复制或同步到 Minis 的技能目录：

```bash
cp -r skills/<技能名> /var/minis/skills/
```

`SKILL.md` is the file Minis reads as the skill entry point. `README.md` is for humans browsing this repository.

`SKILL.md` 是 Minis 读取的技能入口文件；`README.md` 方便人在 GitHub 上查看说明。
