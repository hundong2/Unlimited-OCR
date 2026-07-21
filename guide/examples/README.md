# 요청 생성 실습

## 학습 목표

- 이미지가 OpenAI 호환 멀티모달 메시지로 변환되는 과정을 이해합니다.
- 서버 호출 전에 MIME, 파일 크기와 payload 구조를 검사합니다.
- 실제 문서의 Base64 본문이 콘솔이나 로그에 노출되지 않게 요약 모드를 사용합니다.

## 요구 사항

- Python 3.10 이상
- 외부 패키지 없음
- PNG, JPEG, WebP 또는 BMP 이미지 한 장

## 실행

저장소 루트에서 실행합니다.

```bash
python guide/examples/build_sglang_request.py assets/baidu.png --summary-only
```

예상 출력은 파일에 따라 숫자가 달라지지만 다음 형태입니다.

```text
model: Unlimited-OCR
prompt: document parsing.
image MIME: image/png
image bytes: <원본 바이트 수>
data URL characters: <인코딩된 길이>
image mode: gundam
```

JSON 파일이 필요하면 다음처럼 실행합니다.

```bash
python guide/examples/build_sglang_request.py assets/baidu.png \
  --image-mode base \
  --output request.json
```

`request.json`에는 이미지 원문이 Base64로 포함되므로 저장·공유·로그 정책에 주의하세요. 이 실습은 요청만 만들며 서버에 전송하지 않습니다.
