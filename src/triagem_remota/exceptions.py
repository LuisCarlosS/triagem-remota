class TriageValidationError(ValueError):
    """Entrada inválida para triagem."""


class CaseNotFoundError(LookupError):
    """Caso sintético não encontrado."""