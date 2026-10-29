"""Provider boundary: credentials and execution budgets stay on the backend."""

import hashlib
import math
import re
import asyncio
import httpx
from app.errors import AppError
from app.operations import Budget
from app.settings import Settings
from pydantic import ValidationError


async def call_provider(budget, callback):
    """At most two idempotent attempts; each counts against the shared execution budget."""
    for attempt in range(2):
        try:
            return await budget.call(callback)
        except Exception as error:
            if attempt or (
                getattr(error, "code", None) not in (429, 500, 502, 503, 504)
                and not isinstance(
                    error,
                    (
                        httpx.TimeoutException,
                        httpx.NetworkError,
                        httpx.RemoteProtocolError,
                    ),
                )
            ):
                raise
            delay = 1.0
            details = getattr(error, "details", {})
            if isinstance(details, dict):
                for item in details.get("error", {}).get("details", []):
                    if item.get("@type", "").endswith("RetryInfo"):
                        try:
                            delay = max(
                                delay,
                                float(item.get("retryDelay", "1s").removesuffix("s")),
                            )
                        except TypeError, ValueError:
                            pass
            budget.check()
            if not math.isfinite(delay) or delay >= budget.deadline - budget.clock():
                raise
            await asyncio.sleep(delay)


class GeminiProvider:
    def __init__(self, settings: Settings, client_factory=None):
        self.settings = settings
        self.client_factory = client_factory
        self.last_generation_metadata = {}

    def _client(self):
        if self.settings.gemini_backend == "developer":
            if not self.settings.gemini_api_key.get_secret_value():
                raise AppError(
                    "PROVIDER_NOT_CONFIGURED",
                    "Configure a chave Gemini no backend para usar o modelo real.",
                    503,
                    "provider",
                )
            arguments = {"api_key": self.settings.gemini_api_key.get_secret_value()}
        else:
            if not self.settings.gemini_project or not self.settings.gemini_location:
                raise AppError(
                    "PROVIDER_NOT_CONFIGURED",
                    "Configure projeto, região e credenciais Vertex no backend.",
                    503,
                    "provider",
                )
            arguments = {
                "vertexai": True,
                "project": self.settings.gemini_project,
                "location": self.settings.gemini_location,
            }
        if self.client_factory:
            return self.client_factory()
        from google import genai
        from google.genai import types

        return genai.Client(
            **arguments,
            http_options=types.HttpOptions(
                timeout=int(min(60, self.settings.turn_timeout) * 1000),
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )

    async def embed(
        self, texts: list[str], *, query=False, budget: Budget | None = None
    ):
        if self.settings.app_mode == "fixture":
            return [self._fixture_vector(text) for text in texts]
        client = self._client()
        from google.genai import types

        budget = budget or Budget(
            self.settings.ingestion_timeout,
            attempts=self.settings.max_external_attempts,
        )
        vectors = []
        try:
            for offset in range(0, len(texts), self.settings.embedding_batch_size):
                batch = texts[offset : offset + self.settings.embedding_batch_size]
                response = await call_provider(
                    budget,
                    lambda: client.aio.models.embed_content(
                        model=self.settings.gemini_embedding_model,
                        contents=batch,
                        config=types.EmbedContentConfig(
                            output_dimensionality=768,
                            task_type="RETRIEVAL_QUERY"
                            if query
                            else "RETRIEVAL_DOCUMENT",
                        ),
                    ),
                )
                batch_vectors = [
                    self.validate_vector(e.values) for e in response.embeddings or []
                ]
                if len(batch_vectors) != len(batch):
                    raise AppError(
                        "INVALID_EMBEDDING",
                        "A resposta de vetores veio incompleta.",
                        502,
                        "embed",
                    )
                vectors.extend(batch_vectors)
            return vectors
        except AppError:
            raise
        except Exception:
            raise AppError(
                "EXTERNAL_UNAVAILABLE",
                "O serviço de vetores está indisponível.",
                502,
                "embed",
                True,
            ) from None
        finally:
            await client.aio.aclose()

    async def generate(self, prompt: str, schema, *, budget: Budget | None = None):
        self.last_generation_metadata = {}
        client = self._client()
        from google.genai import types

        budget = budget or Budget(
            self.settings.turn_timeout, attempts=self.settings.max_external_attempts
        )
        try:
            result = await call_provider(
                budget,
                lambda: client.aio.models.generate_content(
                    model=self.settings.gemini_generation_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_json_schema=schema.model_json_schema(),
                        temperature=0,
                        max_output_tokens=2048,
                    ),
                ),
            )
            usage = result.usage_metadata
            self.last_generation_metadata = {
                "model_version": result.model_version,
                "finish_reason": str(result.candidates[0].finish_reason)
                if getattr(result, "candidates", None)
                else None,
                "usage": {
                    field: getattr(usage, field, None)
                    for field in (
                        "prompt_token_count",
                        "candidates_token_count",
                        "thoughts_token_count",
                        "total_token_count",
                    )
                }
                if usage
                else {},
            }
            return schema.model_validate_json(result.text)
        except ValidationError:
            raise AppError(
                "INVALID_MODEL_OUTPUT",
                "O modelo devolveu uma resposta incompleta ou fora do formato esperado. Tente novamente.",
                502,
                "generation",
                True,
            ) from None
        except AppError:
            raise
        except Exception as error:
            self.last_generation_metadata.update(
                error_type=type(error).__name__, status=getattr(error, "code", None)
            )
            raise AppError(
                "EXTERNAL_UNAVAILABLE",
                "O serviço de geração está indisponível.",
                502,
                "generation",
                True,
            ) from None
        finally:
            await client.aio.aclose()

    @staticmethod
    def validate_vector(values):
        if len(values) != 768 or not all(math.isfinite(v) for v in values):
            raise AppError(
                "INVALID_EMBEDDING", "Vetor incompatível com o perfil.", 502, "embed"
            )
        norm = math.sqrt(sum(v * v for v in values))
        if norm == 0:
            raise AppError(
                "INVALID_EMBEDDING", "Vetor vazio ou inválido.", 502, "embed"
            )
        return [v / norm for v in values]

    @staticmethod
    def _fixture_vector(text):
        # Deterministic non-semantic test double. No provider call or payload log.
        vector = [0.0] * 768
        for token in re.findall(r"\w+", text.casefold()):
            digest = hashlib.sha256(token.encode()).digest()
            vector[int.from_bytes(digest[:2]) % 768] += 1 if digest[2] % 2 else -1
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            vector[0] = 1.0
            return vector
        return [value / norm for value in vector]
