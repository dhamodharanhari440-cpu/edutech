"""
explanation.py
---------------
"Explain a difficult topic" feature. Breaks a complex topic down into
simple, step-by-step language with an analogy/example and key points.
"""

from .gemini_client import generate_content


def explain_topic(topic: str) -> str:
    prompt = f"""You are EduGenie, an AI tutor that explains difficult academic
topics to beginners in very simple language.

Topic to explain:
"{topic}"

Structure your explanation as plain text with short headings:

Simple Overview:
<1-2 sentence plain-language overview of what this topic is>

Step-by-Step Explanation:
1. <step or idea 1>
2. <step or idea 2>
3. <step or idea 3>
(add more steps only if genuinely needed)

Analogy / Example:
<a relatable real-world analogy or worked example that makes the concept click>

Key Points to Remember:
- <key point 1>
- <key point 2>
- <key point 3>

Use short sentences and avoid jargon. If a technical term is necessary,
briefly define it in plain words the first time it's used."""

    return generate_content(prompt, max_output_tokens=1000)
