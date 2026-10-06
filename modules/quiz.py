"""
quiz.py
-------
Generates exactly 5 multiple-choice questions from a topic or a passage
of educational text. Returns strict, parsed JSON matching the schema the
frontend expects.
"""

from .gemini_client import generate_content, safe_json_loads, GeminiError


def generate_quiz(source_text: str) -> dict:
    prompt = f"""You are EduGenie, an AI that creates multiple-choice quizzes for
students.

Based on the following topic or passage, generate EXACTLY 5 multiple-choice
questions:

\"\"\"{source_text}\"\"\"

Respond with ONLY valid JSON (no markdown fences, no commentary) matching
EXACTLY this schema:

{{
  "questions": [
    {{
      "question": "string - the question text",
      "options": ["string option A", "string option B", "string option C", "string option D"],
      "correct_answer": "string - must exactly match one of the 4 options",
      "explanation": "string - a short explanation of why that answer is correct"
    }}
  ]
}}

Rules:
- Exactly 5 items in "questions".
- Exactly 4 items in "options" for every question.
- "correct_answer" must be an exact copy of one of the strings in "options".
- Questions should test real understanding, not just memorized trivia.
- Keep each explanation to 1-2 sentences."""

    raw = generate_content(prompt, expect_json=True, max_output_tokens=2000)
    data = safe_json_loads(raw)

    questions = data.get("questions") if isinstance(data, dict) else None
    if not isinstance(questions, list) or len(questions) == 0:
        raise GeminiError("Gemini returned an unexpected quiz format.")

    # Light validation / normalization so the frontend can rely on the shape.
    cleaned_questions = []
    for q in questions[:5]:
        question_text = str(q.get("question", "")).strip()
        options = q.get("options", [])
        correct_answer = str(q.get("correct_answer", "")).strip()
        explanation = str(q.get("explanation", "")).strip()

        if not question_text or not isinstance(options, list) or len(options) < 2 or not correct_answer:
            continue

        cleaned_questions.append(
            {
                "question": question_text,
                "options": [str(o).strip() for o in options][:4],
                "correct_answer": correct_answer,
                "explanation": explanation,
            }
        )

    if not cleaned_questions:
        raise GeminiError("Gemini returned a quiz with no valid questions.")

    return {"questions": cleaned_questions}
