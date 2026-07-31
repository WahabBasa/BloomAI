# BloomAI — Active Recall Learning System

Upload a PDF, get practice questions generated from it, answer them in your own
words, and have those answers graded with written feedback.

The idea is active recall: you learn more by trying to retrieve something from
memory than by rereading it. The hard part of doing that with your own study
material is writing the questions, so this writes them for you — from your
document, not from a generic question bank — and then marks what you write back.

> **Live demo:** currently offline. The Azure resources behind the original
> hackathon deployment were torn down; the app is being redeployed and this
> section will link to it again when it is back. Everything below runs locally.

---

## How it works

```
  Vue 3 SPA                Django                        OpenAI
 ┌───────────┐  HTTP/JSON ┌────────────────┐            ┌──────────────────┐
 │ Upload    │───────────▶│ views.py       │            │ Question         │
 │ Practice  │            │  (plain JSON   │            │  generator agent │
 │ Results   │◀───────────│   views)       │            │ Answer           │
 └───────────┘            │       │        │───────────▶│  generator agent │
                          │       ▼        │            │ Grading agent    │
                          │ recall_service │            └──────────────────┘
                          │       │        │
                          │       ▼        │            ┌──────────────────┐
                          │ SQLite         │            │ PDFExtractorTool │
                          └────────────────┘            │  (PyPDF2, local) │
                                                        └──────────────────┘
```

Uploading a PDF runs the whole pipeline synchronously, in the request:

1. `PDFExtractorTool` pulls text and metadata out of the file with PyPDF2. This
   is a local tool, not a model call.
2. The **question generator agent** reads the extracted text and returns five
   active recall questions.
3. The **answer generator agent** reads the same text plus those questions and
   returns one reference explanation per question.
4. Both are saved, and the browser is sent to the practice view.

Answering a question posts it to the backend, where the **grading agent**
compares it against the reference explanation and returns a score of 0, 0.5 or
1 — stored as 0, 50 or 100 — together with feedback explaining the score.

Three agents, one tool. All three agents run `gpt-4o-mini`.

### Stack

