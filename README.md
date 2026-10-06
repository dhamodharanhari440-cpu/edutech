<<<<<<< HEAD
# EduGenie — AI-Powered Learning Assistant

EduGenie is a full-stack, AI-powered educational web application built with
**FastAPI** (backend) and **HTML/CSS/JavaScript** (frontend), powered by
**Google's Gemini API**. It helps students ask questions, understand
difficult concepts, generate quizzes, summarize text, and build
personalized learning roadmaps.

---

## 1. Features

- **Ask Question** — Get a direct answer, simple explanation, key points,
  and an example for any academic or general question.
- **Explain Topic** — Break a difficult concept down step-by-step with a
  simple analogy.
- **Generate Quiz** — Turn any topic or passage into 5 interactive MCQs
  with instant scoring and explanations.
- **Summarize Text** — Condense long educational passages into a short
  summary, key points, and important concepts.
- **Learning Path** — Get a structured Beginner → Intermediate → Advanced
  roadmap, complete with timelines and practice suggestions, for any topic.

---

## 2. Technology Stack

**Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic, python-dotenv,
Google Generative AI SDK (Gemini)

**Frontend:** HTML5, CSS3, vanilla JavaScript (Fetch API), Jinja2 templating

No React/Next.js — kept intentionally simple and beginner-friendly.

---

## 3. Folder Structure

```
EduGenie/
│
├── main.py                 # FastAPI app: routes, CORS, error handling
├── requirements.txt        # Python dependencies
├── .env.example             # Template for environment variables
├── README.md
│
├── modules/
│   ├── __init__.py
│   ├── gemini_client.py     # Shared Gemini API wrapper (key handling, errors)
│   ├── qna.py                # Q&A feature logic
│   ├── explanation.py        # Concept explanation feature logic
│   ├── quiz.py                # Quiz generation + JSON validation
│   ├── summarizer.py          # Text summarization logic
│   └── learning_path.py       # Learning roadmap generation
│
├── templates/
│   └── index.html            # Single-page frontend
│
└── static/
    ├── style.css              # Styling
    └── script.js               # Fetch calls + quiz interactivity
```

---

## 4. Installation

### Step 1 — Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Environment Variable Setup

1. Copy the example file:

   ```bash
   cp .env.example .env      # macOS/Linux
   copy .env.example .env    # Windows
   ```

2. Open `.env` and set your Gemini API key:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

The key is loaded server-side via `python-dotenv` and is **never** sent to
the browser or exposed in any frontend JavaScript.

---

## 6. Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **Create API key** (create a new project if prompted).
4. Copy the key into your `.env` file as shown above.

---

## 7. Running the Application

```bash
uvicorn main:app --reload
```

Then open your browser to:

```
http://127.0.0.1:8000
```

---

## 8. API Endpoints

All AI endpoints accept `POST` requests with JSON body `{ "text": "..." }`
and return a JSON response shaped as:

```json
{ "success": true, "result": "...", "error": null }
```

or, on failure:

```json
{ "success": false, "result": null, "error": "friendly error message" }
```

| Method | Endpoint                     | Purpose                              |
|--------|-------------------------------|---------------------------------------|
| GET    | `/`                            | Serves the frontend                   |
| POST   | `/api/qa`                      | Answer a question                     |
| POST   | `/api/explain`                 | Explain a difficult topic             |
| POST   | `/api/quiz`                    | Generate a 5-question MCQ quiz        |
| POST   | `/api/summarize`               | Summarize a passage                   |
| POST   | `/api/learn/recommendations`   | Generate a personalized learning path |

### Example Request — `/api/qa`

```json
POST /api/qa
{
  "text": "What is photosynthesis?"
}
```

### Example Response

```json
{
  "success": true,
  "result": "Direct Answer:\nPhotosynthesis is the process plants use to convert sunlight into energy...\n\nKey Points:\n- ...",
  "error": null
}
```

### Example Request — `/api/quiz`

```json
POST /api/quiz
{
  "text": "The Pythagorean Theorem"
}
```

### Example Response

```json
{
  "success": true,
  "result": {
    "questions": [
      {
        "question": "What does the Pythagorean Theorem describe?",
        "options": [
          "The relationship between the sides of a right triangle",
          "The area of a circle",
          "The volume of a cube",
          "The angles of a hexagon"
        ],
        "correct_answer": "The relationship between the sides of a right triangle",
        "explanation": "It relates the lengths of the two legs and the hypotenuse of a right triangle: a^2 + b^2 = c^2."
      }
    ]
  },
  "error": null
}
```

---

## 9. How to Test Each Feature

1. Start the server (`uvicorn main:app --reload`) and open
   `http://127.0.0.1:8000`.
2. Click **Ask Question**, type a question, and click **Ask EduGenie**.
3. Click **Explain Topic**, enter a hard concept, and click **Explain This**.
4. Click **Generate Quiz**, enter a topic or paste a passage, click
   **Generate Quiz**, answer the 5 questions, then click **Submit Quiz** to
   see your score, correct/incorrect highlighting, and explanations.
5. Click **Summarize Text**, paste a long passage, and click **Summarize**.
6. Click **Learning Path**, enter a topic (e.g. "Cybersecurity"), and click
   **Build My Roadmap**.

You can also test the API directly with `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"What is the difference between HTTP and HTTPS?\"}"
```

---

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is not set` error | Make sure you created `.env` (not just `.env.example`) and set a real key, then restart the server. |
| `ModuleNotFoundError` on startup | Re-run `pip install -r requirements.txt` inside your activated virtual environment. |
| Buttons do nothing / network errors in console | Confirm the server is running on `http://127.0.0.1:8000` and that you're accessing the app from that same address. |
| Quiz shows a friendly error instead of questions | Gemini occasionally returns malformed JSON for unusual inputs — try a clearer topic or shorter passage and try again. |
| `429` errors from Gemini | You've hit your API quota/rate limit — wait a bit or check your Google AI Studio usage dashboard. |
| Static files (CSS/JS) not loading | Make sure you're running `uvicorn` from the project's root folder (the one containing `main.py`), so the relative `static/` and `templates/` paths resolve correctly. |

---

## 11. Security Notes

- The Gemini API key lives only in `.env` on the server and is never sent
  to the browser.
- All input is validated with Pydantic (length limits included).
- Errors are logged server-side; only short, friendly messages are ever
  returned to the client — no stack traces.
- CORS is restricted to the configured local origins by default.

---

## 12. Final Verification Checklist

- [x] Every button/form in the frontend calls a real backend endpoint via `fetch()`
- [x] All 5 `/api/*` routes exist and match the JavaScript fetch URLs exactly
- [x] JSON field names (`text`) match the Pydantic request models
- [x] Quiz JSON schema (`questions[].question/options/correct_answer/explanation`) matches what `script.js` parses
- [x] `GEMINI_API_KEY` is read from environment variables only, never hardcoded
- [x] `requirements.txt` contains every package actually imported by the code
- [x] `static/` and `templates/` paths match what `main.py` mounts
- [x] Errors never expose Python tracebacks to the browser
=======
# edutech
>>>>>>> 6ec5736370cf46d3f4fdea0df421bab01b845898
