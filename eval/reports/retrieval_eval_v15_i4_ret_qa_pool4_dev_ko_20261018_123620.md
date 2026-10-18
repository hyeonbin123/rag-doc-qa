# Retrieval eval report (v15_i4_ret_qa_pool4_dev_ko)

- date: 2026-10-18T12:36:05.927005+00:00
- embedding models: en BAAI/bge-small-en-v1.5, ko ibm-granite/granite-embedding-311m-multilingual-r2
- database: ragdb
- top_k: 10
- retrieval mode: dense
- search: as planned; dense plan: ko Sort > Seq Scan on chunks c > Seq Scan on documents d
- score floor: ko 0.0
- stored vectors checked: ko chunks vs ibm-granite/granite-embedding-311m-multilingual-r2@44399559930365213510b1ee2eb15ded83374f0e:dim384 (min cosine 1.0)
- dataset: qa_pool4_dev_ko.jsonl
- questions: 40
- hit: a chunk of an expected page, in any translation
- short: questions with fewer than 5 results (the score floor cut the rest)
- latency: retrieval only (after the query embedding), this machine's CPU

## Aggregate metrics

| set | questions | Hit@3 | Hit@5 | Hit@10 | MRR | short | latency p50 (ms) | latency p95 (ms) |
|---|---|---|---|---|---|---|---|---|
| all | 40 | 0.95 | 0.97 | 0.97 | 0.915 | 0 | 7 | 8 |

## Per-question

