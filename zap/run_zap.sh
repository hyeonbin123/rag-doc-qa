#!/usr/bin/env bash
# ZAP 릴리스(크로스플랫폼 패키지, Java 17 이상)로 zap/automation.yaml을 스캔 대상(docs/security-scan.md)에 대고
# 실행한다. 스캔 대상은 zap/compose.scan.yml로 띄운 api 이미지다.
#
#   ZAP_DIR=<zap-2.17.0.jar가 있는 폴더> ACCESS_TOKEN=<스캔하는 DB에 있는 사용자의 접근 토큰> \
#     zap/run_zap.sh <name>
#
# 대상은 TARGET(기본 http://127.0.0.1:8000)에서 이미 실행 중이어야 한다. 리포트 <name>.json과 <name>.md, ZAP
# 로그, 새로 만든 ZAP 홈 폴더는 work/zap/<name>/에 생긴다. 출력은 파이프로 보내지 않고 파일로만 받는다.
# [파일 역할] 서비스 코드를 바꾼 뒤 실행하는 OWASP ZAP 스캔 실행기. Docker 없이 ZAP 공식 크로스플랫폼
# 패키지(jar)를 Java로 직접 돌리고, 스캔 내용은 zap/automation.yaml 하나에 정한다(docs/security-scan.md).
# [왜 이렇게 하나] 위 설명대로 스캐너 출력은 파이프가 아니라 파일로만 받는다. 차수마다 리포트·로그·ZAP 홈
# 폴더를 저장소의 work/zap/<이름>/에 새로 만들어 이전 실행과 섞이지 않게 한다.
# [흐름] 인자·환경 변수 확인 → 출력 폴더 준비 → ZAP이 읽을 환경 변수(대상, 인증 헤더, 리포트 위치) 내보내기 →
# ZAP 실행 → 종료 코드 전달.
# set -euo pipefail: 명령 실패, 정의되지 않은 변수, 파이프 중간 실패에서 바로 멈춘다.

set -euo pipefail

# 스캔 이름(출력 폴더 이름)은 필수다. ZAP_DIR(jar 위치)와 ACCESS_TOKEN(스캔 대상 DB 사본에만 있는 사용자의
# 토큰)이 없으면 사용법을 알리고 멈춘다. root는 이 스크립트가 있는 zap/의 상위, 즉 저장소 루트다.
name=${1:?usage: zap/run_zap.sh <name>}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${ZAP_DIR:?set ZAP_DIR to the folder that holds zap-<version>.jar}"
: "${ACCESS_TOKEN:?set ACCESS_TOKEN to an access token from POST /auth/login on the target}"

# 경로를 절대 경로로 바꾸고, Git Bash(Windows)에서는 cygpath -m으로 Java가 이해하는 'C:/...' 형태로 바꾼다.
# Linux처럼 cygpath가 없으면 절대 경로 그대로 쓴다. 상대 경로를 넘기지 않는 이유는 ZAP이 상대 경로를 작업
# 폴더가 아니라 계획 파일의 폴더(zap/) 기준으로 풀기 때문이다.
native() {
  local abs
  abs=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
  if command -v cygpath > /dev/null; then cygpath -m "$abs"; else printf '%s\n' "$abs"; fi
}

# 같은 이름의 폴더가 이미 있으면 이전 차수의 결과를 덮어쓰지 않도록 멈춘다. ZAP_DIR에서 zap-*.jar를 찾지
# 못해도 멈춘다.
out=$root/work/zap/$name
if [ -e "$out" ]; then
  echo "$out exists: pick another name" >&2
  exit 1
fi
jars=("$ZAP_DIR"/zap-*.jar)
[ -f "${jars[0]}" ] || { echo "no zap-*.jar in $ZAP_DIR" >&2; exit 1; }
mkdir -p "$out"

# automation.yaml이 환경 변수로 읽는 값들. TARGET은 기본 로컬 API(8000). host는 TARGET에서 스킴을 떼고,
# 아래에서 포트·경로까지 떼어 호스트 이름만 인증 헤더의 적용 범위로 넘긴다(다른 호스트로 가는 요청에는 토큰이
# 붙지 않게).
export TARGET=${TARGET:-http://127.0.0.1:8000}
host=${TARGET#*://}
# ZAP은 대상 호스트로 가는 모든 요청에 이 헤더를 붙인다(zap/automation.yaml 참고).
export ZAP_AUTH_HEADER=Authorization ZAP_AUTH_HEADER_VALUE="Bearer $ACCESS_TOKEN" ZAP_AUTH_HEADER_SITE=${host%%[:/]*}
export REPORT_DIR REPORT_NAME=$name
REPORT_DIR=$(native "$out")

# set -e 상태에서 ZAP이 0이 아닌 코드로 끝나도 스크립트가 바로 멈추지 않도록 '|| status=$?'로 종료 코드를 받아
# 두고, 결과 위치를 알린 뒤 같은 코드로 끝낸다.
# ZAP 옵션: -Xmx2g 힙 2GB, -cmd 화면 없이 실행, -notel 원격 측정 끔, -dir 이번 차수 전용 홈 폴더, 업데이트
# 확인 끔, -autorun으로 계획 파일 실행. 표준 출력·오류는 모두 zap.log 파일로만 보낸다.
status=0
java -Xmx2g -jar "$(native "${jars[0]}")" -cmd -notel -dir "$(native "$out/home")" \
  -config start.checkForUpdates=false -autorun "$(native "$root/zap/automation.yaml")" \
  > "$out/zap.log" 2>&1 || status=$?
echo "ZAP exit status $status, reports and log in $out"
exit "$status"
