# Unlimited OCR Works

[English](README.md) | **한국어** | [한국어 학습 가이드](guide/README.md)

> 이 문서는 원본 [`README.md`](README.md)의 한국어 번역본입니다.
> 번역 기준: 2026-07-21, 원본 커밋 `528fca4e2161e23231d05666a6d35155dcb1957e`

Unlimited-OCR은 한 번의 긴 생성 과정으로 문서 이미지와 여러 페이지를 구조화해 파싱하는 OCR 모델입니다.

![Unlimited OCR 개요](assets/Unlimited-OCR.png)

## 공개 이력

- **2026-07-03**: Baidu Cloud에서 모델 제공
- **2026-06-28**: vLLM 추론 지원
- **2026-06-24**: Hugging Face Spaces 데모 공개
- **2026-06-23**: [arXiv 논문](https://arxiv.org/abs/2606.23050) 공개, ModelScope 모델 제공
- **2026-06-22**: DeepSeek-OCR을 확장하는 Unlimited-OCR 공개

주요 링크: [공식 원본 저장소](https://github.com/baidu/Unlimited-OCR) · [Hugging Face 모델](https://huggingface.co/baidu/Unlimited-OCR) · [ModelScope](https://modelscope.cn/models/PaddlePaddle/Unlimited-OCR) · [Baidu Cloud](https://cloud.baidu.com/doc/OCR/s/fmr1p39gb)

## 추론

### Transformers

NVIDIA GPU에서 Hugging Face Transformers로 추론할 수 있습니다. 공식 확인 환경은 Python 3.12.3과 CUDA 12.9이며 다음 버전을 사용합니다.

```text
torch==2.10.0
torchvision==0.25.0
transformers==4.57.1
Pillow==12.1.1
matplotlib==3.10.8
einops==0.8.2
addict==2.4.0
easydict==1.13
pymupdf==1.27.2.2
psutil==7.2.2
```

```python
import torch
from transformers import AutoModel, AutoTokenizer

model_name = "baidu/Unlimited-OCR"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    trust_remote_code=True,
    use_safetensors=True,
    torch_dtype=torch.bfloat16,
).eval().cuda()

# 단일 이미지는 gundam 또는 base 구성을 지원합니다.
model.infer(
    tokenizer,
    prompt="<image>document parsing.",
    image_file="your_image.jpg",
    output_path="your/output/dir",
    base_size=1024,
    image_size=640,
    crop_mode=True,
    max_length=32768,
    no_repeat_ngram_size=35,
    ngram_window=128,
    save_results=True,
)
```

단일 이미지의 두 구성은 다음과 같습니다.

| 구성 | `base_size` | `image_size` | `crop_mode` |
|---|---:|---:|---|
| `gundam` | 1024 | 640 | `True` |
| `base` | 1024 | 1024 | `False` |

여러 이미지나 PDF 페이지는 `base` 구성만 사용합니다.

```python
model.infer_multi(
    tokenizer,
    prompt="<image>Multi page parsing.",
    image_files=["page1.png", "page2.png", "page3.png"],
    output_path="your/output/dir",
    image_size=1024,
    max_length=32768,
    no_repeat_ngram_size=35,
    ngram_window=1024,
    save_results=True,
)
```

PDF는 PyMuPDF로 각 페이지를 이미지로 변환한 뒤 `infer_multi`에 전달합니다. 전체 예시는 원본 [`README.md`](README.md)를 참고하세요.

### vLLM

배포 방법은 [공식 vLLM 레시피](https://recipes.vllm.ai/baidu/Unlimited-OCR)를 참고하세요.

```bash
# 기본 이미지: CUDA 13.0
docker pull vllm/vllm-openai:unlimited-ocr

# Hopper GPU: CUDA 12.9
docker pull vllm/vllm-openai:unlimited-ocr-cu129
```

### SGLang

`uv` 가상 환경을 만든 뒤 저장소에 포함된 wheel과 고정 버전 의존성을 설치합니다.

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install wheel/sglang-0.0.0.dev11416+g92e8bb79e-py3-none-any.whl
uv pip install kernels==0.11.7
uv pip install pymupdf==1.27.2.2
```

서버를 실행합니다.

```bash
python -m sglang.launch_server \
    --model baidu/Unlimited-OCR \
    --served-model-name Unlimited-OCR \
    --attention-backend fa3 \
    --page-size 1 \
    --mem-fraction-static 0.8 \
    --context-length 32768 \
    --enable-custom-logit-processor \
    --disable-overlap-schedule \
    --skip-server-warmup \
    --host 0.0.0.0 \
    --port 10000
```

OpenAI 호환 엔드포인트는 `http://127.0.0.1:10000/v1/chat/completions`입니다. 이미지 데이터 URL과 프롬프트를 메시지 콘텐츠로 보내며, 반복 생성을 억제하기 위해 전용 n-gram logit processor를 함께 지정합니다.

저장소의 `infer.py`는 서버 기동과 병렬 요청을 자동화합니다.

```bash
# 이미지 디렉터리
python infer.py \
    --image_dir ./examples/images \
    --output_dir ./outputs \
    --concurrency 8 \
    --image_mode gundam

# PDF
python infer.py \
    --pdf ./examples/document.pdf \
    --output_dir ./outputs \
    --concurrency 8 \
    --image_mode gundam
```

주요 옵션:

- `--model_dir`: 로컬 모델 경로나 Hugging Face 모델 ID
- `--gpu`: `CUDA_VISIBLE_DEVICES`에 전달할 GPU 번호
- `--concurrency`: 동시에 처리할 요청 수
- `--image_mode`: `gundam` 또는 `base`
- `--server_log`: SGLang 서버 로그 파일

상세한 설치, 보안, 튜닝, 장애 대응은 [한국어 학습 가이드](guide/README.md)를 참고하세요.

## 시각화

![장시간 OCR 데모](assets/long-horizon-ocr.gif)

## 감사의 말

유용한 모델과 아이디어를 제공한 [DeepSeek-OCR](https://github.com/deepseek-ai/DeepSeek-OCR), [DeepSeek-OCR-2](https://github.com/deepseek-ai/DeepSeek-OCR-2), [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)에 감사드립니다.

## 인용

```bibtex
@misc{yin2026unlimitedocrworks,
  title={Unlimited OCR Works},
  author={Youyang Yin and Huanhuan Liu and YY and Qunyi Xie and Chaorun Liu and Shiqi Yang and Shaohua Wang and Zhanlong Liu and Hao Zou and Jinyue Chen and Shu Wei and Jingjing Wu and Mingxin Huang and Zhen Wu and Guibin Wang and Tengyu Du and Lei Jia},
  year={2026},
  eprint={2606.23050},
  archivePrefix={arXiv},
  primaryClass={cs.CV},
  url={https://arxiv.org/abs/2606.23050}
}
```

## 라이선스와 기여

코드는 저장소의 [LICENSE](LICENSE)를 따릅니다. 문제나 기능 제안은 upstream 이슈를 이용하고, 기여 전에는 [CONTRIBUTING.md](CONTRIBUTING.md)의 PEP 8·테스트·GitHub Actions 요구 사항을 확인하세요.
