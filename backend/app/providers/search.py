import httpx
from app.errors import AppError


class SearchProvider:
    def __init__(self, settings):
        self.settings = settings

    async def discover(self, topic, budget):
        if self.settings.app_mode == "fixture":
            return [
                {
                    "title": "[Fixture] Células e organização da vida",
                    "url": "https://example.org/studyforge-fixture/celulas",
                },
                {
                    "title": "[Fixture] Energia nos seres vivos",
                    "url": "https://example.org/studyforge-fixture/energia",
                },
            ]
        if not self.settings.search_api_key.get_secret_value():
            raise AppError(
                "SEARCH_NOT_CONFIGURED",
                "O provedor de busca não foi configurado.",
                503,
                "search",
            )
        try:
            async with httpx.AsyncClient(
                trust_env=False, timeout=10, follow_redirects=False
            ) as client:
                response = await budget.call(
                    lambda: client.get(
                        "https://api.search.brave.com/res/v1/web/search",
                        params={
                            "q": topic,
                            "count": self.settings.max_pages_per_research,
                        },
                        headers={
                            "X-Subscription-Token": self.settings.search_api_key.get_secret_value(),
                            "Accept": "application/json",
                        },
                    )
                )
                response.raise_for_status()
                return [
                    {
                        "title": str(item.get("title", "Fonte web"))[:200],
                        "url": item["url"],
                    }
                    for item in response.json()
                    .get("web", {})
                    .get("results", [])[: self.settings.max_pages_per_research]
                    if isinstance(item.get("url"), str)
                ]
        except AppError:
            raise
        except Exception:
            raise AppError(
                "SEARCH_UNAVAILABLE",
                "O serviço de pesquisa está indisponível.",
                502,
                "search",
                True,
            ) from None
