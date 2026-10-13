"""A stand-in for Ollama's /api/chat, so a security scan can drive the API without a GPU.

An active scan sends hundreds of questions to POST /query/ask; with the real generator each one takes
seconds of GPU time. This answers at once with a fixed reply in the shape the app reads
(app/services/generation.py): plain text for the answer call, the citations JSON when the request
carries a `format` schema. The rest of the request path (auth, validation, language detection, the
embedding model, retrieval, the query log) runs for real. Standard library only.

    python ollama_stub.py [port]     # default 11434
"""

# [파일 역할] OWASP ZAP 보안 스캔(DAST) 때 실제 Ollama 대신 띄우는 가짜 생성기 서버. zap/compose.scan.yml이 이
# 파일을 별도 컨테이너(ollama-stub)로 띄우고, API 컨테이너의 OLLAMA_BASE_URL을 이 서버로 돌린다.
# [왜 필요한가] 액티브 스캔은 /query/ask에 질문을 수백 번 보낸다(1차 스캔에서 657건). 실제 LLM이면 한 번에 몇
# 초씩 GPU를 쓰므로, 생성만 정해진 답으로 바꾸고 인증·입력 검증·언어 판별·임베딩·검색·질문 기록은 실제 코드가
# 돌게 한다(docs/security-scan.md '대상').
# [설계] 컨테이너 이미지에 따로 설치할 것이 없도록 표준 라이브러리만 쓴다.

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 답변 호출에 돌려줄 고정 문장과, 인용 호출에 돌려줄 JSON(1번 패시지를 인용). 앱의 Ollama 생성기는 답변을 자유
# 텍스트로, 인용을 숫자 스키마 JSON으로 두 번에 나눠 받으므로 두 형태를 모두 준비한다.
ANSWER = "Stand-in answer from the scan's stub generator."
CITATIONS = json.dumps({"citations": [{"chunk_number": 1}]})


# POST 요청만 처리하는 핸들러. /api/chat이 아닌 경로나 JSON 객체가 아닌 본문에는 404를 돌려준다.
class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        # 본문 길이만큼 읽어 JSON으로 푼다. 깨진 본문이면 빈 요청으로 보고 계속한다.
        length = int(self.headers.get("Content-Length") or 0)
        try:
            request = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            request = {}
        if self.path != "/api/chat" or not isinstance(request, dict):
            self.send_error(404)
            return
        # 앱은 인용 호출에만 format(JSON 스키마)을 넣으므로, format이 있으면 인용 JSON을, 없으면 답변 문장을
        # 돌려준다.
        content = CITATIONS if request.get("format") is not None else ANSWER
        # 앱이 읽는 Ollama 응답 필드(message.content, done_reason, 토큰 수)를 같은 모양으로 채운다. 토큰 수는
        # 의미가 없으므로 0으로 둔다.
        body = json.dumps(
            {
                "model": request.get("model", ""),
                "message": {"role": "assistant", "content": content},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 0,
                "eval_count": 0,
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    # 기본 포트는 Ollama와 같은 11434. 0.0.0.0에 바인드해 compose 네트워크의 API 컨테이너가 서비스 이름으로
    # 접속할 수 있게 하고, ThreadingHTTPServer로 동시에 오는 요청을 각각 스레드에서 처리한다.
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 11434
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
