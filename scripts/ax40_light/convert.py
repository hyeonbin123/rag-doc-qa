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

import argparse
import runpy
import sys
from pathlib import Path

import transformers
from huggingface_hub import snapshot_download
from transformers import GPT2TokenizerFast

REPO = "skt/A.X-4.0-Light"
REVISION = "ba21c20ea1b31ded1ec3e2fb432335077dc4be98"
FILES = ["*.json", "*.safetensors", "merges.txt", "LICENSE", "README.md"]  # as downloaded for v13


def declared_tokenizer(path, *args, **kwargs):
    kwargs.pop("trust_remote_code", None)
    return GPT2TokenizerFast.from_pretrained(path, *args, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("outfile", help="the bf16 GGUF to write")
    parser.add_argument("--llama-cpp", required=True, type=Path, help="llama.cpp checkout (81bc6b8)")
    parser.add_argument("--snapshot", type=Path, help="local copy of the pinned revision")
    parser.add_argument("--vocab-only", action="store_true", help="write the tokenizer metadata only")
    args = parser.parse_args()

    snapshot = args.snapshot or Path(snapshot_download(REPO, revision=REVISION, allow_patterns=FILES))
    transformers.AutoTokenizer.from_pretrained = staticmethod(declared_tokenizer)
    llama = args.llama_cpp.resolve()
    sys.argv = ["convert_hf_to_gguf.py", str(snapshot), "--outtype", "bf16", "--outfile", args.outfile]
    if args.vocab_only:
        sys.argv.append("--vocab-only")
    sys.path.insert(0, str(llama))
    runpy.run_path(str(llama / "convert_hf_to_gguf.py"), run_name="__main__")


if __name__ == "__main__":
    main()
