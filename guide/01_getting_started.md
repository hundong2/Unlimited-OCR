# 01. 설치와 첫 실행

## 1. 실행 전 확인

공식 Transformers 예시는 Python 3.12.3, CUDA 12.9, BF16을 지원하는 NVIDIA GPU에서 확인되었습니다. 실제 설치 전 다음을 점검하세요.

```bash
python --version
nvidia-smi
```

Windows PowerShell에서는 가상 환경 활성화 명령이 `\.venv\Scripts\Activate.ps1`이고, Linux/macOS에서는 `source .venv/bin/activate`입니다. SGLang·CUDA wheel 호환성 때문에 Linux 또는 NVIDIA Container Toolkit 환경이 일반적으로 수월합니다.

## 2. 백엔드 선택

### Transformers

모델 객체와 토크나이저를 Python 안에서 직접 제어합니다. 한 장 실험이나 API 이해에 좋지만 프로세스별 모델 메모리를 직접 관리해야 합니다.

### vLLM

OpenAI 호환 서버와 높은 처리량이 필요할 때 선택합니다. 저장소 README가 연결한 공식 vLLM 레시피와 GPU별 컨테이너를 우선 사용하세요.

### SGLang

저장소의 `infer.py`를 그대로 활용하려면 이 경로를 선택합니다. 스크립트가 포트 10000의 서버를 확인하고, 없으면 직접 기동한 후 이미지/PDF 작업을 병렬 처리합니다.

## 3. 격리된 환경 만들기

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install wheel/sglang-0.0.0.dev11416+g92e8bb79e-py3-none-any.whl
uv pip install kernels==0.11.7 pymupdf==1.27.2.2
```

저장소의 wheel은 특정 개발 커밋을 담고 있습니다. 다른 SGLang 버전으로 임의 교체하기 전에 custom logit processor와 서버 인자가 호환되는지 확인하세요.

## 4. 모델 내려받기와 보안

Transformers 경로는 `trust_remote_code=True`를 사용합니다. 실험에서는 편리하지만 공급망 위험을 줄이려면 다음 원칙을 적용하세요.

1. 모델 카드와 파일 목록을 검토합니다.
2. 검증한 revision 또는 commit hash를 고정합니다.
3. 토큰과 개인 문서는 격리된 실행 환경에만 제공합니다.
4. 모델 캐시와 출력 디렉터리의 접근 권한을 제한합니다.

모델이 공개라면 일반적으로 Hugging Face 토큰은 필수가 아닙니다. 접근 제한이나 rate limit이 있다면 `HF_TOKEN`을 설정하되 소스 코드나 셸 기록에 값을 남기지 마세요.

## 5. 최소 실행

### 이미지 디렉터리

```bash
python infer.py \
  --image_dir ./examples/images \
  --output_dir ./outputs \
  --concurrency 1 \
  --image_mode gundam
```

처음에는 동시성을 1로 두고 성공을 확인한 뒤 늘립니다. `infer.py`는 `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`를 재귀 탐색하고 큰 파일부터 요청합니다.

### PDF

```bash
python infer.py \
  --pdf ./examples/document.pdf \
  --output_dir ./outputs \
  --concurrency 1 \
  --image_mode base
```

코드는 PDF를 300 DPI PNG로 변환해 페이지별 요청으로 처리합니다. 원본 README의 Transformers 다중 페이지 설명은 `base`만 지원한다고 안내하므로 PDF에서도 우선 `base`를 사용하세요. 현재 CLI 기본값은 `gundam`이므로 명시적으로 선택하는 편이 안전합니다.

## 6. 성공 여부 확인

정상 실행 시 다음을 확인합니다.

- 서버 로그: `log/sglang_server.log`
- 페이지별 결과: `outputs/*.md`
- 요약: 성공 요청 수, 총 토큰, wall time, 시스템 TPS
- 실패: 마지막 재시도 후 `FAILED`가 출력되는지

출력 파일이 생겼다는 사실만으로 정확성을 판단하지 마세요. 최소 10~20개의 대표 문서에서 누락, 읽기 순서, 표 구조와 숫자를 육안 대조합니다.

## 7. 첫 문제 해결

| 증상 | 확인할 것 | 조치 |
|---|---|---|
| CUDA OOM | 모델 크기, 이미지 모드, 동시성 | `--concurrency 1`, 다른 GPU, 서버 메모리 설정 검토 |
| 서버 준비 시간 초과 | `server_log`, 모델 다운로드 | 네트워크·디스크·CUDA 오류 확인 |
| 포트 10000 충돌 | 기존 프로세스 또는 `/health` | 기존 서버를 재사용하거나 프로세스 정리 |
| PDF 변환 실패 | PyMuPDF 설치, 암호화 PDF | 의존성/암호 해제/파일 무결성 확인 |
| 빈 결과 | HTTP 상태, 스트림, 입력 이미지 | 서버 로그와 원본 해상도, 프롬프트 확인 |

[다음: 핵심 구조와 실습](02_core_concepts.md)
