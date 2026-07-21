# 02. 핵심 구조와 실습

## 1. 전체 데이터 흐름

```text
이미지 디렉터리 또는 PDF
  → 이미지 경로 수집 / PDF 페이지를 PNG로 변환
  → 이미지를 Base64 data URL로 인코딩
  → OpenAI 호환 chat payload 생성
  → SGLang SSE 스트림 수신
  → 페이지별 Markdown 저장
  → 요청 수·토큰·시간 집계
```

## 2. 프롬프트와 출력

Transformers API는 프롬프트 앞에 `<image>`를 포함하지만, SGLang의 chat payload에서는 이미지가 별도 콘텐츠 항목이므로 텍스트는 `document parsing.`입니다. 백엔드의 입력 템플릿이 이 둘을 연결합니다.

OCR 모델은 일반 대화 모델처럼 자유도가 높은 답을 생성하는 것이 목적이 아닙니다. 코드도 `temperature=0`으로 결정성을 높이고, 35-token n-gram 반복을 억제해 긴 출력에서 반복 루프를 줄입니다.

## 3. `gundam`과 `base`

- `gundam`: 단일 이미지에 사용하는 crop 기반 구성입니다. 원본 README 예시는 `base_size=1024`, `image_size=640`, `crop_mode=True`입니다.
- `base`: 1024 크기와 crop 없는 구성입니다. 다중 이미지와 PDF의 공식 경로입니다.

모드 선택은 품질·속도·메모리에 영향을 줄 수 있습니다. 동일 검증 세트로 측정하지 않은 채 이름만 보고 운영 기본값을 결정하지 마세요.

## 4. PDF 전처리

`pdf_to_images`는 `dpi / 72` 배율 행렬로 각 페이지를 렌더링합니다. 300 DPI는 작은 글자를 보존하지만 페이지 수와 면적에 비례해 임시 저장 공간이 증가합니다.

실무에서는 다음을 추가로 고려합니다.

- 암호화·손상 PDF 사전 검사
- 최대 페이지 수와 파일 크기 제한
- 임시 폴더의 수명 관리
- 회전된 페이지와 스캔 방향 정규화
- 저해상도 미리보기 후 필요한 페이지만 고해상도 처리

현재 `infer.py`가 만든 임시 PDF 이미지 폴더는 자동 삭제하지 않습니다. 장기 서비스에서는 요청 완료 후 안전하게 정리하는 래퍼가 필요합니다.

## 5. 병렬 실행

`ThreadPoolExecutor`가 요청을 동시에 보내며 기본 동시성은 8입니다. 이 값은 GPU 병렬성만 의미하지 않습니다. 이미지 Base64 크기, HTTP 연결, 디코딩 길이와 GPU KV cache가 함께 영향을 받습니다.

조정 절차:

1. 동시성 1로 기준 지연시간과 최대 메모리를 측정합니다.
2. 2, 4, 8 순서로 늘립니다.
3. 성공률, P50/P95 시간, TPS와 GPU 메모리를 함께 기록합니다.
4. OOM이나 tail latency 급증 직전보다 낮은 값을 운영 한도로 둡니다.

## 6. 재시도와 스트리밍

현재 코드는 요청당 최대 5번 시도하고 502 응답에는 점증 대기합니다. 다른 네트워크 오류도 재시도하지만 멱등성, 전체 시간 제한과 취소 전파는 호출자가 관리해야 합니다.

SSE 파서는 `data:` 행을 읽고 `[DONE]`에서 종료합니다. `choices[0].delta.content`가 있는 조각만 이어 붙여 Markdown 파일로 기록합니다. 조각 수를 `tokens`로 표시하지만 이는 토크나이저가 계산한 엄밀한 토큰 수가 아니라 **콘텐츠 이벤트 수**입니다. 따라서 TPS도 비교용 근사치로 해석해야 합니다.

## 7. 실습: GPU 없이 요청 확인

[`examples/build_sglang_request.py`](examples/build_sglang_request.py)는 로컬 이미지 한 장을 읽어 실제 코드와 같은 data URL payload를 만듭니다.

```bash
python guide/examples/build_sglang_request.py assets/baidu.png --summary-only
python guide/examples/build_sglang_request.py assets/baidu.png --output request.json
```

첫 명령은 민감한 Base64 본문을 출력하지 않고 MIME·바이트·URI 길이만 보여 줍니다. 두 번째는 서버에 보내기 전 구조 검토용 JSON을 생성합니다.

## 8. 품질 검증 설계

검증 세트는 실제 분포를 반영해야 합니다.

- 문서 유형: 보고서, 영수증, 표, 수식, 다단 편집
- 이미지 조건: 흐림, 기울기, 그림자, 저해상도
- 언어: 한국어/영어/숫자/특수문자 혼합
- 길이: 한 장부터 긴 PDF까지

문자 오류율(CER)만으로는 구조를 평가하기 어렵습니다. 표 셀 일치, 읽기 순서, Markdown 구조, 필수 필드 정확도와 치명적 숫자 오류율을 별도로 측정하세요.

[이전: 설치와 첫 실행](01_getting_started.md) · [다음: 운영·성능·보안](03_advanced.md)
