# Test set 2: question draft

Written from a developer's point of view before looking up any answer document.
Answer documents are located afterwards; questions the corpus cannot answer get dropped.

1. My React app on localhost:3000 gets blocked when it calls my API on port 8000. How do I fix it?
2. How do I return a 404 error when the item someone asks for doesn't exist?
3. How can I load config values from a .env file?
4. How do I give a field in my request JSON a default value so clients can leave it out?
5. How do I accept several values for the same query parameter, like ?tag=a&tag=b?
6. How do I protect an endpoint so only logged-in users can call it?
7. How should I hash user passwords before saving them?
8. How can I log how long every request takes?
9. How can I stream a large file to the client instead of loading it all into memory?
10. How do I let the user download a file from an endpoint?
11. How do I redirect a request to another URL?
12. How do I add a description and a version number to my API docs?
13. How can I group my endpoints into sections in the docs page?
14. How do I get the client's IP address inside an endpoint?
15. How do I check that an email field in the request really is an email address?
16. How do I connect to a SQL database and create the tables when the app starts?
17. How do I write a test for my WebSocket endpoint?
18. How do I let users log in with a username and password and get back a token?
19. How do I make the login tokens expire after some time?
20. How do I upload several files in one request?
21. How do I receive a file and some form fields in the same request?
22. How do I make a query parameter required?
23. How do I restrict a path parameter to a fixed set of allowed values?
24. How do I leave fields that were never set out of the JSON response?
25. Should I run Gunicorn with several Uvicorn workers inside each container when I deploy to Kubernetes?
26. What's the difference between declaring my endpoint with def and with async def?
27. How do I catch my own exception type everywhere and turn it into a custom JSON error?
28. How do I change the error response FastAPI sends when the request data is invalid?
29. How do I put all the routes of one module under a prefix like /api/v1?
30. How do I push updates to the browser in real time over one open HTTP connection?
31. Can I use Python dataclasses instead of Pydantic models?
32. How do I check a string query parameter against a regular expression?
33. How do I accept a JSON body whose keys I don't know in advance?
34. How do I run a dependency for every endpoint in one router but not the whole app?
35. How do I return plain text instead of JSON?
36. My header is called X-Token. How do I read it when Python names can't contain a hyphen?
37. How do type hints like list[str] or str | None work in Python?
38. How do I add a custom logo to the generated OpenAPI docs?
39. How do I upgrade my app from Pydantic v1 to v2?
40. How do I send a custom header along with an error response?
41. How do I require an API key in a request header?
42. How do I serve a React single-page app build from my FastAPI app?
43. How do I stream a list of JSON objects one line at a time?
44. How do I add a field that the client sends but that should never be shown in the docs?

## After locating answers (work/locate_answers.py)

- Dropped Q41 (API key header): the corpus only has `APIKeyHeader` in an import list in
  reference/security/index.md, with no explanation of how to use it.
- Kept every other question's wording unchanged; 43 questions became eval/qa_test2.jsonl
  as t001-t043 in the same order (Q42-Q44 became t041-t043).
- Note: `ILIKE '%websocket_connect%'` also matched "websocket connect" in websockets.md
  because `_` is a single-character wildcard, so that hit was not a real answer for Q17.
