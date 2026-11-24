from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from triagem_remota.constants import COMORBIDADES_VALIDAS, SINTOMAS_VALIDOS


class NivelUrgencia(str, Enum):
    EMERGENCIA = "emergencia"
    URGENTE = "urgente"
    ROTINA = "rotina"
    AUTOCUIDADO = "autocuidado"


class SinaisVitais(BaseModel):
    frequencia_cardiaca_bpm: int = Field(..., ge=30, le=220)
    pressao_sistolica_mmhg: int = Field(..., ge=70, le=250)
    temperatura_celsius: float = Field(..., ge=34.0, le=42.0)
    saturacao_o2_percent: int | None = Field(default=None, ge=50, le=100)


class IntakeCase(BaseModel):
    case_id: str
    idade_anos: int = Field(..., ge=0, le=120)
    sintomas: list[str] = Field(..., min_length=1)
    sinais_vitais: SinaisVitais
    duracao_horas: float = Field(..., ge=0, le=24 * 365)
    comorbidades_simuladas: list[str] = Field(default_factory=list)
    timestamp_simulado: datetime | None = None
    rotulo_ouro: NivelUrgencia | None = None

    @field_validator("sintomas")
    @classmethod
    def validar_sintomas(cls, v: list[str]) -> list[str]:
        unknown = set(v) - SINTOMAS_VALIDOS
        if unknown:
            raise ValueError(f"Sintomas desconhecidos: {sorted(unknown)}")
        return v

    @field_validator("comorbidades_simuladas")
    @classmethod
    def validar_comorbidades(cls, v: list[str]) -> list[str]:
        if not v:
            return ["nenhuma"]
        unknown = set(v) - COMORBIDADES_VALIDAS
        if unknown:
            raise ValueError(f"Comorbidades desconhecidas: {sorted(unknown)}")
        return v


class ProcessingStep(BaseModel):
    etapa: str
    detalhe: str
    dados: dict[str, Any] = Field(default_factory=dict)


class TriageResult(BaseModel):
    case_id: str
    nivel_urgencia: NivelUrgencia
    encaminhamento: str
    resumo_plain_language: str
    confianca_heuristica: float = Field(..., ge=0.0, le=1.0)
    processing_steps: list[ProcessingStep]
    regras_disparadas: list[str]
    pontuacao_total: float = 0.0