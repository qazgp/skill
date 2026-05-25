#!/usr/bin/env python3
import argparse, base64, json, mimetypes, os, sys, time
from pathlib import Path
from urllib import request, parse, error

API_BASE = os.environ.get('INPUT_IMAGE_BASE_URL', 'https://ai.input.im/v1')
API_KEY_ENV = 'OPENAI_API_KEY'


def die(msg, code=1):
    print(json.dumps({'success': False, 'error': msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


def get_key():
    key = os.environ.get(API_KEY_ENV)
    if not key:
        die(f'Missing {API_KEY_ENV}. Set it in Minis Settings → Environments.')
    return key


def multipart(fields, files):
    boundary = '----MinisFormBoundary' + str(int(time.time()*1000))
    chunks = []
    for name, value in fields.items():
        chunks.append(f'--{boundary}\r\n'.encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(str(value).encode())
        chunks.append(b'\r\n')
    for name, path in files.items():
        p = Path(path)
        if not p.exists():
            die(f'File not found: {p}')
        mime = 'image/png' if p.suffix.lower() == '.png' else 'image/jpeg'
        chunks.append(f'--{boundary}\r\n'.encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"; filename="{p.name}"\r\n'.encode())
        chunks.append(f'Content-Type: {mime}\r\n\r\n'.encode())
        chunks.append(p.read_bytes())
        chunks.append(b'\r\n')
    chunks.append(f'--{boundary}--\r\n'.encode())
    return b''.join(chunks), boundary


def extract_image(resp):
    data = json.loads(resp.decode('utf-8'))
    if isinstance(data, dict) and data.get('data'):
        item = data['data'][0]
        if item.get('b64_json'):
            return base64.b64decode(item['b64_json']), data
        if item.get('url'):
            req = request.Request(item['url'], headers={'User-Agent': 'Minis/1.0'})
            with request.urlopen(req, timeout=300) as r:
                return r.read(), data
    die('No image found in API response: ' + json.dumps(data, ensure_ascii=False)[:500])


def _normalize_b64_text(text):
    value = str(text).strip()
    if value.startswith('data:image/') and ',' in value:
        value = value.split(',', 1)[1].strip()
    return value


def extract_responses_images(resp):
    data = json.loads(resp.decode('utf-8'))
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key in ('result', 'b64_json', 'image_base64'):
                value = node.get(key)
                if isinstance(value, str):
                    value = _normalize_b64_text(value)
                    if value:
                        found.append(value)
            for key in ('data', 'output', 'content'):
                value = node.get(key)
                if isinstance(value, list):
                    for item in value:
                        walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    unique = []
    seen = set()
    for item in found:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    if not unique:
        die('No image found in Responses API response: ' + json.dumps(data, ensure_ascii=False)[:500])
    return [base64.b64decode(item) for item in unique], data


def guess_ext(image_bytes):
    if image_bytes.startswith(b'\x89PNG'):
        return 'png'
    if image_bytes.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:16]:
        return 'webp'
    return 'png'


def build_data_url(path):
    p = Path(path)
    if not p.exists():
        die(f'File not found: {p}')
    mime = mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
    b64 = base64.b64encode(p.read_bytes()).decode('utf-8')
    return f'data:{mime};base64,{b64}'


def build_responses_payload(args):
    tool = {'type': 'image_generation', 'action': 'edit' if args.image else 'generate'}
    if args.size != 'auto':
        tool['size'] = args.size
    if args.quality != 'auto':
        tool['quality'] = args.quality
    if args.output_format:
        tool['output_format'] = args.output_format
    if args.output_format != 'png' and args.output_compression is not None:
        tool['output_compression'] = args.output_compression
    if args.moderation != 'auto':
        tool['moderation'] = args.moderation

    if args.image:
        input_payload = [{
            'role': 'user',
            'content': [
                {'type': 'input_text', 'text': args.prompt},
                {'type': 'input_image', 'image_url': build_data_url(args.image)},
            ],
        }]
    else:
        input_payload = args.prompt
    return {'model': args.model, 'input': input_payload, 'tools': [tool]}
def call_json(endpoint, payload, key):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = request.Request(API_BASE + endpoint, data=body, method='POST', headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Apifox/1.0.0',
    })
    try:
        with request.urlopen(req, timeout=600) as r:
            return r.read()
    except error.HTTPError as e:
        die(f'HTTP {e.code}: {e.read().decode("utf-8", "ignore")[:1000]}')


def call_multipart(endpoint, fields, files, key):
    body, boundary = multipart(fields, files)
    req = request.Request(API_BASE + endpoint, data=body, method='POST', headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'User-Agent': 'Apifox/1.0.0',
    })
    try:
        with request.urlopen(req, timeout=600) as r:
            return r.read()
    except error.HTTPError as e:
        die(f'HTTP {e.code}: {e.read().decode("utf-8", "ignore")[:1000]}')


def main():
    ap = argparse.ArgumentParser(description='Generate or edit images using ai.input.im OpenAI-compatible image API')
    sub = ap.add_subparsers(dest='cmd', required=True)
    t = sub.add_parser('generate', help='text-to-image')
    t.add_argument('prompt')
    t.add_argument('--output', '-o', default='/var/minis/workspace/input_image.png')
    t.add_argument('--model', default='gpt-image-2')
    t.add_argument('--size', default='1024x1024')
    t.add_argument('--quality', default=None)
    t.add_argument('--n', type=int, default=1)
    e = sub.add_parser('edit', help='image edit / image-to-image')
    e.add_argument('prompt')
    e.add_argument('--image', '-i', required=True)
    e.add_argument('--output', '-o', default='/var/minis/workspace/input_image_edit.png')
    e.add_argument('--model', default='gpt-image-2')
    e.add_argument('--size', default='1024x1024')
    e.add_argument('--quality', default=None)
    e.add_argument('--mask', default=None)
    r = sub.add_parser('responses', help='text-to-image or image edit via /responses')
    r.add_argument('prompt')
    r.add_argument('--image', '-i', default=None, help='optional reference image for edit action')
    r.add_argument('--output', '-o', default='/var/minis/workspace/input_image_responses.png')
    r.add_argument('--model', default='gpt-image-2')
    r.add_argument('--size', default='auto')
    r.add_argument('--quality', default='auto')
    r.add_argument('--output-format', choices=['png', 'jpeg', 'webp'], default='png')
    r.add_argument('--output-compression', type=int, default=90)
    r.add_argument('--moderation', default='auto')
    r.add_argument('--n', type=int, default=1, help='loop /responses calls and save up to n images')
    args = ap.parse_args()
    key = get_key()
    if args.cmd == 'generate':
        payload = {'model': args.model, 'prompt': args.prompt, 'size': args.size, 'n': args.n}
        if args.quality:
            payload['quality'] = args.quality
        raw = call_json('/images/generations', payload, key)
        img, meta = extract_image(raw)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(img)
        print(json.dumps({'success': True, 'path': str(out), 'size': out.stat().st_size, 'response_keys': list(meta.keys())}, ensure_ascii=False))
    elif args.cmd == 'edit':
        fields = {'model': args.model, 'prompt': args.prompt, 'size': args.size}
        if args.quality:
            fields['quality'] = args.quality
        files = {'image': args.image}
        if args.mask:
            files['mask'] = args.mask
        raw = call_multipart('/images/edits', fields, files, key)
        img, meta = extract_image(raw)
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(img)
        print(json.dumps({'success': True, 'path': str(out), 'size': out.stat().st_size, 'response_keys': list(meta.keys())}, ensure_ascii=False))
    else:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        saved = []
        meta_keys = []
        for idx in range(max(1, args.n)):
            raw = call_json('/responses', build_responses_payload(args), key)
            images, meta = extract_responses_images(raw)
            meta_keys = list(meta.keys())
            for image_bytes in images:
                if len(saved) >= args.n:
                    break
                if args.n == 1:
                    path = out
                else:
                    path = out.with_name(f'{out.stem}_{len(saved)+1}{out.suffix or "." + guess_ext(image_bytes)}')
                    if not path.suffix:
                        path = path.with_suffix('.' + guess_ext(image_bytes))
                path.write_bytes(image_bytes)
                saved.append(str(path))
            if len(saved) >= args.n:
                break
        print(json.dumps({'success': True, 'paths': saved, 'count': len(saved), 'response_keys': meta_keys}, ensure_ascii=False))

if __name__ == '__main__':
    main()
