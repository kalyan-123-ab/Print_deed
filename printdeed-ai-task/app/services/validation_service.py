from datetime import datetime, timedelta
from fastapi import HTTPException

def validate_envelope(envelope):
    threshold = envelope.processing_instructions.confidence_threshold
    failed_fields = []
    missing_fields = []

    # Required fields
    for field in ["shipment_id", "recipient_name"]:
        if field not in envelope.extraction or not envelope.extraction[field].value:
            missing_fields.append(field)

    if not (
        envelope.extraction.get("commodity_code") or 
        envelope.extraction.get("commodity_desc")
    ):
        missing_fields.append("commodity")

    if missing_fields:
        raise HTTPException(status_code=422, detail={"missing_fields": missing_fields})

    # Confidence check
    for key, field in envelope.extraction.items():
        if field.confidence < threshold:
            failed_fields.append(key)

    # Date validation
    if "ship_date" in envelope.extraction:
        try:
            ship_date = datetime.fromisoformat(envelope.extraction["ship_date"].value)
            if ship_date > datetime.now() or ship_date < datetime.now() - timedelta(days=365):
                failed_fields.append("ship_date")
        except:
            failed_fields.append("ship_date")

    # Decision
    if not failed_fields:
        route = "auto_approve"
    elif envelope.processing_instructions.hitl_on_failure:
        route = "hitl_review"
    else:
        route = "rejected"

    envelope.decision.route = route
    envelope.validation_results = {"failed_fields": failed_fields}

    envelope.audit.append({
        "timestamp": datetime.utcnow().isoformat(),
        "service": "validation_service",
        "action": "validate",
        "envelope_id": envelope.envelope_id,
        "result": route,
        "details": failed_fields
    })

    return envelope