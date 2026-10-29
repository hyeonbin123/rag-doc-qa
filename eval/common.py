# [파일 역할] 평가 스크립트들(eval/run_retrieval_eval.py, run_answer_eval.py, run_judge.py,
# compare_judgments.py, generator_arms.py, embedding_latency.py, retrieval_runs.py)이 함께 쓰는 공통 도구.
# 질문셋 형식과 로더, 키워드 커버리지 지표, 리포트·문항별 기록(JSON/JSONL) 읽기·쓰기, 실행 시점의 git 커밋
# 기록, 실행 기록의 출처 정보(질문셋 파일 해시, DB 코퍼스 요약), 다시 생성할 문항 목록(--ids-file) 형식을
# 모았다.
# [왜 필요한가] 모든 평가가 같은 질문셋 형식과 같은 파일 위치·인코딩을 쓰게 해서, 실행마다
# 리포트(eval/reports/)와 문항별 기록(eval/runs/)을 같은 방식으로 남기고 나중에 다시 판정·비교할 수 있게 한다.
# 출처 정보는 2026-10-29부터 기록한다. 그 전 기록에는 코퍼스·질문셋에 관해 DB 이름과 질문셋 파일 이름만 있어,
# 다른 원본 커밋으로 다시 적재한 DB나 고친 질문셋으로 잰 결과를 기록만으로 가려낼 수 없었다.

import hashlib
import json
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

# 코퍼스 요약 질의에 쓴다. 평가 스크립트가 넘기는 비동기 세션(AsyncSession)에 원시 SQL을 보낸다.
from sqlalchemy import text

# DATASET_PATH: --dataset을 주지 않을 때의 기본 질문셋(v1~v6의 30문항 테스트셋). REPORTS_DIR: 마크다운
# 리포트를 남기는 곳.
DATASET_PATH = Path(__file__).parent / "qa_dataset.jsonl"
REPORTS_DIR = Path(__file__).parent / "reports"
# RUNS_DIR: 답변 평가 실행의 문항별 기록(답과 그 근거 문맥, 판정 응답)을 두는 곳. 저장된 답으로 판정만 다시
# 돌릴 수 있게 한다.
RUNS_DIR = Path(__file__).parent / "runs"


# 질문셋 한 줄(JSONL 한 행)의 모양. expected_source_paths는 정답으로 인정하는 문서 경로들(Hit·MRR 계산),
# reference_answer는 판정 모델에게 주는 참고 답안, must_include_keywords는 키워드 커버리지 지표에 쓰는 핵심
# 단어들이다.
@dataclass
class EvalQuestion:
    id: str
    question: str
    expected_source_paths: list[str]
    reference_answer: str
    must_include_keywords: list[str] = field(default_factory=list)


