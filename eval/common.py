import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "qa_dataset.jsonl"
REPORTS_DIR = Path(__file__).parent / "reports"
# Per-item records of answer-eval runs (answers with their passages, judge replies), so a
# judge can be rerun on stored answers.
RUNS_DIR = Path(__file__).parent / "runs"


@dataclass
class EvalQuestion:
    id: str
    question: str
    expected_source_paths: list[str]
    reference_answer: str
    must_include_keywords: list[str] = field(default_factory=list)


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


def write_report(filename: str, content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


def write_jsonl(path: Path, records: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read_json(path: Path) -> dict:
    """A run's notes file, or {} when there is none."""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def git_commit() -> str | None:
    """The checked-out commit, recorded with each run."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, timeout=10
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
