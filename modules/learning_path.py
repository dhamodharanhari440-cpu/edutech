"""
learning_path.py
-----------------
Generates a personalized, structured learning roadmap (Beginner ->
Intermediate -> Advanced) for a topic the user requests.
"""

from .gemini_client import generate_content


def generate_learning_path(topic: str) -> str:
    prompt = f"""You are EduGenie, an AI that designs structured learning roadmaps
for students.

The learner wants a roadmap for this topic:
"{topic}"

Respond as plain text, structured EXACTLY like this:

Learning Roadmap: {topic}

Beginner Stage
- Topics: <comma-separated list of topics>
- What to Learn: <short description>
- Suggested Timeline: <e.g. "2-3 weeks">
- Practice Suggestions: <short, concrete practice ideas>
- Recommended Resource Types: <e.g. "official docs, beginner video course">

Intermediate Stage
- Topics: <comma-separated list of topics>
- What to Learn: <short description>
- Suggested Timeline: <e.g. "4-6 weeks">
- Practice Suggestions: <short, concrete practice ideas>
- Recommended Resource Types: <...>

Advanced Stage
- Topics: <comma-separated list of topics>
- What to Learn: <short description>
- Suggested Timeline: <e.g. "6-8 weeks">
- Practice Suggestions: <short, concrete practice ideas>
- Recommended Resource Types: <...>

Make the topics and suggestions genuinely specific to "{topic}" rather than
generic advice."""

    return generate_content(prompt, max_output_tokens=1200)
