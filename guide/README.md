# Unlimited-OCR 한국어 학습 가이드

작성일: 2026-07-21

대상 버전: `528fca4e2161e23231d05666a6d35155dcb1957e`

출처: [Unlimited-OCR 저장소](https://github.com/hundong2/Unlimited-OCR), [한국어 README](../README_kor.md)

## 이 프로젝트가 해결하는 문제

일반 OCR 파이프라인은 문자 검출, 인식, 읽기 순서 복원, 표·수식·레이아웃 분석을 여러 단계로 나눕니다. Unlimited-OCR은 문서 이미지 또는 여러 페이지를 시각 언어 모델에 입력하고, 긴 출력 한 번으로 구조화된 문서 내용을 생성하는 **one-shot long-horizon parsing**을 지향합니다.

이 가이드는 단순 실행 명령을 넘어 입력 전처리, 추론 백엔드 선택, 병렬 처리, 품질 검증과 안전한 서비스 운영까지 설명합니다.

## 학습 순서

1. [설치와 첫 실행](01_getting_started.md): 필수 개념, 환경 점검, Transformers/SGLang 최소 실행
2. [핵심 구조와 실습](02_core_concepts.md): 프롬프트, 이미지 모드, PDF 변환, SSE 응답과 `infer.py`
3. [운영·성능·보안](03_advanced.md): 메모리, 동시성, 품질 평가, 장애 대응과 배포
4. [요청 생성 실습](examples/README.md): GPU나 모델 없이 OpenAI 호환 요청 JSON 만들기

## 빠른 선택표

| 목표 | 권장 경로 | 이유 |
|---|---|---|
| Python에서 한 장 시험 | Transformers | 모델 API를 직접 확인하기 쉬움 |
| 기존 추론 서버에 통합 | vLLM | 공식 레시피와 컨테이너 제공 |
| 이 저장소의 배치 스크립트 사용 | SGLang | `infer.py`가 서버와 요청을 함께 관리 |
| GPU 없이 요청 형식 학습 | `guide/examples` | 네트워크 호출 없이 payload 확인 가능 |

## 저장소 구조

```text
Unlimited-OCR/
├── README.md              # 영문 원본 안내
├── README_kor.md          # 한국어 번역
├── infer.py               # SGLang 서버 기동 및 병렬 추론
├── wheel/                 # 저장소가 제공하는 SGLang wheel
├── assets/                # 문서 이미지와 데모
├── Unlimited-OCR.pdf      # 논문 PDF
└── guide/                 # 한국어 단계별 학습 자료
```

## 핵심 용어

- **OCR**: 이미지의 문자를 기계가 다룰 수 있는 텍스트로 변환하는 기술
- **문서 파싱**: 문자뿐 아니라 제목, 문단, 표, 수식, 읽기 순서 같은 구조까지 복원하는 작업
- **long-horizon generation**: 많은 토큰을 연속 생성해 긴 문서 결과를 구성하는 방식
- **SSE**: 서버가 `data:` 이벤트를 연속 전송하는 HTTP 스트리밍 형식
- **context length**: 한 요청에서 모델이 다룰 수 있는 입력·출력 문맥의 최대 범위
- **n-gram 억제**: 이미 생성한 토큰 패턴의 불필요한 반복을 막는 후처리

## 반드시 알아둘 제한

- 공식 예시는 NVIDIA GPU, CUDA와 특정 라이브러리 버전을 전제로 합니다.
- `trust_remote_code=True`는 내려받은 모델 저장소의 Python 코드를 실행하므로, 운영 환경에서는 revision 고정과 코드 검토가 필요합니다.
- OCR 결과는 사실 검증이 아닙니다. 숫자, 날짜, 계좌·법률·의료 정보는 원문 이미지와 대조해야 합니다.
- PDF를 300 DPI 이미지로 바꾸면 메모리와 임시 디스크 사용량이 크게 늘 수 있습니다.
- 이 문서는 코드와 README를 기반으로 한 학습 자료이며 실제 GPU 추론 결과를 보증하지 않습니다.

## 다음 단계

처음이라면 [설치와 첫 실행](01_getting_started.md)부터 시작하세요. 이미 SGLang을 운영한다면 [핵심 구조와 실습](02_core_concepts.md)의 요청 흐름을 읽고 [운영·성능·보안](03_advanced.md)으로 이동하면 됩니다.
