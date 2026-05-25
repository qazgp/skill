---
name: input-image
description: 使用 ai.input.im 的 OpenAI 兼容图片接口调用 gpt-image-2 进行文生图、图生图/图片编辑，也支持 Responses API 的 image_generation 工具。触发场景：用户要求“用 image 2 / gpt-image-2 / ai.input.im / images edits / images generations / responses / 文生图 / 图生图 / 改图 / 编辑图片 / 生成图片”，尤其当用户提供 curl 示例或要求使用 OPENAI_API_KEY 时。
version: 1.1.0
---
# Input Image / gpt-image-2

通过 `https://ai.input.im/v1` 的 OpenAI 兼容图片接口调用 `gpt-image-2`。

## 环境

- 使用环境变量 `OPENAI_API_KEY`，不要打印密钥值。
- 如需切换接口根地址，可设 `INPUT_IMAGE_BASE_URL`，默认 `https://ai.input.im/v1`。
- 检查密钥只允许：`[ -n "$OPENAI_API_KEY" ] && echo set || echo not_set`。
- 若未设置，回复用户：[Set OPENAI_API_KEY](minis://settings/environments?create_key=OPENAI_API_KEY&create_value=)

## 脚本

技能脚本：`/var/minis/skills/input-image/scripts/input_image.py`

### 文生图

```sh
python3 /var/minis/skills/input-image/scripts/input_image.py generate \
  "一只可爱的猫，暖色灯光，摄影质感" \
  --output /var/minis/workspace/cat.png \
  --model gpt-image-2 \
  --size 1024x1024
```

对应接口：`POST /v1/images/generations`，JSON：

```json
{"model":"gpt-image-2","prompt":"...","size":"1024x1024","n":1}
```

### 图生图 / 图片编辑

```sh
python3 /var/minis/skills/input-image/scripts/input_image.py edit \
  "将人物背景设置成温馨的二次元卧室，墙上贴满了D.Va的海报" \
  --image /var/minis/attachments/uploads/photo.jpg \
  --output /var/minis/workspace/edit.png \
  --model gpt-image-2 \
  --size 1024x1024
```

对应接口：`POST /v1/images/edits`，multipart form：

```sh
-F "model=gpt-image-2" \
-F "size=1024x1024" \
-F "prompt=..." \
-F "image=@/path/to/image.jpg"
```

支持可选 mask：`--mask /path/to/mask.png`，脚本会以 `mask` 表单字段上传。

### Responses API 文生图 / 带参考图编辑

```sh
python3 /var/minis/skills/input-image/scripts/input_image.py responses \
  "生成一张赛博朋克城市夜景，霓虹灯，电影感" \
  --output /var/minis/workspace/responses.png \
  --model gpt-image-2 \
  --size 1024x1024 \
  --quality high \
  --output-format png
```

带参考图时会把图片转为 data URL，通过 `input_image` 传入，工具 `action` 自动改为 `edit`：

```sh
python3 /var/minis/skills/input-image/scripts/input_image.py responses \
  "保留人物姿势，改成水彩插画风格" \
  --image /var/minis/attachments/uploads/photo.jpg \
  --output /var/minis/workspace/responses_edit.png
```

对应接口：`POST /v1/responses`，JSON 结构：

```json
{
  "model": "gpt-image-2",
  "input": "...",
  "tools": [{
    "type": "image_generation",
    "action": "generate",
    "size": "1024x1024",
    "quality": "high",
    "output_format": "png"
  }]
}
```

Responses 支持参数：`--size` 默认 `auto`；`--quality` 默认 `auto`；`--output-format png|jpeg|webp`；非 png 可用 `--output-compression 0..100`；`--moderation auto|low`；`--n` 会循环调用 `/responses` 保存多张。

## 工作流

1. 读取本技能说明后，直接用脚本执行，不要手写长 curl，避免泄露密钥和转义问题。
2. 如果用户给了图片附件，优先使用 `/var/minis/attachments/uploads/...` 中对应文件。
3. 输出文件放在 `/var/minis/workspace/`，文件名要简短可读，例如 `gpt_image2_edit.png`。
4. 成功后用 Markdown 链接返回：`[查看结果](minis://workspace/xxx.png)`；图片也可用 `![结果](minis://workspace/xxx.png)` 内联展示。
5. 如果 API 返回错误，简洁说明 HTTP 状态和错误文本，不要重试过多。

## 常用参数

- `--model` 默认 `gpt-image-2`
- `--size` 默认 `1024x1024`
- `--quality` 可选；不确定支持时省略
- `--n` 文生图和 responses 可用；responses 会循环调用 `/responses` 保存多张

## 注意

- 该 skill 使用用户提供的 OpenAI 兼容代理 `ai.input.im`，不是 Minis 内置 `minis-model-use`。
- `gpt-image-2` 在此接口中可通过 `/images/generations` 文生图、`/images/edits` 图生图/编辑，也可通过 `/responses` + `image_generation` 工具生成或参考图编辑。
- 永远不要输出 `$OPENAI_API_KEY` 的值。
