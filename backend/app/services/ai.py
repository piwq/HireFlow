# AI summarizer stub — replace implementation when API key is available
# Supports: Claude (anthropic), YandexGPT, GigaChat
# Frontend already calls POST /api/candidates/{id}/summarize — just wire up here

async def summarize_resume(text: str) -> str:
    """Return a 3-sentence summary of the resume. Stub returns placeholder."""
    # TODO: replace with real API call when key is available
    # Example with Claude:
    #   import anthropic
    #   client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    #   msg = client.messages.create(model="claude-opus-4-6", max_tokens=300,
    #       messages=[{"role": "user", "content": f"Summarize in 3 sentences: {text}"}])
    #   return msg.content[0].text
    return "AI-анализ временно недоступен. Добавьте API-ключ для активации функции."
