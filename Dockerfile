# Pin the Debian codename (trixie, what python:3.11-slim resolves to today) so the next Debian
# release can't slip in under a floating tag. uv is a fixed release copied from its official
# image, not whatever the install script serves on the day of the build.
FROM python:3.11-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /bin/
ENV PATH="/app/.venv/bin:${PATH}"

# 서버는 root가 아닌 app 사용자(uid 10001)로 돈다(맨 아래 USER). 이 사용자가 쓸 수 있는 곳은 홈(/home/app)과 모델
# 캐시(/opt/hf)뿐이고, 코드와 가상환경(/app)은 root 소유로 남긴다. 서버는 실행 중에 /app 아래에 아무것도 쓰지 않으므로
# (질문 기록·사용자는 DB에, tiktoken 인코딩 캐시는 /tmp에 쓴다) 이렇게 두면 프로세스가 뚫려도 자기 코드와 의존성을
# 고쳐 쓸 수 없다. uid를 10001로 두는 것은 호스트의 보통 사용자 uid(1000 부근)와 겹치지 않게 하려는 관례다.
RUN useradd --create-home --uid 10001 app \
 && install -d -o app -g app /opt/hf

# 모델 캐시 위치. 기본값(~/.cache/huggingface)은 사용자마다 달라지므로, 빌드 때 받는 사용자와 실행하는 사용자가 같은
# 캐시를 보도록 고정 경로로 둔다.
ENV HF_HOME=/opt/hf

# 모델 층. 의존성(lock) 층보다 앞에 두어, uv.lock이나 pyproject.toml만 바꾼 재빌드가 모델 약 1.8GB를 다시 받지 않게
# 한다(층 캐시는 앞 층이 그대로일 때만 쓰인다). 그래서 앱의 가상환경 없이 내려받기 도구(huggingface-hub의 hf CLI)만
# uvx로 잠깐 받아 쓴다. --no-cache라 도구 환경은 층에 남지 않는다. 도구의 huggingface-hub·hf-xet 판은 uv.lock의 판과
# 같게 맞춰, 캐시를 쓰는 쪽(빌드)과 읽는 쪽(실행)의 판이 같게 한다(tests/test_docker_image.py가 확인한다).
# - 리비전: 앱이 부르는 커밋과 같아야 한다(app/services/embedding.py의 EMBEDDING_MODELS, app/services/reranking.py의
#   RERANKER_REVISIONS, 같은 테스트가 확인). 커밋 해시로 받으면 refs/main이 생기지 않으므로, 리비전 없이 부르는
#   코드는 아래 HF_HUB_OFFLINE에서 모델을 찾지 못한다.
# - 파일 목록: sentence-transformers가 모델을 올릴 때 읽는 파일만 받는다. 2026-10-30 전 이미지(모델을
#   SentenceTransformer·CrossEncoder로 받던 때)의 캐시에 있던 파일과 같은 목록이다. 저장소 전체를 받으면 쓰지 않는
#   ONNX·OpenVINO 변환본이나 pytorch_model.bin 사본까지 들어온다. 목록의 파일이 저장소에 없으면 hf download는 오류
#   없이 건너뛰므로, 목록을 바꿀 때는 --dry-run으로 받을 파일 수를 먼저 확인한다.
# - 모델마다 층을 나눠 docker image history로 크기를 볼 수 있게 하고, 뒤쪽 모델만 바꿀 때 앞 층을 다시 쓰게 한다.
# - 받는 동안만 app 사용자로 바꿔 캐시가 처음부터 app 소유가 되게 한다. 나중에 chown -R 하면 같은 1.8GB가 층에 한 번
#   더 쌓인다.
# - HF_HUB_DISABLE_XET=1: Xet 저장소의 파일도 Xet 전용 클라이언트(hf-xet) 대신 보통 HTTP로 받는다. 2026-10-30 빌드에서
#   hf-xet로 받던 bge model.safetensors(133MB)가 7분 넘게 진행 없이 멈췄고(2026-10-15 빌드에서도 Xet 내려받기 오류가
#   한 번 있었다), 같은 파일을 같은 PC에서 HTTP로 받으면 3초였다. 받은 파일이 같다는 것은 sha256으로 확인했다.
ARG HF_CLI="env HF_HUB_DISABLE_XET=1 uvx --no-cache --python /usr/local/bin/python3 --from huggingface-hub==1.31.0 --with hf-xet==1.6.0 hf"
USER app
# 영어 임베딩(기본, v8부터)
RUN $HF_CLI download BAAI/bge-small-en-v1.5 --revision 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a \
      modules.json config_sentence_transformers.json sentence_bert_config.json 1_Pooling/config.json \
      config.json model.safetensors tokenizer.json tokenizer_config.json special_tokens_map.json vocab.txt README.md
