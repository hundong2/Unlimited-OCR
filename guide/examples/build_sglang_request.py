"""Unlimited-OCR용 SGLang 요청을 네트워크 호출 없이 생성한다.

실행 예:
    python guide/examples/build_sglang_request.py assets/baidu.png --summary-only
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


def encode_image(image_path: Path) -> tuple[str, int, str]:
    """이미지를 읽고 MIME, 원본 크기, data URL을 반환한다."""
    if not image_path.is_file():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

    suffix = image_path.suffix.lower()
    if suffix not in MIME_TYPES:
        supported = ", ".join(sorted(MIME_TYPES))
        raise ValueError(f"지원하지 않는 확장자입니다: {suffix} (지원: {supported})")

    raw = image_path.read_bytes()
    if not raw:
        raise ValueError(f"빈 이미지 파일입니다: {image_path}")

    mime = MIME_TYPES[suffix]
    encoded = base64.b64encode(raw).decode("ascii")
    return mime, len(raw), f"data:{mime};base64,{encoded}"


def build_payload(image_path: Path, image_mode: str) -> tuple[dict, dict]:
    """저장소의 SGLang 예제와 같은 핵심 필드로 요청을 만든다."""
    mime, byte_count, data_url = encode_image(image_path)
    payload = {
        "model": "Unlimited-OCR",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "document parsing."},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        "temperature": 0,
        "skip_special_tokens": False,
        "images_config": {"image_mode": image_mode},
        "stream": True,
    }
    summary = {
        "model": payload["model"],
        "prompt": payload["messages"][0]["content"][0]["text"],
        "image MIME": mime,
        "image bytes": byte_count,
        "data URL characters": len(data_url),
        "image mode": image_mode,
    }
    return payload, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="입력 이미지 경로")
    parser.add_argument("--image-mode", choices=("gundam", "base"), default="gundam")
    parser.add_argument("--output", type=Path, help="payload JSON 저장 경로")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Base64 본문을 출력하지 않고 안전한 요약만 표시",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload, summary = build_payload(args.image, args.image_mode)

    if args.output:
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"요청 JSON 저장: {args.output}")

    if args.summary_only or not args.output:
        for key, value in summary.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
