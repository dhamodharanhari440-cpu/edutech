"""
summarizer.py
-------------
Summarizes a long educational passage into a short summary, key points,
and important concepts.
"""

from .gemini_client import generate_content

MAX_INPUT_CHARS = 20000


def summarize_text(text: str) -> str:
    trimmed = text[:MAX_INPUT_CHARS]

    prompt = f"""You are EduGenie, an AI that summarizes educational text for
students who need a quick, clear overview.

Passage:
\"\"\"{trimmed}\"\"\"

Respond as plain text with this structure:

Short Summary:
<a concise 2-4 sentence summary of the passage>

Key Points:
- <key point 1>
- <key point 2>
- <key point 3>
(add more only if truly needed, max 6)

Important Concepts:
- <concept 1>: <one-line explanation>
- <concept 2>: <one-line explanation>

Keep the language simple and avoid copying long sentences verbatim from the
passage - rephrase in your own words."""

    return generate_content(prompt, max_output_tokens=900)
