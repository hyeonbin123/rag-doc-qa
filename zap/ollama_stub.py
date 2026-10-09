"""A stand-in for Ollama's /api/chat, so a security scan can drive the API without a GPU.

An active scan sends hundreds of questions to POST /query/ask; with the real generator each one takes
seconds of GPU time. This answers at once with a fixed reply in the shape the app reads
(app/services/generation.py): plain text for the answer call, the citations JSON when the request
carries a `format` schema. The rest of the request path (auth, validation, language detection, the
embedding model, retrieval, the query log) runs for real. Standard library only.

    python ollama_stub.py [port]     # default 11434
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ANSWER = "Stand-in answer from the scan's stub generator."
CITATIONS = json.dumps({"citations": [{"chunk_number": 1}]})


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        try:
            request = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            request = {}
        if self.path != "/api/chat" or not isinstance(request, dict):
            self.send_error(404)
            return
        content = CITATIONS if request.get("format") is not None else ANSWER
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 11434
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