# 한국어 임베딩 e5-small(v13 단계 B 전까지의 기본). EMBEDDING_MODEL_NAME_KO만 바꿔 다시 빌드하지 않고 되돌릴 수 있게 남긴다.
RUN $HF_CLI download intfloat/multilingual-e5-small --revision 614241f622f53c4eeff9890bdc4f31cfecc418b3 \
      modules.json sentence_bert_config.json 1_Pooling/config.json config.json model.safetensors \
      sentencepiece.bpe.model tokenizer.json tokenizer_config.json special_tokens_map.json README.md
# 한국어 임베딩(기본, v13 단계 B부터)
RUN $HF_CLI download ibm-granite/granite-embedding-311m-multilingual-r2 --revision 44399559930365213510b1ee2eb15ded83374f0e \
      modules.json config_sentence_transformers.json sentence_bert_config.json 1_Pooling/config.json \
      config.json model.safetensors tokenizer.json tokenizer_config.json special_tokens_map.json README.md
# cross-encoder 두 개는 RETRIEVAL_MODE=rerank에서만 쓰지만, 아래 HF_HUB_OFFLINE 때문에 실행 중에 받을 수도 없어 미리
# 넣는다. 영어 모델 저장소는 허브에서 ms-marco-MiniLM-L6-v2로 이름이 바뀌었고 옛 이름으로 받으면 새 이름으로 넘겨진다.
# 캐시 폴더 이름은 요청한 옛 이름을 따르므로 설정값(RERANKER_MODEL_NAME)과 맞는다.
RUN $HF_CLI download cross-encoder/ms-marco-MiniLM-L-6-v2 --revision 233902d25c440f23af6f7d6e94d2946bac0bee0a \
      config.json model.safetensors tokenizer.json tokenizer_config.json special_tokens_map.json vocab.txt
RUN $HF_CLI download cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 --revision 1427fd652930e4ba29e8149678df786c240d8825 \
      config.json model.safetensors sentencepiece.bpe.model tokenizer.json tokenizer_config.json special_tokens_map.json
USER root
# The models are cached above; without this, every startup still round-trips to the Hub.
ENV HF_HUB_OFFLINE=1

WORKDIR /app

# 의존성 층. --compile-bytecode로 가상환경의 .py를 빌드 때 미리 컴파일한다. 가상환경은 root 소유라 실행 사용자(app)가
# __pycache__를 쓸 수 없으므로, 미리 컴파일하지 않으면 컨테이너를 띄울 때마다 torch·transformers 같은 큰 패키지를
# 메모리에서 다시 컴파일해 시작이 느려진다(전에는 root가 빌드 중 모델을 받으며 import한 모듈의 .pyc가 층에 남았다).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --compile-bytecode

COPY . .

USER app

EXPOSE 8000

# exec: 마이그레이션이 끝나면 셸을 uvicorn으로 바꿔 uvicorn이 PID 1이 되게 한다. docker stop의 SIGTERM이
# uvicorn에 바로 가서 요청을 마무리하고 정상 종료한다(exec가 없으면 sh가 신호를 넘기지 않아 10초 뒤 SIGKILL로
# 끝났다).
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
