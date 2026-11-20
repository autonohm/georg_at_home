"""HTTP client for a local LLM with an OpenAI-compatible chat endpoint (plan P6).

llama.cpp (llama-server), Ollama and vLLM all offer ``POST /v1/chat/completions``.
The planner only knows this endpoint; model and hardware stay exchangeable.

    GEORG_LLM_URL      default http://localhost:8080
    GEORG_LLM_MODEL    default local (llama-server ignores it, Ollama needs the model name)
    GEORG_LLM_TIMEOUT_S default 120
"""

from dataclasses import dataclass, field
import json
import os
from typing import List
import urllib.error
import urllib.request


class LLMError(RuntimeError):
    pass


@dataclass
class LLMConfig:
    url: str = field(default_factory=lambda: os.environ.get('GEORG_LLM_URL',
                                                            'http://localhost:8080'))
    model: str = field(default_factory=lambda: os.environ.get('GEORG_LLM_MODEL', 'local'))
    timeout_s: float = field(default_factory=lambda: float(
        os.environ.get('GEORG_LLM_TIMEOUT_S', '120')))
    temperature: float = 0.0
    seed: int = 42
    max_tokens: int = 600


class LLMClient:

    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()

    @property
    def model(self) -> str:
        return self.config.model

    def chat(self, messages: List[dict], schema: dict = None) -> str:
        """Send the conversation, return the text of the answer (expected to be JSON).

        ``schema``: JSON schema the answer must follow (constrained decoding).
        """
        c = self.config
        body = {
            'model': c.model,
            'messages': messages,
            'temperature': c.temperature,
            'seed': c.seed,
            'max_tokens': c.max_tokens,
            'response_format': {'type': 'json_object'},
        }
        if schema is not None:
            body['response_format'] = {'type': 'json_schema', 'json_schema': {
                'name': 'georg_plan', 'strict': True, 'schema': schema}}
        request = urllib.request.Request(
            c.url.rstrip('/') + '/v1/chat/completions', data=json.dumps(body).encode(),
            headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=c.timeout_s) as response:
                data = json.loads(response.read().decode())
        except (urllib.error.URLError, OSError, ValueError) as exc:
            raise LLMError(f'LLM endpoint {c.url} not reachable: {exc}') from exc
        try:
            return data['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f'unexpected LLM response: {str(data)[:200]}') from exc

    def available(self) -> bool:
        """Return True if the endpoint answers (GET /v1/models)."""
        try:
            with urllib.request.urlopen(self.config.url.rstrip('/') + '/v1/models',
                                        timeout=3) as response:
                return response.status == 200
        except (urllib.error.URLError, OSError):
            return False
