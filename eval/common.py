import json
from dataclasses import dataclass, field
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "qa_dataset.jsonl"
REPORTS_DIR = Path(__file__).parent / "reports"


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
