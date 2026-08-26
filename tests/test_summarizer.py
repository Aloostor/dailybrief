from __future__ import annotations

import pytest

from dailybrief.reader import Note
import dailybrief.summarizer as summarizer
from dailybrief.summarizer import generate_brief


class _FakeTextBlock:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.content = [_FakeTextBlock(text)]


class _FakeMessagesAPI:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text

    def create(self, **kwargs):
        return _FakeResponse(self._response_text)


class _FakeClient:
    def __init__(self, api_key: str, response_text: str = "Ozet") -> None:
        self.api_key = api_key
        self.messages = _FakeMessagesAPI(response_text)


class _FakeAnthropicModule:
    class APIError(Exception):
        pass

    class APIConnectionError(APIError):
        pass

    class RateLimitError(APIError):
        pass

    def __init__(self, response_text: str = "Ozet") -> None:
        self._response_text = response_text

    def Anthropic(self, api_key: str):
        return _FakeClient(api_key=api_key, response_text=self._response_text)


def test_generate_brief_raises_when_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(summarizer, "_load_anthropic", lambda: _FakeAnthropicModule())

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY bulunamadi"):
        generate_brief([Note(name="n.md", content="icerik")])


def test_generate_brief_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    monkeypatch.setattr(
        summarizer,
        "_load_anthropic",
        lambda: _FakeAnthropicModule(response_text="Kisa brifing"),
    )

    result = generate_brief([Note(name="n.md", content="icerik")])

    assert result == "Kisa brifing"


def test_generate_brief_rate_limit_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")

    class _RateLimitedClient:
        class _Messages:
            def create(self, **kwargs):
                raise _FakeAnthropicModule.RateLimitError("rate limited")

        def __init__(self, api_key: str) -> None:
            self.messages = self._Messages()

    class _RateLimitAnthropicModule(_FakeAnthropicModule):
        def Anthropic(self, api_key: str):
            return _RateLimitedClient(api_key=api_key)

    monkeypatch.setattr(
        summarizer,
        "_load_anthropic",
        lambda: _RateLimitAnthropicModule(),
    )

    with pytest.raises(RuntimeError, match="rate limit"):
        generate_brief([Note(name="n.md", content="icerik")])
