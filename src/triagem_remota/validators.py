from triagem_remota.exceptions import TriageValidationError
from triagem_remota.models import IntakeCase


def validate_case_payload(data: dict) -> IntakeCase:
    """Valida e instancia um caso; converte erros Pydantic em TriageValidationError."""
    try:
        return IntakeCase.model_validate(data)
    except Exception as exc:
        raise TriageValidationError(str(exc)) from exc