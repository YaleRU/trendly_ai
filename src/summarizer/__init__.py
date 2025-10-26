import os
import asyncio
from .prompt import prompt as _PROMPT

_client = None

def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI  # type: ignore
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

def _mk_prompt(text: str) -> str:
    text = (text or "").strip()
    if len(text) > 8000:
        text = text[:8000]
    return _PROMPT.replace("{текст новости}", text)

async def summarize_text(article_text: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        t = (article_text or "").strip()
        return (t[:400] + "…") if len(t) > 400 else t

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "300"))
    except ValueError:
        max_tokens = 300
    try:
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    except ValueError:
        temperature = 0.2

    prompt_text = _mk_prompt(article_text)

    def _call():
        client = _get_client()
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": "Ты краткий редактор новостей."},
                {"role": "user", "content": prompt_text},
            ],
        )
        return (resp.choices[0].message.content or "").strip()

    return await asyncio.to_thread(_call)
