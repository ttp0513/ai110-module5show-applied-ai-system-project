"""Orchestrate preference interpretation, validation, and safe fallback."""

import logging

from pydantic import ValidationError

from app.ai.providers import (
    DemoPreferenceProvider,
    PreferenceExtractionProvider,
    PreferenceProviderError,
)
from app.models.preference_interpretation import PreferenceInterpretationResponse

logger = logging.getLogger(__name__)


class PreferenceInterpretationService:
    """Produce reviewable domain preferences without trusting model output."""

    def __init__(
        self,
        primary: PreferenceExtractionProvider,
        fallback: DemoPreferenceProvider,
        initial_fallback_reason: str | None = None,
    ) -> None:
        self.primary = primary
        self.fallback = fallback
        self.initial_fallback_reason = initial_fallback_reason

    async def interpret(self, prompt: str) -> PreferenceInterpretationResponse:
        provider = self.primary
        used_fallback = self.initial_fallback_reason is not None
        fallback_reason = self.initial_fallback_reason
        try:
            extraction = await provider.extract(prompt)
        except (PreferenceProviderError, ValidationError):
            provider = self.fallback
            extraction = await provider.extract(prompt)
            used_fallback = True
            fallback_reason = "AI provider unavailable or invalid; local rules used."

        try:
            preferences = extraction.to_user_preferences()
        except ValidationError:
            preferences = None

        values = extraction.model_dump(
            exclude={"interpretation_summary", "ambiguities"},
        )
        extracted_fields = [
            name for name, value in values.items() if value is not None and value != []
        ]
        logger.info(
            "preference_interpretation_completed provider=%s fallback=%s "
            "prompt_length=%s extracted_fields=%s",
            provider.name,
            used_fallback,
            len(prompt),
            len(extracted_fields),
        )
        return PreferenceInterpretationResponse(
            preferences=preferences,
            interpretation_summary=extraction.interpretation_summary,
            ambiguities=extraction.ambiguities,
            extracted_fields=extracted_fields,
            provider=provider.name,
            model=provider.model,
            used_fallback=used_fallback,
            fallback_reason=fallback_reason,
        )
