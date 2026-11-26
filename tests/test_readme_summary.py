"""README 맨 위 '결과 요약' 절이 본문에 기록된 수치만 다시 적은 글인지 검증한다.

README.md와 저장소 안의 파일만 읽는다. DB·모델·네트워크는 쓰지 않는다.
"""

# [테스트 묶음] README.md의 '## 결과 요약' 절(요약 다섯 줄과 맺음 문장)을 본다. 이 절은 README 아래쪽의 표
# ('한눈에 보기', '핵심 결과')와 docs/experiments.md에 이미 기록된 수치를 맨 위에 다시 적은 글이다. 네
# 가지를 확인한다.
# - 이 절이 README의 첫 `## ` 제목이고 바로 다음 제목이 '## 한눈에 보기'인가(맨 위에 서는 자리).
# - 요약 줄(`- **`로 시작하는 줄)이 정확히 다섯 개인가.
# - 절 안의 숫자가 절 밖 본문에 그대로 있는가.
# - 절이 거는 링크('#핵심-결과', 'docs/experiments.md')가 가리키는 곳이 있는가.
# [왜 중요한가] 요약은 본문의 수치를 옮겨 적은 글이라, 옮기다 틀린 숫자는 기록에 없는 새 수치가 되어
# README 맨 위에 선다. 이 프로젝트는 단계마다 측정값을 기록하고 그 기록으로 채택을 판단하므로(README '설계
# 판단'의 '측정 규칙을 먼저 정함'), 맨 위의 수치도 기록과 어긋나면 안 된다. 그래서 요약의 숫자가 요약 밖
# 본문에 그대로 있는지를 기계로 본다.
# [한계] 값이 옳은지는 보지 않는다. 본문 어딘가에 같은 숫자가 있으면 통과하므로, 숫자를 엉뚱한 항목에 붙여
# 적은 경우(예: 영어 수치를 한국어 자리에)는 잡지 못한다. 값이 맞는지의 근거는 본문 기록과
# docs/experiments.md이고 이 시험은 그것을 대신하지 않는다. 한 자리 정수(1~9)는 본문 어디에나 있어 찾는
# 뜻이 없으므로 건너뛴다. 제목은 `## `로 시작하는 줄로만 가려내고 코드 울타리 안의 줄은 따로 가리지
# 않는다(지금 README에는 요약 절 앞뒤에 울타리가 없다).
# [격리] conftest.py의 DB 픽스처(db_engine·db_session·client·authed_client)를 받지 않는 동기 함수라 테스트
# DB에 접속하지 않는다.

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 요약 절과 그 바로 뒤 절의 제목 줄, 요약이 거는 두 링크의 대상. '#핵심-결과'는 GitHub이 제목
# '## 핵심 결과'에서 만드는 앵커(공백을 '-'로 바꾼 것)다.
SUMMARY_HEADING = "## 결과 요약"
OVERVIEW_HEADING = "## 한눈에 보기"
RESULTS_HEADING = "## 핵심 결과"
RESULTS_ANCHOR = "#핵심-결과"
EXPERIMENTS_DOC = "docs/experiments.md"

# 숫자 낱말: 소수(0.909)·분수 꼴(20/20)·쉼표가 든 수(1,535)를 한 낱말로 잡는다. 부호와 단위(%·초·점)는
# 낱말에 들지 않는다(예: '−13점'에서는 13, '25%'에서는 25). 글자 수가 MIN_NUMBER_LENGTH보다 짧은 낱말은
# 건너뛴다.
NUMBER = re.compile(r"\d+(?:[.,/]\d+)*")
MIN_NUMBER_LENGTH = 2


# README 전문. 텍스트 모드로 읽으므로 줄 끝은 \n으로 통일된다.
def read_readme() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


# README의 둘째 수준 제목 줄(`## `로 시작)을 나온 순서대로 모은다. 셋째 수준 제목(`### `)은 `## ` 뒤에
# 공백이 아니라 `#`이 와서 걸리지 않는다.
def level2_headings(readme: str) -> list[str]:
    return [line.rstrip() for line in readme.splitlines() if line.startswith("## ")]


# README 글을 (요약 절, 본문)으로 나눈다. 절은 `## 결과 요약` 제목 줄부터 다음 `## ` 제목 줄 앞까지이고,
# 본문은 그 구간을 뺀 나머지 전체(요약 앞의 제목·소개 문단과 요약 뒤의 모든 절)다. 요약이 자기 숫자를 자기
# 안에서 찾아 '있다'고 하는 일이 없도록 본문에서 절을 뺀다. 절이 없으면 단언 오류를 낸다. 없을 때 빈
# 구간을 검사하며 조용히 통과하는 시험이 되지 않게 하려는 것이다. 파일이 아니라 글을 받으므로, 틀리게 고친
# 글을 넣어 시험이 실제로 실패하는지도 파일 없이 볼 수 있다.
def split_summary(readme: str) -> tuple[str, str]:
    lines = readme.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.rstrip() == SUMMARY_HEADING]
    assert starts, f"README에 '{SUMMARY_HEADING}' 절이 없다"
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "".join(lines[start:end]), "".join(lines[:start] + lines[end:])


