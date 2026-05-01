import asyncio
from datetime import datetime
from app.models import MatchResult
from app.data.commodity_catalog import catalog

async def mock_llm(desc: str):
    for item in catalog:
        if item["description"] in desc.lower():
            return MatchResult(
                matched_code=item["hs_code"],
                match_confidence=0.8,
                rationale="keyword match",
                fallback_used=True,
                source="catalog_exact"
            )

    return MatchResult(
        matched_code=None,
        match_confidence=0.5,
        rationale="no match",
        fallback_used=False,
        source="no_match"
    )

async def match_envelope(envelope):
    threshold = envelope.processing_instructions.confidence_threshold
    code = envelope.extraction.get("commodity_code")

    try:
        if code and code.confidence >= threshold:
            return envelope

        desc = envelope.extraction["commodity_desc"].value

        result = await asyncio.wait_for(mock_llm(desc), timeout=10)

        envelope.matching_results = result

        if result.match_confidence < 0.7:
            envelope.decision.route = "hitl_review"

        envelope.audit.append({
            "timestamp": datetime.utcnow().isoformat(),
            "service": "matching_service",
            "action": "match",
            "envelope_id": envelope.envelope_id,
            "result": result.source,
            "details": result.dict()
        })

    except Exception:
        envelope.matching_results = MatchResult(
            matched_code=None,
            match_confidence=0,
            rationale="LLM failure",
            fallback_used=False,
            source="no_match"
        )
        envelope.decision.route = "hitl_review"

    return envelope