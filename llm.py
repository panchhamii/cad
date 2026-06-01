"""
llm.py
──────
Handles all communication with the local Ollama LLM.

Ollama runs entirely offline on your machine — no API key needed,
no internet connection required at inference time.

Responsibilities:
- Create and return an Ollama-compatible client
- Send prompts to the LLM and return the raw text response
- Maintain conversation history so retry messages include previous context
"""

from openai import OpenAI

from config import OLLAMA_MODEL, OLLAMA_BASE_URL, LLM_TEMPERATURE, SYSTEM_PROMPT


def get_ollama_client() -> OpenAI:
    """
    Create and return an Ollama client.

    Ollama exposes an OpenAI-compatible API at localhost:11434,
    so we use the openai library to talk to it.
    No API key is needed — Ollama runs fully offline.

    Returns:
        OpenAI: client pointed at local Ollama server

    Raises:
        ConnectionError: if Ollama is not running (start with: ollama serve)
    """
    return OpenAI(
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key="ollama",   # Ollama requires any non-empty string here
    )


def call_llm(
    client: OpenAI,
    user_prompt: str,
    conversation: list[dict],
) -> str:
    """
    Send a prompt to the Ollama LLM and return the response text.

    The conversation list is updated in-place so that previous messages
    are included in each new API call. This allows the retry loop to
    send error context back to the LLM for self-correction.

    Args:
        client:       Ollama client from get_ollama_client()
        user_prompt:  The new message to send (description or error feedback)
        conversation: Running list of past messages — updated in-place

    Returns:
        str: raw text response from the LLM (may contain markdown fences)
    """
    # Append the new user message to conversation history
    conversation.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation,
        temperature=LLM_TEMPERATURE,
    )

    reply: str = response.choices[0].message.content.strip()

    # Append the LLM reply so the next call has full context
    conversation.append({"role": "assistant", "content": reply})
    return reply