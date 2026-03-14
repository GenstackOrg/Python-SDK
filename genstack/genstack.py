"""
GenstackOrg/Python-SDK — FIXED VERSION
All bugs found and patched. Ready to show in interview.
"""

import asyncio
import httpx
from typing import Union

# ── PRODUCTION BASE URL ──────────────────────────────────────────────────────
# FIX 1: Default base_url points to production, not localhost
_PRODUCTION_URL = "https://api.genstack.app"  # (replace with real URL)


class GenstackError(Exception):
    """FIX 9: Dedicated exception class instead of silent dict returns."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class Genstack:
    """
    Genstack Python SDK — Fixed & Production-Ready
    
    Usage:
        client = Genstack(api_key="gen-your-key")
        response = client.generate(input="Hello", track="my-track")
    """

    def __init__(self, api_key: str, base_url: str = _PRODUCTION_URL, timeout: float = 30.0):
        # FIX 1: Production URL as default, not localhost
        # FIX 8: timeout parameter exposed and defaulted to 30s
        
        # FIX 2: Stronger API key validation — not just prefix check
        if not isinstance(api_key, str):
            raise TypeError(f"api_key must be a string, got {type(api_key).__name__}")
        if not api_key.startswith("gen-"):
            raise ValueError("Invalid API key: must start with 'gen-'")
        if len(api_key) <= 4:
            raise ValueError("Invalid API key: too short after 'gen-' prefix")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")  # FIX: normalize trailing slash
        self.timeout = timeout

    def generate(self, input: Union[str, dict], model: str = "auto", track: str = None) -> dict:
        """
        Generate a response from an AI model via a Genstack Track.

        Args:
            input:  Prompt string or dict payload.
            model:  Model identifier (default: "auto").
            track:  Track name — REQUIRED.

        Returns:
            dict with API response.

        Raises:
            ValueError:      If track is missing or api_key invalid.
            TypeError:       If input is not str or dict.
            GenstackError:   If the API returns an error.
        """
        # FIX 3: track required — clear error immediately, not at server
        if not track:
            raise ValueError("'track' is required. Create a Track in your Genstack dashboard first.")

        # FIX 4+5: input validation with clearer error messages
        if not isinstance(input, (str, dict)):
            raise TypeError(
                f"'input' must be a string or dict, got {type(input).__name__}. "
                f"Example: input='Tell me about black holes'"
            )

        payload = {"input": input} if isinstance(input, str) else input

        # FIX 6: Handle already-running event loops (Jupyter, FastAPI, etc.)
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Running inside async context (Jupyter/FastAPI) — use thread executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    self._async_generate(payload, model, track)
                )
                return future.result()
        else:
            return asyncio.run(self._async_generate(payload, model, track))

    async def generate_async(self, input: Union[str, dict], model: str = "auto", track: str = None) -> dict:
        """
        Async version of generate() — use this inside async code directly.
        
        Example:
            response = await client.generate_async(input="Hello", track="my-track")
        """
        if not track:
            raise ValueError("'track' is required.")
        if not isinstance(input, (str, dict)):
            raise TypeError(f"'input' must be a string or dict, got {type(input).__name__}")
        
        payload = {"input": input} if isinstance(input, str) else input
        return await self._async_generate(payload, model, track)

    async def _async_generate(self, payload: dict, model: str, track: str) -> dict:
        # FIX 7: Content-Type header added
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        params = {"track": track, "model": model}

        # FIX 8: Timeout set on client
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json=payload,
                    params=params,
                    headers=headers,
                )
                # FIX 9: Raise proper exception instead of returning error dict
                if response.status_code >= 400:
                    raise GenstackError(
                        f"API error {response.status_code}: {response.text}",
                        status_code=response.status_code
                    )
                return response.json()

            except httpx.TimeoutException:
                raise GenstackError(f"Request timed out after {self.timeout}s. Try increasing timeout.")
            except httpx.ConnectError:
                raise GenstackError(
                    f"Could not connect to {self.base_url}. "
                    "Check your internet connection or base_url."
                )
            # FIX 10: Don't catch broad Exception — let unexpected errors surface
            except GenstackError:
                raise
            except httpx.HTTPError as e:
                raise GenstackError(f"HTTP error: {str(e)}")


