
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Optional

from groq import Groq

from config import GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, SYSTEM_PROMPT


def get_groq_client() -> Groq:
    api_key: Optional[str] = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY environment variable not set.\n"
            
        )
    return Groq(api_key=api_key)


def call_llm(
    client: Groq,
    user_prompt: str,
    conversation: list[dict],
) -> str:
    conversation.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )

    reply: str = response.choices[0].message.content.strip()
    conversation.append({"role": "assistant", "content": reply})
    return reply