# 글에 나온 숫자 낱말을 나온 순서대로, 같은 낱말은 한 번만 돌려준다. 글자 수가 MIN_NUMBER_LENGTH보다 짧은
# 낱말(한 자리 정수)은 본문 어디에나 있어 찾는 뜻이 없으므로 뺀다.
def numbers_in(text: str) -> list[str]:
    found: list[str] = []
    for token in NUMBER.findall(text):
        if len(token) >= MIN_NUMBER_LENGTH and token not in found:
            found.append(token)
    return found


# body에 token이 '숫자 경계'를 지키고 나오는지 본다. 앞에 숫자·'.'·','·'/'가 붙어 있거나(10.88 안의 0.88),
# 뒤에 숫자나 '.'·','·'/'와 숫자가 이어지면(0.885 안의 0.88, 20/20 안의 20) 그 자리는 다른 숫자의 일부라서
# 센다고 하지 않는다. 문장 끝의 '.'이나 쉼표 뒤 공백(…20/20, 한국어…)은 숫자가 이어지지 않으므로 경계로
# 본다. 그냥 `token in body`로 찾으면 0.88이 0.885에 들어 있다는 이유로 통과해서, 옮겨 적다 한 자리를
# 빠뜨린 숫자를 놓친다.
def appears_in(token: str, body: str) -> bool:
    pattern = r"(?<![\d.,/])" + re.escape(token) + r"(?!\d|[.,/]\d)"
    return re.search(pattern, body) is not None


# 요약 절의 숫자 낱말 가운데 본문에 없는 것을 요약에 나온 순서대로 돌려준다. 모두 있으면 빈 목록이다.
def missing_numbers(section: str, body: str) -> list[str]:
    return [token for token in numbers_in(section) if not appears_in(token, body)]


# 요약이 README의 첫 `## ` 제목이고 바로 다음 `## ` 제목이 '한눈에 보기'인지 본다. 요약은 소개 문단과
# '한눈에 보기' 사이, 맨 위에 서야 하므로 다른 절이 앞서거나 사이에 끼면 실패한다. 절이 아예 없을 때도
# 여기서 실패한다.
def test_summary_is_the_first_section():
    headings = level2_headings(read_readme())

    assert SUMMARY_HEADING in headings, f"README에 '{SUMMARY_HEADING}' 절이 없다"
    assert headings[:2] == [SUMMARY_HEADING, OVERVIEW_HEADING], headings[:2]


# 요약 줄(`- **`로 시작하는 줄)이 정확히 다섯 개인지 본다. 줄 하나가 검색·답변·답이 없는 질문·응답
# 시간·판단 방식 가운데 하나를 맡으므로, 줄이 늘거나 줄면 요약이 길어지거나 한 영역이 빠진 것이다.
def test_summary_has_five_bullets():
    section, _ = split_summary(read_readme())
    bullets = [line for line in section.splitlines() if line.startswith("- **")]

    assert len(bullets) == 5, f"'- **'로 시작하는 줄이 {len(bullets)}개다(5개여야 한다)"


# 요약의 숫자가 모두 요약 밖 본문에 그대로 있는지 본다. 없는 숫자가 있으면 그 목록을 단언 메시지에 싣는다.
# 요약에서 숫자 낱말이 하나도 잡히지 않으면(절이 비었거나 숫자 규칙이 깨진 경우) 검사할 것이 없어 통과하는
# 시험이 되므로, 그것도 실패로 본다.
def test_summary_numbers_appear_in_the_body():
    section, body = split_summary(read_readme())
    missing = missing_numbers(section, body)

    assert numbers_in(section), "요약에서 숫자 낱말을 하나도 찾지 못했다(절이 비었거나 숫자 규칙이 깨졌다)"
    assert not missing, f"요약에는 있고 요약 밖 본문에는 없는 숫자 {len(missing)}개: {' '.join(missing)}"


# 요약이 거는 두 링크의 도착지가 있는지 본다. '(#핵심-결과)'는 README에 '## 핵심 결과' 제목이 있어야
# 앵커가 열리고, '(docs/experiments.md)'는 그 파일이 저장소에 있어야 한다. 제목을 바꾸거나 문서를 옮기면
# 링크가 조용히 끊기므로 여기서 잡는다.
def test_summary_links_point_at_existing_targets():
    readme = read_readme()
    section, _ = split_summary(readme)

    assert f"({RESULTS_ANCHOR})" in section, f"요약에 '({RESULTS_ANCHOR})' 링크가 없다"
    assert RESULTS_HEADING in level2_headings(readme), f"README에 '{RESULTS_HEADING}' 제목이 없다"
    assert f"({EXPERIMENTS_DOC})" in section, f"요약에 '({EXPERIMENTS_DOC})' 링크가 없다"
    assert (ROOT / EXPERIMENTS_DOC).is_file(), f"저장소에 {EXPERIMENTS_DOC} 파일이 없다"
