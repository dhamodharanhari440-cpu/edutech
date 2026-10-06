"""
qna.py
------
Question-answering feature. Given a student's question, asks Gemini for a
concise, student-friendly answer with a short explanation, key points, and
an example when useful.
"""

from .gemini_client import generate_content


def answer_question(question: str) -> str:
    prompt = f"""You are EduGenie, a friendly AI study assistant for students.

A student asked the following question:
"{question}"

Respond in clear, student-friendly language using this structure (as plain
text with short headings, not JSON):

Direct Answer:
<a short, direct answer in 1-3 sentences>

Simple Explanation:
<a slightly deeper explanation in simple language>

Key Points:
- <point 1>
- <point 2>
- <point 3 (optional)>

Example (only if genuinely useful for this question):
<a short concrete example>

Keep the whole answer concise - avoid unnecessary length. Do not repeat the
question back verbatim at the start."""

    return generate_content(prompt, max_output_tokens=800)
