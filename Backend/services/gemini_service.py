"""Google Gemini wrapper for explanations, summaries, suggestions, and code gen."""
import os
import google.generativeai as genai


def _model():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set in environment")
    genai.configure(api_key=key)
    return genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))


def explain_code(code: str, language: str = "python") -> str:
    prompt = f"""You are a programming tutor. Explain the following {language} code clearly for a student.
Return three sections in plain text:
1) Step-by-step explanation
2) Algorithm summary (2-3 sentences)
3) Logic breakdown (bullets)

CODE:
```{language}
{code}
```"""
    return _model().generate_content(prompt).text


def summarize_code(code: str, language: str = "python") -> str:
    prompt = f"Summarize this {language} program in 2 sentences for a beginner:\n\n{code}"
    return _model().generate_content(prompt).text


def suggest_improvements(code: str, language: str = "python") -> str:
    prompt = f"""Review this {language} code and return:
- Optimization suggestions
- Time/space complexity analysis
- Best-practice recommendations

CODE:
```{language}
{code}
```"""
    return _model().generate_content(prompt).text


def flowchart_to_code(mermaid: str, language: str = "python") -> str:
    prompt = f"""Convert this Mermaid flowchart into a complete, runnable {language} program.
Return ONLY the code inside a single fenced code block.

FLOWCHART:
```mermaid
{mermaid}
```"""
    text = _model().generate_content(prompt).text or ""
    # strip code fences
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            block = parts[1]
            if block.startswith(language):
                block = block[len(language):]
            return block.strip("\n")
    return text.strip()