| | |
|---|---|
| Frontend | Vue 3, Pinia, Vue Router, Vite |
| Backend | Django 5.2 — plain function-based views returning `JsonResponse`. There is no Django REST Framework in this project. |
| Agents | [atomic-agents](https://github.com/BrainBlend-AI/atomic-agents) 1.1.0 + [instructor](https://github.com/instructor-ai/instructor), against OpenAI `gpt-4o-mini` |
| PDF | PyPDF2 |
| Database | SQLite. Nothing in the code configures Postgres. |

---

## Running it locally

**Prerequisites:** Python 3.12, Node 18+, and an
[OpenAI API key](https://platform.openai.com/api-keys).

### Backend

`requirements.txt` is at the **repository root**, not in `Backend/`.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp Backend/.env.example Backend/.env   # then edit it, see below
cd Backend
python manage.py migrate
python manage.py runserver             # http://localhost:8000
```

`Backend/.env` — copy from `Backend/.env.example`:

| Variable | Required | Notes |
|---|---|---|
| `OPENAI_API_KEY` | To process documents | Needed only when a request actually calls a model. `manage.py migrate`, `check`, `test` and friends all run without it. |
| `DJANGO_DEBUG` | For local dev | `True` puts `localhost` in `ALLOWED_HOSTS` and `http://localhost:5173` in the CORS allowlist. Without it a local server answers every request with HTTP 400. Defaults to `False`. |
| `DJANGO_SECRET_KEY` | For deployment | Falls back to the insecure development key if unset. |

### Frontend

```bash
cd Frontend
npm install
npm run dev                      # http://localhost:5173
```

No frontend configuration is needed for local development: the API service
defaults to the relative path `/api`, and the Vite dev server proxies that to
`http://localhost:8000` (see `vite.config.js`). To point a deployed frontend at
a backend on another origin, set `VITE_API_BASE_URL` — see
`Frontend/.env.example`.

### Try it

Open http://localhost:5173, upload a PDF, wait for the questions to generate
(a few seconds — three model calls happen in that one request), answer them,
and finish the test to see your marks, the grader's feedback, and the reference
explanations.

`python manage.py createsuperuser` plus http://localhost:8000/admin/ gives you a
look at the stored documents, questions and answers.

### Tests

```bash
cd Backend
python manage.py test main_system
```

Every agent factory and the PDF extractor are stubbed, so the suite makes no
network calls and needs no API key. It covers score conversion (0 / 0.5 / 1 →
0 / 50 / 100), UUID validation, the upload rules, orphan cleanup when
generation fails, and that internal error detail stays out of API responses.

---

## API

All endpoints return JSON. There is no authentication.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/documents/upload/` | Upload a PDF (multipart, field `file`). Extracts text, generates questions and explanations, returns `document_id` and `questions_count`. |
| `GET` | `/api/documents/` | List documents with title, upload time, page count, question count. |
| `GET` | `/api/documents/<document_id>/` | One document plus its questions. |
| `GET` | `/api/documents/<document_id>/questions/` | Questions for a document, each with its explanation and the most recent mark and feedback. |
| `GET` | `/api/questions/<question_id>/` | One question plus every answer submitted to it. |
| `POST` | `/api/questions/<question_id>/answer/` | Submit `{"answer": "..."}`. Grades it and returns `mark` (0/50/100) and `feedback`. |
| `GET` | `/api/answers/<answer_id>/` | One graded answer. |

Malformed UUIDs return 400, unknown IDs 404, wrong methods 405. Errors are
logged server-side and reported to the client generically.

---

## Layout

```
requirements.txt              # backend dependencies (repo root)
Backend/
  manage.py
  recall_system/
    settings.py               # loads Backend/.env; DEBUG from DJANGO_DEBUG
    urls.py                   # every route, all under /api/
  main_system/
    views.py                  # the JSON endpoints
    models.py                 # Document, Question, UserAnswer
    admin.py
    services/recall_service.py   # orchestrates tool + agents
    agents/
      llm_client.py           # lazily built, shared OpenAI client
      agents/
        qgen_agent.py         # question generator
        agen_agent.py         # answer/explanation generator
        g_agent.py            # grader
    tools/content_extractor.py   # PDFExtractorTool (PyPDF2)
Frontend/
  src/
    views/                    # UploadView, TestView, ResultsView
    components/               # UploadForm, QuestionCard, ResultItem, ...
    stores/testStore.js       # Pinia store
    services/apiService.js    # fetch wrapper
```

### Data model

```python
class Document:
    document_id, title, file_path, content, page_count, author,
    created_date, uploaded_at

class Question:
    question_id, document (FK), question_text, answer_explanation, created_at

class UserAnswer:
    answer_id, question (FK), user_answer,
    mark,        # 0, 50 or 100 — null until graded
    feedback,    # the grader's written explanation of the mark
    submitted_at
```

### Agents

Each agent is built **per request** by a factory —
`build_question_agent`, `build_answer_agent`, `build_grading_agent` — called
inside `process_pdf` or `grade_answer`.

This matters. `atomic_agents.BaseAgent` accumulates every input and response in
an `AgentMemory` and replays the whole history on each subsequent call. As
module-level singletons the agents re-sent every document they had ever seen on
every new request: token cost grew with process uptime, each document was
generated in the context of the last, and concurrent requests raced on shared
mutable context providers. Building them per request means each call starts
with empty memory and its own context.

The OpenAI client is the one shared piece — it holds a connection pool but no
per-request state, and it is constructed lazily so importing the agents does
not require an API key.

Each agent takes its bulk context (the document, or the answer being graded)
through an atomic-agents *context provider*, which lands in the system prompt,
and its request through a Pydantic input schema. Outputs are Pydantic schemas
too, so instructor validates the model's JSON before it reaches the database.

---

## Notes and limitations

- Question generation is fixed at five questions per document
  (`DEFAULT_QUESTION_COUNT` in `recall_service.py`).
- Upload is synchronous: the HTTP request is held open for three model calls.
  Large PDFs will feel slow and can hit a proxy timeout. A task queue is the
  obvious next step.
- There are no user accounts. Every document is visible to everyone, and the
  browser tracks "your" current document in `localStorage`.
- PDF only. Scanned PDFs with no text layer extract nothing — there is no OCR.
- No rate limiting or upload size cap, so anyone who can reach the server can
  spend your OpenAI credit.

---

## Deployment

Both GitHub Actions workflows in `.github/workflows/` target Azure resources
that no longer exist, so they are set to `workflow_dispatch` (manual) only. To
redeploy: re-create the App Service and Static Web App, restore the `push`
triggers, and set `OPENAI_API_KEY` and `DJANGO_SECRET_KEY` in the App Service
configuration. The Azure hostnames are still in `ALLOWED_HOSTS` and
`CORS_ALLOWED_ORIGINS`.

---

## License

MIT — see [LICENSE](LICENSE).
