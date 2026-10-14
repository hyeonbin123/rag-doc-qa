# [파일 역할] 평가 스크립트들(eval/run_retrieval_eval.py, run_answer_eval.py, run_judge.py,
# compare_judgments.py, generator_arms.py, embedding_latency.py, retrieval_runs.py)이 함께 쓰는 공통 도구.
# 질문셋 형식과 로더, 키워드 커버리지 지표, 리포트·문항별 기록(JSON/JSONL) 읽기·쓰기, 실행 시점의 git 커밋
# 기록을 모았다.
# [왜 필요한가] 모든 평가가 같은 질문셋 형식과 같은 파일 위치·인코딩을 쓰게 해서, 실행마다
# 리포트(eval/reports/)와 문항별 기록(eval/runs/)을 같은 방식으로 남기고 나중에 다시 판정·비교할 수 있게 한다.

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

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
