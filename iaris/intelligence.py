"""
IARIS intelligence layer.

Runs selective insight recomputation and reuses cached insight when changes are minor.
Optionally uses Gemini only on meaningful changes.
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

from iaris.credentials import CredentialStore

logger = logging.getLogger("iaris.intelligence")

GEMINI_ENDPOINT_CANDIDATES = (
    ("v1", "gemini-2.0-flash"),
    ("v1beta", "gemini-2.0-flash"),
    ("v1beta", "gemini-1.5-flash"),
    ("v1beta", "gemini-1.5-pro"),
)


@dataclass
class InsightCacheEntry:
    insight: str
    source: str
    timestamp: float
    gemini_meta: dict[str, object] = field(default_factory=dict)


class IntelligenceLayer:
    """Applies significance gating and cache reuse for high-level insights."""

    def __init__(
        self,
        cache_ttl_seconds: int = 45,
        external_min_interval_seconds: int = 20,
        repeated_state_ttl_seconds: int = 120,
    ):
        self.cache_ttl_seconds = cache_ttl_seconds
        self.external_min_interval_seconds = external_min_interval_seconds
        self.repeated_state_ttl_seconds = repeated_state_ttl_seconds
        self._cache: Optional[InsightCacheEntry] = None
        self._last_gemini_meta: dict[str, object] = {
            "enabled": False,
            "attempted": False,
            "status": "not_configured",
            "message": "Gemini integration not configured.",
            "api_version": "",
            "model": "",
        }
        self._last_remote_attempt_at: float = 0.0
        self._last_remote_signature: str = ""

    def evaluate(
        self,
        *,
        observability: dict,
        engine_insights: list[dict],
        credentials: CredentialStore,
        force_refresh: bool = False,
        force_external: bool = False,
    ) -> dict:
        """Evaluate current state and decide whether to recompute or reuse insight."""
        now = time.time()
        significant = bool(observability.get("significant", False))
        reason = observability.get("significance_reason", "")
        effective_significant = significant or force_refresh

        if not effective_significant and self._cache:
            cache_age = int(now - self._cache.timestamp)
            if cache_age <= self.cache_ttl_seconds:
                gemini_meta = self._cache.gemini_meta or self._last_gemini_meta
                return {
                    "significant": False,
                    "reason": reason,
                    "used_cache": True,
                    "source": "cache",
                    "insight": self._cache.insight,
                    "last_updated": self._cache.timestamp,
                    "cache_age_seconds": cache_age,
                    "cache_ttl_seconds": self.cache_ttl_seconds,
                    "forced_refresh": False,
                    "gemini": gemini_meta,
                }

        if effective_significant:
            fresh_insight, source, gemini_meta = self._compute_fresh_insight(
                observability=observability,
                engine_insights=engine_insights,
                credentials=credentials,
                force_external=force_external,
            )
            self._last_gemini_meta = gemini_meta
            self._cache = InsightCacheEntry(
                insight=fresh_insight,
                source=source,
                timestamp=now,
                gemini_meta=gemini_meta,
            )
            return {
                "significant": True,
                "reason": reason,
                "used_cache": False,
                "source": source,
                "insight": fresh_insight,
                "last_updated": now,
                "cache_age_seconds": 0,
                "cache_ttl_seconds": self.cache_ttl_seconds,
                    "forced_refresh": force_refresh,
                "gemini": gemini_meta,
            }

        # No significant changes and no valid cache.
        fallback = "System stable. No significant changes detected. Reusing previous operating posture."
        gemini_meta = self._idle_gemini_meta(credentials)
        self._last_gemini_meta = gemini_meta
        self._cache = InsightCacheEntry(
            insight=fallback,
            source="local",
            timestamp=now,
            gemini_meta=gemini_meta,
        )
        return {
            "significant": False,
            "reason": reason,
            "used_cache": False,
            "source": "local",
            "insight": fallback,
            "last_updated": now,
            "cache_age_seconds": 0,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "forced_refresh": force_refresh,
            "gemini": gemini_meta,
        }

    def _compute_fresh_insight(
        self,
        *,
        observability: dict,
        engine_insights: list[dict],
        credentials: CredentialStore,
        force_external: bool = False,
    ) -> tuple[str, str, dict[str, object]]:
        local_summary = self._build_local_summary(observability=observability, engine_insights=engine_insights)
        gemini_enabled = os.getenv("IARIS_ENABLE_GEMINI", "0") == "1"

        # External AI is opt-in so the system remains safe and predictable by default.
        if not gemini_enabled:
            return (
                local_summary,
                "local",
                {
                    "enabled": False,
                    "attempted": False,
                    "status": "disabled",
                    "message": "Gemini disabled. Set IARIS_ENABLE_GEMINI=1 to enable remote summaries.",
                    "api_version": "",
                    "model": "",
                },
            )

        if not credentials.has_gemini_key:
            return (
                local_summary,
                "local",
                {
                    "enabled": False,
                    "attempted": False,
                    "status": "missing_key",
                    "message": "Gemini API key not found at ~/.iaris/gemini.key.",
                    "api_version": "",
                    "model": "",
                },
            )

        signature = self._build_external_signature(
            observability=observability,
            engine_insights=engine_insights,
            local_summary=local_summary,
        )

        should_attempt, skip_meta = self._should_attempt_remote(
            signature=signature,
            force_external=force_external,
        )
        if not should_attempt:
            return local_summary, "local", skip_meta

        self._last_remote_signature = signature
        self._last_remote_attempt_at = time.time()

        remote_result = self._query_gemini(
                gemini_key=credentials.gemini_api_key,
                observability=observability,
                local_summary=local_summary,
            )
        if remote_result.get("text"):
            return (
                str(remote_result["text"]),
                "gemini",
                {
                    "enabled": True,
                    "attempted": True,
                    "status": "success",
                    "message": "Gemini summary generated successfully.",
                    "api_version": str(remote_result.get("api_version", "")),
                    "model": str(remote_result.get("model", "")),
                },
            )

        return (
            local_summary,
            "local",
            {
                "enabled": True,
                "attempted": True,
                "status": str(remote_result.get("status", "unavailable")),
                "message": str(remote_result.get("message", "Gemini unavailable; using local summary.")),
                "api_version": str(remote_result.get("api_version", "")),
                "model": str(remote_result.get("model", "")),
            },
        )

    @staticmethod
    def _idle_gemini_meta(credentials: CredentialStore) -> dict[str, object]:
        gemini_enabled = os.getenv("IARIS_ENABLE_GEMINI", "0") == "1"
        if not gemini_enabled:
            return {
                "enabled": False,
                "attempted": False,
                "status": "disabled",
                "message": "Gemini disabled. Set IARIS_ENABLE_GEMINI=1 to enable remote summaries.",
                "api_version": "",
                "model": "",
            }

        if not credentials.has_gemini_key:
            return {
                "enabled": False,
                "attempted": False,
                "status": "missing_key",
                "message": "Gemini API key not found at ~/.iaris/gemini.key.",
                "api_version": "",
                "model": "",
            }

        return {
            "enabled": True,
            "attempted": False,
            "status": "ready",
            "message": "Gemini is configured and will run on meaningful changes.",
            "api_version": "",
            "model": "",
        }

    def _build_external_signature(
        self,
        *,
        observability: dict,
        engine_insights: list[dict],
        local_summary: str,
    ) -> str:
        insight_seed = [
            {
                "type": item.get("type"),
                "severity": item.get("severity"),
                "message": item.get("message"),
                "recommendation": item.get("recommendation"),
            }
            for item in engine_insights[:3]
        ]
        signature_payload = {
            "reason": observability.get("significance_reason", ""),
            "diff": observability.get("diff", {}),
            "insights": insight_seed,
            "local_summary": local_summary,
        }
        return json.dumps(signature_payload, sort_keys=True, separators=(",", ":"))

    def _should_attempt_remote(
        self,
        *,
        signature: str,
        force_external: bool,
    ) -> tuple[bool, dict[str, object]]:
        if force_external:
            return True, {}

        now = time.time()
        since_last_attempt = now - self._last_remote_attempt_at

        if (
            self._last_remote_signature
            and signature == self._last_remote_signature
            and since_last_attempt < self.repeated_state_ttl_seconds
        ):
            remaining = max(0, int(self.repeated_state_ttl_seconds - since_last_attempt))
            return (
                False,
                {
                    "enabled": True,
                    "attempted": False,
                    "status": "skipped_unchanged",
                    "message": f"Skipped remote call: no meaningful state change since last request. Retry in ~{remaining}s.",
                    "api_version": "",
                    "model": "",
                },
            )

        if self._last_remote_attempt_at and since_last_attempt < self.external_min_interval_seconds:
            remaining = max(0, int(self.external_min_interval_seconds - since_last_attempt))
            return (
                False,
                {
                    "enabled": True,
                    "attempted": False,
                    "status": "cooldown",
                    "message": f"Skipped remote call: cooldown active. Retry in ~{remaining}s.",
                    "api_version": "",
                    "model": "",
                },
            )

        return True, {}

    @staticmethod
    def _build_local_summary(*, observability: dict, engine_insights: list[dict]) -> str:
        diff = observability.get("diff", {})

        proc_diff = diff.get("processes", {})
        if proc_diff.get("added"):
            names = ", ".join(proc_diff["added"][:3])
            return (
                f"Significant process change detected. Newly observed process(es): {names}. "
                "Monitor CPU and memory impact over the next 30 seconds."
            )

        cpu = diff.get("cpu")
        if cpu and abs(cpu.get("delta", 0.0)) > 20:
            direction = "increase" if cpu["delta"] > 0 else "decrease"
            return (
                f"Major CPU {direction} detected ({cpu.get('old')} -> {cpu.get('new')}). "
                "Investigate active high-load processes and rebalance workload priority."
            )

        memory = diff.get("memory")
        if memory and abs(memory.get("delta", 0.0)) > 15:
            direction = "increase" if memory["delta"] > 0 else "decrease"
            return (
                f"Major memory {direction} detected ({memory.get('old')} -> {memory.get('new')}). "
                "Inspect memory-heavy processes and reclaim non-critical workloads if needed."
            )

        if engine_insights:
            first = engine_insights[0]
            recommendation = first.get("recommendation", "Continue monitoring trend stability.")
            return f"{first.get('message', 'Meaningful change detected.')} Recommendation: {recommendation}"

        return "Meaningful change detected. Continue monitoring for sustained trend shifts."

    @staticmethod
    def _query_gemini(*, gemini_key: str, observability: dict, local_summary: str) -> dict[str, object]:
        prompt = (
            "You are monitoring live system metrics. Provide one concise operational insight "
            "and one recommendation. Keep under 40 words.\n"
            f"Observability payload: {json.dumps(observability, separators=(',', ':'))}\n"
            f"Local summary: {local_summary}"
        )

        req_payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 120,
            },
        }

        best_error = {
            "status": "unavailable",
            "message": "No Gemini endpoint succeeded; using local summary.",
            "api_version": "",
            "model": "",
        }

        error_priority = {
            "rate_limited": 5,
            "http_error": 4,
            "network_error": 3,
            "model_unavailable": 2,
            "unavailable": 1,
        }

        def choose_error(current: dict[str, object], candidate: dict[str, object]) -> dict[str, object]:
            current_rank = error_priority.get(str(current.get("status", "unavailable")), 0)
            candidate_rank = error_priority.get(str(candidate.get("status", "unavailable")), 0)
            return candidate if candidate_rank >= current_rank else current

        for api_version, model_name in GEMINI_ENDPOINT_CANDIDATES:
            endpoint = (
                f"https://generativelanguage.googleapis.com/{api_version}/models/"
                f"{model_name}:generateContent?key={gemini_key}"
            )

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(req_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            try:
                with urllib.request.urlopen(req, timeout=3.0) as response:
                    body = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                # Model availability varies by account/region; try the next candidate.
                if exc.code == 404:
                    logger.debug("Gemini model unavailable (%s/%s)", api_version, model_name)
                    best_error = choose_error(
                        best_error,
                        {
                            "status": "model_unavailable",
                            "message": f"Gemini model unavailable for account/region: {model_name} ({api_version}).",
                            "api_version": api_version,
                            "model": model_name,
                        },
                    )
                    continue
                if exc.code == 429:
                    logger.debug("Gemini rate limited for %s/%s", api_version, model_name)
                    best_error = choose_error(
                        best_error,
                        {
                            "status": "rate_limited",
                            "message": f"Gemini rate limit or quota exceeded (HTTP 429) for {model_name} ({api_version}).",
                            "api_version": api_version,
                            "model": model_name,
                        },
                    )
                    continue
                logger.debug("Gemini HTTP error for %s/%s: %s", api_version, model_name, exc)
                best_error = choose_error(
                    best_error,
                    {
                        "status": "http_error",
                        "message": f"Gemini HTTP error {exc.code} for {model_name} ({api_version}).",
                        "api_version": api_version,
                        "model": model_name,
                    },
                )
                continue
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                logger.debug("Gemini summary unavailable for %s/%s: %s", api_version, model_name, exc)
                best_error = choose_error(
                    best_error,
                    {
                        "status": "network_error",
                        "message": f"Gemini request failed for {model_name} ({api_version}): {exc}",
                        "api_version": api_version,
                        "model": model_name,
                    },
                )
                continue

            candidates = body.get("candidates") or []
            if not candidates:
                best_error = choose_error(
                    best_error,
                    {
                        "status": "http_error",
                        "message": f"Gemini returned no candidates for {model_name} ({api_version}).",
                        "api_version": api_version,
                        "model": model_name,
                    },
                )
                continue

            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
            )
            if not parts:
                best_error = choose_error(
                    best_error,
                    {
                        "status": "http_error",
                        "message": f"Gemini returned empty content for {model_name} ({api_version}).",
                        "api_version": api_version,
                        "model": model_name,
                    },
                )
                continue

            text = parts[0].get("text", "").strip()
            if text:
                return {
                    "text": text,
                    "status": "success",
                    "message": "Gemini summary generated successfully.",
                    "api_version": api_version,
                    "model": model_name,
                }

        return {
            "text": None,
            "status": best_error["status"],
            "message": best_error["message"],
            "api_version": best_error["api_version"],
            "model": best_error["model"],
        }
