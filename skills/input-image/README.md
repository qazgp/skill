# input-image

## English

Generate and edit images through the `ai.input.im` OpenAI-compatible image API, using the bundled helper script in `scripts/input_image.py`.

Use this skill when the user asks for:

- text-to-image generation
- image-to-image generation
- image editing
- `gpt-image-2`
- OpenAI-compatible `/v1/images/*` or `/v1/responses` image workflows

### Main Files

- `SKILL.md`: Minis skill instructions and trigger metadata.
- `scripts/input_image.py`: Command-line helper for image generation and editing.

### Notes

The API key should be provided through environment variables or Minis settings. Do not hard-code secrets in the repository.

## 中文

通过 `ai.input.im` 的 OpenAI 兼容图片接口生成和编辑图片，核心脚本是 `scripts/input_image.py`。

适用场景：

- 文生图
- 图生图
- 图片编辑 / 改图
- `gpt-image-2`
- OpenAI 兼容的 `/v1/images/*` 或 `/v1/responses` 图片流程

### 主要文件

- `SKILL.md`：Minis 技能说明和触发元数据。
- `scripts/input_image.py`：用于生成和编辑图片的命令行辅助脚本。

### 注意

API Key 应通过环境变量或 Minis 设置提供，不要写死在仓库里。