# 답에 핵심 키워드가 몇 개나 들어 있는지의 비율(대소문자 무시, 부분 문자열 일치). 키워드가 없으면 1.0. LLM
# 판정 없이 바로 계산되는 거친 지표라, README '알려진 한계'에 적힌 대로 표현만 달라도 0이 될 수 있어 판정
# 점수와 함께 본다.
def keyword_coverage(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    lower_answer = answer.lower()
    hits = sum(1 for kw in keywords if kw.lower() in lower_answer)
    return hits / len(keywords)


# JSONL 질문셋을 EvalQuestion 목록으로 읽는다. 빈 줄은 건너뛴다. 모르는 필드가 있으면 EvalQuestion 생성에서
# TypeError가 나므로 질문셋 형식이 어긋나면 바로 드러난다.
def load_dataset(path: Path = DATASET_PATH) -> list[EvalQuestion]:
    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            questions.append(EvalQuestion(**data))
    return questions


# 마크다운 리포트를 eval/reports/에 쓴다(폴더가 없으면 만든다).
def write_report(filename: str, content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


# 문항별 기록을 JSONL로 쓴다. ensure_ascii=False로 한국어를 그대로 두고, newline="\n"으로 Windows에서도 줄
# 끝을 LF로 고정해 커밋된 기록이 OS마다 달라지지 않게 한다.
def write_jsonl(path: Path, records: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


# JSONL 파일을 dict 목록으로 읽는다(빈 줄 제외).
def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_json(path: Path) -> dict:
    """실행 하나의 메모 파일(JSON)을 읽는다. 파일이 없으면 {}."""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


# 실행 기록(.meta.json 등)을 들여쓰기 2칸 JSON으로 쓴다.
def write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# 지금 체크아웃된 커밋 해시. 실행 기록에 남겨 어떤 코드로 잰 결과인지 추적한다. git이 없거나 저장소
# 밖이면(또는 10초 안에 끝나지 않으면) None.
def git_commit() -> str | None:
    """지금 체크아웃된 커밋. 실행마다 함께 기록한다."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=10
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


# --- 실행 기록의 출처 정보 ---


# 질문셋 파일의 sha256(16진 64자). 두 평가 스크립트가 meta에 파일마다 남겨, 이름이 같은 질문셋이 나중에
# 고쳐졌는지를 기록만으로 가려낸다. 줄 끝은 LF로 맞춘 바이트로 센다: 이 저장소에는 .gitattributes가 없어
# Windows에서 core.autocrlf=true로 체크아웃하면 같은 커밋의 같은 파일도 CRLF가 되는데, 그때도 Linux(CI)와 같은
# 값이어야 기록끼리 비교할 수 있다(LF로 맞춘 바이트는 git이 저장한 내용과 같다). 질문 내용의 바뀜을 보려는
# 값이라 그 밖의 정규화(공백, JSON 키 순서)는 하지 않는다.
# 입력: 질문셋 경로. 출력: 소문자 16진 문자열. 파일이 없으면 OSError.
def dataset_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


# 평가 대상 DB의 코퍼스 요약: 문서의 원본 커밋(documents.source_commit_sha)별 문서 수, 마지막 적재 시각
# (max(fetched_at), ISO 8601), 언어별 청크 수. 두 평가 스크립트가 meta의 corpus에 남긴다.
# 왜: meta의 DB 이름과 vector_checks(저장 벡터가 지금 모델로 만든 것인지)만으로는 코퍼스가 같은지 알 수 없다.
# README의 적재 단계는 원본 커밋을 고를 수 있어, 같은 DB 이름으로 다른 커밋의 문서를 잰 실행이 같은 조건처럼
# 보일 수 있고, 일부만 다른 커밋으로 다시 적재한 DB는 여기서 커밋이 둘로 드러난다.
# 문서가 없으면 빈 사전과 None.
async def corpus_snapshot(db) -> dict:
    documents = (
        await db.execute(
            text(
                "SELECT source_commit_sha, count(*) AS documents, max(fetched_at) AS last_fetched_at "
                "FROM documents GROUP BY source_commit_sha ORDER BY source_commit_sha"
            )
        )
    ).all()
    chunks = (
        await db.execute(
            text("SELECT language, count(*) AS chunks FROM chunks GROUP BY language ORDER BY language")
        )
    ).all()
    last = max((row.last_fetched_at for row in documents), default=None)
    return {
        "documents_by_source_commit": {row.source_commit_sha: row.documents for row in documents},
        "last_fetched_at": last.isoformat() if last is not None else None,
        "chunks_by_language": {row.language: row.chunks for row in chunks},
    }


# 리포트 머리에 넣는 코퍼스 한 줄. 커밋은 앞 7자리로 줄이고 문서 수를 붙인다. 예:
# "- corpus: source commit 50113da (1024 documents); last fetched 2026-10-04T...; chunks en 3000, ko 2500".
# 리포트만 보고도 어느 원본 커밋의 코퍼스로 잰 결과인지 알 수 있게 한다. 입력은 corpus_snapshot의 결과.
def corpus_line(corpus: dict) -> str:
    commits = corpus.get("documents_by_source_commit") or {}
    if not commits:
        return "- corpus: no documents"
    label = "source commit" if len(commits) == 1 else "source commits"
    documents = ", ".join(
        f"{sha[:7]} ({count} {'document' if count == 1 else 'documents'})" for sha, count in commits.items()
    )
    by_language = corpus.get("chunks_by_language") or {}
    chunks = ", ".join(f"{language} {count}" for language, count in by_language.items()) or "-"
    fetched = corpus.get("last_fetched_at") or "-"
    return f"- corpus: {label} {documents}; last fetched {fetched}; chunks {chunks}"


# --- 다시 생성할 문항 목록(--ids-file) ---

# 한 줄에 '데이터셋 파일 이름<TAB>문항 id'. 데이터셋 이름은 검색·생성 기록의 dataset 필드와 같은 파일 이름(예:
# qa_test3b_ko.jsonl)이다. eval/refusal.py changed가 쓰고 eval/run_answer_eval.py --ids-file이 읽는다.
# 왜 데이터셋을 함께 적나: test3b 영어·한국어 셋처럼 서로 다른 셋이 같은 id를 쓰므로 id만으로는 어느 셋의
# 문항인지 알 수 없다. v15 I4에서는 id만 적은 목록 때문에, 한쪽 셋에서만 문맥이 바뀐 id가 문맥이 그대로인 다른
# 셋에서도 두 팔로 다시 생성됐다(docs/experiments.md v15 I4 test 결과).
IDS_FILE_SEPARATOR = "\t"


# (데이터셋 이름, id) 짝들을 ids 파일 내용(줄마다 LF)으로 만든다. 순서는 받은 순서 그대로다.
def format_ids_lines(pairs: Iterable[tuple[str, str]]) -> str:
    return "".join(f"{dataset}{IDS_FILE_SEPARATOR}{item_id}\n" for dataset, item_id in pairs)


# ids 파일에서 이 데이터셋(파일 이름) 줄의 id만 모은다. 빈 줄과 줄 끝 공백(CRLF 포함)은 무시한다. 탭으로 나눈
# 칸이 둘이 아니거나 빈 칸이 있는 줄은 ValueError: id만 적은 옛 형식(v15 I4 때의 파일)을 받으면 다른
# 데이터셋의 같은 id까지 다시 생성하게 되므로, 조용히 받지 않고 eval.refusal changed로 다시 만들게 한다.
def read_ids_file(path: Path, dataset: str) -> set[str]:
    wanted: set[str] = set()
    for number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(IDS_FILE_SEPARATOR)]
        if len(parts) != 2 or not all(parts):
            raise ValueError(
                f"{path}:{number}: expected '<dataset file name><TAB><question id>', got {raw!r}. "
                "An ids file with bare ids (one per line) does not say which dataset an id belongs to; "
                "write it again with `python -m eval.refusal changed`"
            )
        if parts[0] == dataset:
            wanted.add(parts[1])
    return wanted