| id | hit@3 | hit@5 | hit@10 | RR | results | ms | question |
|---|---|---|---|---|---|---|---|
| k4010 | True | True | True | 1.00 | 10 | 10 | 경로 매개변수를 int로 선언했는데 문자열 넣으면 어떤 에러 응답이 나와요? |
| k4011 | True | True | True | 1.00 | 10 | 7 | fastapi dev main.py 랑 fastapi run main.py 차이가 뭐임? 운영에서 --reload 켜면 안 되는 이유도 궁금 |
| k4017 | True | True | True | 1.00 | 10 | 7 | 바디에 모델 하나밖에 없는데 {"item": {...}} 처럼 키로 한 번 감싸서 받고 싶으면 Body(embed=True) 쓰면 돼요? |
| k4019 | True | True | True | 1.00 | 10 | 7 | 422 에러 응답 포맷을 회사 표준 형식으로 바꾸고 싶어요. RequestValidationError 핸들러를 오버라이드하면 되나요? |
| k4020 | True | True | True | 1.00 | 10 | 7 | APIRouter(prefix=, tags=, dependencies=)에 주는 거랑 app.include_router()에서 주는 거랑 무슨 차이예요? |
| k4021 | True | True | True | 1.00 | 10 | 8 | main.py 맨 아래에 if __name__ == "__main__": uvicorn.run(app) 넣으면 디버거로 실행할 수 있다던데 그게 무슨 뜻이에요? |
| k4027 | True | True | True | 1.00 | 10 | 7 | 로그인 성공하면 응답에 쿠키를 심고 싶은데 Response 파라미터 받아서 set_cookie 하면 되나요? 커스텀 헤더도 같은 방식인가요? |
| k4032 | True | True | True | 1.00 | 10 | 7 | Swagger에 요청 바디 예시 넣고 싶은데 json_schema_extra, Field(examples=...), openapi_examples 셋이 뭐가 다른가요? |
| k4033 | True | True | True | 1.00 | 10 | 8 | 테스트에서 lifespan 시작/종료 코드도 실행되게 하려면 with TestClient(app) as client: 로 써야 하나요? |
| k4034 | True | True | True | 1.00 | 10 | 7 | 경로 매개변수 값을 몇 개로 제한하고 싶은데 str 상속한 Enum 쓰면 docs에도 선택지로 나오나요? |
| k4037 | True | True | True | 1.00 | 10 | 7 | yield 의존성에서 yield 뒤 코드는 응답 보내기 전에 돌아요, 후에 돌아요? 버전에 따라 바뀌었다는 얘기가 있던데 |
| k4039 | True | True | True | 1.00 | 10 | 8 | 모든 요청의 처리 시간을 X-Process-Time 응답 헤더로 넣어주는 미들웨어 만들고 싶어요 |
| k4040 | True | True | True | 1.00 | 10 | 7 | 중첩 모델이나 list[Image], set[str] 같은 필드는 어떻게 선언해요? |
| k4041 | True | True | True | 1.00 | 10 | 7 | 클라이언트 IP 알아내려면 Request 객체를 직접 받아서 request.client.host 쓰면 되나요? |
| k4042 | True | True | True | 1.00 | 10 | 7 | 운영 환경에선 /docs 를 꺼두고 싶어요. 환경 변수 보고 openapi_url 을 None 으로 주는 방식이면 되나요? |
| k4044 | True | True | True | 1.00 | 10 | 7 | JWT 발급할 때 문서에서는 어떤 라이브러리를 쓰고, SECRET_KEY는 어떻게 생성하라고 하나요? |
| k4048 | True | True | True | 1.00 | 10 | 7 | 서브 의존성 구조에서 같은 의존성이 여러 군데서 쓰이면 요청당 한 번만 호출되나요? 캐싱 끄는 옵션도 있어요? |
| k4050 | True | True | True | 1.00 | 10 | 7 | Swagger UI 구문 강조를 끄거나 deepLinking 같은 옵션을 바꾸려면 swagger_ui_parameters 쓰면 되나요? |
| k4052 | True | True | True | 1.00 | 10 | 7 | UserIn, UserOut, UserInDB 처럼 모델 여러 개 만들 때 필드 중복 줄이려면 상속 쓰는 게 맞나요? |
| k4053 | True | True | True | 0.50 | 10 | 7 | 파일 다운로드 엔드포인트에서 FileResponse로 filename 지정해서 내려주는 방법 알려주세요 |
| k4054 | True | True | True | 1.00 | 10 | 7 | fastapi의 HTTPException이랑 starlette의 HTTPException 차이가 있나요? 예외 핸들러는 어느 쪽 기준으로 등록해야 해요? |
| k4059 | True | True | True | 1.00 | 10 | 7 | Strawberry 같은 GraphQL 라이브러리를 FastAPI에 붙여서 쓸 수 있나요? |
| k4060 | True | True | True | 0.33 | 10 | 7 | allow_origins=["*"]에 allow_credentials=True 같이 줬는데 쿠키 인증이 안 돼요. 와일드카드 쓰면 안 되는 건가요? |
| k4061 | True | True | True | 1.00 | 10 | 7 | Path()에 ge=1, le=1000 같은 숫자 범위 검증 거는 법 |
| k4063 | True | True | True | 1.00 | 10 | 7 | tiangolo/uvicorn-gunicorn-fastapi 베이스 이미지 아직 써도 되나요? deprecated 됐다는 말이 있던데 |
| k4065 | True | True | True | 1.00 | 10 | 7 | 쿠키 값 읽으려면 Cookie() 써야 하죠? 그냥 str 파라미터로 선언하면 쿼리로 인식되는 거 맞나요? |
| k4066 | True | True | True | 1.00 | 10 | 7 | 초기화할 때 인자 받는 의존성(예: 특정 문자열 포함 여부 체크)을 __call__ 있는 클래스 인스턴스로 만드는 방법 |
| k4067 | True | True | True | 1.00 | 10 | 7 | HTMLResponse로 HTML 직접 반환할 때 response_class로 지정해야 docs에 text/html 로 표시되나요? |
| k4072 | True | True | True | 1.00 | 10 | 7 | Pydantic v2 쓰니까 docs에 같은 모델이 Item-Input, Item-Output 두 개로 나와요. 하나로 합칠 수 있나요? |
| k4073 | True | True | True | 1.00 | 10 | 8 | 기존 Flask 앱을 FastAPI 안에 붙여서 같이 돌리고 싶어요. WSGIMiddleware 쓰면 되나요? |
| k4075 | False | False | False | 0.00 | 10 | 7 | 앱 전체 엔드포인트에 X-Key 헤더 검사 의존성을 한 번에 걸고 싶어요. FastAPI(dependencies=[...]) 쓰면 되나? |
| k4076 | True | True | True | 1.00 | 10 | 7 | Pydantic 모델 대신 dataclasses로 바디나 response_model 선언해도 동작해요? |
| k4077 | False | True | True | 0.25 | 10 | 7 | POST 바디를 BaseModel로 받을 때 필드에 기본값 주면 선택 필드 되는 거 맞죠? |
| k4080 | True | True | True | 1.00 | 10 | 7 | HTTPSRedirectMiddleware, TrustedHostMiddleware, GZipMiddleware 각각 어떤 상황에서 쓰는 건가요? |
| k4085 | True | True | True | 1.00 | 10 | 7 | 우리 API가 외부로 보내는 웹훅 요청 형식을 OpenAPI 문서에 표시하려면 app.webhooks 쓰나요? callbacks랑은 뭐가 달라요? |
| k4092 | True | True | True | 1.00 | 10 | 8 | 헤더 여러 개를 Pydantic 모델로 묶어서 Header()로 한 번에 받을 수 있다던데 어떻게 써요? |
| k4097 | True | True | True | 1.00 | 10 | 7 | Jinja2Templates로 HTML 렌더링할 때 템플릿 안에서 url_for로 static 파일 경로 만드는 법 |
| k4107 | True | True | True | 0.50 | 10 | 7 | 엔드포인트에 tags, summary 붙이고 docstring을 마크다운 설명으로 쓰는 방법 |
| k4109 | True | True | True | 1.00 | 10 | 7 | 반환값은 안 쓰고 검증만 하는 의존성은 데코레이터에 dependencies=[Depends(verify_token)]로 넣으면 되죠? |
| k4110 | True | True | True | 1.00 | 10 | 7 | 직접 만든 UnicornException을 던지면 418 응답으로 바꿔주는 예외 핸들러 등록하는 법 |