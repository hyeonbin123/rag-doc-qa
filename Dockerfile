# Pin the Debian codename (trixie, what python:3.11-slim resolves to today) so the next Debian
# release can't slip in under a floating tag. uv is a fixed release copied from its official
# image, not whatever the install script serves on the day of the build.
FROM python:3.11-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /bin/
ENV PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Bake the models in before copying source, so code edits don't re-download them. The
# cross-encoders are only used with RETRIEVAL_MODE=rerank, but HF_HUB_OFFLINE below
# means they could not be fetched at runtime either.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5'); SentenceTransformer('intfloat/multilingual-e5-small')"
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')"
# The Korean model since v13 stage B, at the revision app/services/embedding.py pins (the app
# loads that commit, so it must be the snapshot cached here). e5-small above stays in the image
# so EMBEDDING_MODEL_NAME_KO can switch back without a rebuild.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('ibm-granite/granite-embedding-311m-multilingual-r2', revision='44399559930365213510b1ee2eb15ded83374f0e')"
# The models are cached above; without this, every startup still round-trips to the Hub.
ENV HF_HUB_OFFLINE=1

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
