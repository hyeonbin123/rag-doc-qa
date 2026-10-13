"""Convert skt/A.X-4.0-Light to a bf16 GGUF with llama.cpp's converter (docs/experiments.md v13).

This is how the v13 candidate G3 (`a.x-4.0-light:q4_k_m`) was built; the repo had no official
GGUF on 2026-10-04.

Why a wrapper: transformers 5.x's AutoTokenizer loads this repo as Qwen2Tokenizer (from
config.json's model_type qwen2) and pre-tokenizes with Qwen2's regex, so the converter's check
text hashes to 261dca7f... and the converter stops. The repo declares tokenizer_class
GPT2Tokenizer and ships a tokenizer.json with a ByteLevel GPT-2 pre-tokenizer. Loaded as
declared (GPT2TokenizerFast, i.e. tokenizer.json) the check text hashes to b0a6b1c0..., which
llama.cpp registers as "a.x-4.0". The wrapper only hands the converter that tokenizer.

The whole build (each step as run for v13):

1. llama.cpp checkout at 81bc6b83f827df746eb129235488d325c49cae52, then from this repo's root:
       uv run --no-sync --with sentencepiece==0.2.2 python scripts/ax40_light/convert.py \
           --llama-cpp <checkout> A.X-4.0-Light-bf16.gguf
2. llama.cpp release b11255's llama-quantize:
       llama-quantize A.X-4.0-Light-bf16.gguf A.X-4.0-Light-Q4_K_M.gguf Q4_K_M
3. Drop the GGUF's jinja chat template, so Ollama uses the Modelfile's template (Ollama 0.35.1
   prefers a GGUF template that supports tools over the Modelfile's and ignores the latter):
       python <checkout>/gguf-py/gguf/scripts/gguf_new_metadata.py --force \
           --remove-metadata tokenizer.chat_template \
           A.X-4.0-Light-Q4_K_M.gguf A.X-4.0-Light-Q4_K_M-gotmpl.gguf
   v13's file had sha256 330634890beb44ac970bc7c12f96294e9be2d2a3111fe43101b65f330235d79b.
4. With scripts/ax40_light/Modelfile copied next to that file, in that folder:
       ollama create a.x-4.0-light:q4_k_m -f Modelfile
   v13's model had digest a874a70d2c09d0b718662cc3f52e38a85c34eacfb29284996530edfbc23d8661.

Without --snapshot the pinned revision is taken from the Hugging Face cache (HF_HOME) or
downloaded (about 14.5 GB of safetensors).
"""

# [파일 역할] v13 생성 후보 G3(A.X-4.0-Light)를 Ollama에서 쓰려고 Hugging Face 원본을 bf16 GGUF로 바꾸는
# llama.cpp 변환기의 얇은 래퍼다. 위 docstring의 1~4단계 중 1단계에 해당한다.
# [왜 공개 저장소에 있나] A.X는 공식 GGUF가 없어 직접 변환한 모델이라, 변환 방법이 없으면 다른 사람이 G3를
# 다시 만들 수 없다. 그래서 측정에 쓴 변환 스크립트를 경로만 인자로 바꿔 scripts/ax40_light/에 Modelfile과
# 함께 두었고, --vocab-only로 다시 변환해 처음 만든 파일과 sha256까지 같음을 확인했다(docs/experiments.md v13
# 'A.X-4.0-Light 변환' 추가 절).
# [하는 일] 변환기가 토크나이저를 불러오는 AutoTokenizer.from_pretrained를 저장소가 선언한 GPT2TokenizerFast로
# 바꿔 끼운 뒤, llama.cpp의 convert_hf_to_gguf.py를 같은 프로세스에서 그대로 실행한다. 변환기 코드는 고치지
# 않는다.

import argparse
import runpy
import sys
from pathlib import Path

# transformers: 변환기가 쓰는 AutoTokenizer를 바꿔 끼우고, 선언된 토크나이저(GPT2TokenizerFast)를 불러온다.
# huggingface_hub: 고정 리비전의 원본 파일을 받거나 HF 캐시(HF_HOME)에서 찾는다.
import transformers
from huggingface_hub import snapshot_download
from transformers import GPT2TokenizerFast

# 측정에 쓴 원본을 리비전까지 고정한다(v13 후보 표와 같은 값). FILES는 v13 때 받은 파일 패턴과 같게 둬 같은
# 스냅숏을 받게 한다.
REPO = "skt/A.X-4.0-Light"
REVISION = "ba21c20ea1b31ded1ec3e2fb432335077dc4be98"
FILES = ["*.json", "*.safetensors", "merges.txt", "LICENSE", "README.md"]  # as downloaded for v13


# AutoTokenizer.from_pretrained 자리에 들어갈 대체 함수. 어떤 경로로 불려도 저장소가 선언한
# GPT2TokenizerFast(tokenizer.json, GPT-2 바이트 단위 사전 분할)로 불러온다.
# 변환기는 일부 경로에서 trust_remote_code=True를 넘기는데, 원격 코드가 필요 없는 토크나이저이므로 그 인자는
# 버린다.
def declared_tokenizer(path, *args, **kwargs):
    kwargs.pop("trust_remote_code", None)
    return GPT2TokenizerFast.from_pretrained(path, *args, **kwargs)


# 인자를 받아 스냅숏을 준비하고 변환기를 실행한다. --vocab-only는 텐서 없이 토크나이저 메타데이터만 쓰며,
# 공개한 래퍼가 처음 변환과 같은 결과를 내는지 확인할 때 썼다.
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("outfile", help="the bf16 GGUF to write")
    parser.add_argument("--llama-cpp", required=True, type=Path, help="llama.cpp checkout (81bc6b8)")
    parser.add_argument("--snapshot", type=Path, help="local copy of the pinned revision")
    parser.add_argument("--vocab-only", action="store_true", help="write the tokenizer metadata only")
    args = parser.parse_args()

    # --snapshot이 없으면 고정 리비전을 HF 캐시에서 찾거나 받는다(safetensors 약 14.5GB).
    snapshot = args.snapshot or Path(snapshot_download(REPO, revision=REVISION, allow_patterns=FILES))
    # 핵심 한 줄: 클래스 속성을 바꿔 끼우므로 변환기 안에서 AutoTokenizer.from_pretrained를 부르는 모든 곳이
    # 선언된 토크나이저를 받는다. 그러면 확인 문장의 해시가 llama.cpp에 등록된 'a.x-4.0'과 같아져 변환이
    # 멈추지 않는다.
    transformers.AutoTokenizer.from_pretrained = staticmethod(declared_tokenizer)
    llama = args.llama_cpp.resolve()
    # 변환기가 명령행으로 실행된 것처럼 sys.argv를 꾸민다. 출력 형식은 bf16으로 고정하고, 양자화(Q4_K_M)는
    # 다음 단계에서 llama-quantize로 한다.
    sys.argv = ["convert_hf_to_gguf.py", str(snapshot), "--outtype", "bf16", "--outfile", args.outfile]
    if args.vocab_only:
        sys.argv.append("--vocab-only")
    # runpy.run_path는 스크립트 폴더를 import 경로에 넣지 않는다. 변환기는 checkout 안의 다른 모듈을
    # import하므로 checkout 루트를 경로 맨 앞에 넣은 뒤 __main__으로 실행한다.
    sys.path.insert(0, str(llama))
    runpy.run_path(str(llama / "convert_hf_to_gguf.py"), run_name="__main__")


if __name__ == "__main__":
    main()
