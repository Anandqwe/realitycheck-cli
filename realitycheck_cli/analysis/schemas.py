from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class ClauseCategory(str, Enum):
    NON_COMPETE = "NON_COMPETE"
    IP_TRANSFER = "IP_TRANSFER"
    LIABILITY = "LIABILITY"
    TERMINATION = "TERMINATION"
    FINANCIAL_RISK = "FINANCIAL_RISK"
    PRIVACY = "PRIVACY"
    NEUTRAL = "NEUTRAL"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BenefitsParty(str, Enum):
    CLIENT = "CLIENT"
    VENDOR = "VENDOR"
    MUTUAL = "MUTUAL"
    UNKNOWN = "UNKNOWN"


class SignalType(str, Enum):
    VAGUE_LANGUAGE = "VAGUE_LANGUAGE"
    MISSING_PROTECTION = "MISSING_PROTECTION"
    ONE_SIDED_RIGHT = "ONE_SIDED_RIGHT"
    LIABILITY_EXPANSION = "LIABILITY_EXPANSION"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ClauseSignal(BaseModel):
    type: SignalType
    label: str
    severity: Severity
    evidence: str


class Clause(BaseModel):
    contract_id: str
    clause_id: str
    title: str
    page: int = Field(ge=1)
    text: str


class ClauseAnalysis(BaseModel):
    contract_id: str
    clause_id: str
    title: str
    page: int = Field(ge=1)
    text: str
    category: ClauseCategory
    category_confidence: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    benefits_party: BenefitsParty
    signals: list[ClauseSignal] = Field(default_factory=list)
    missing_protections: list[str] = Field(default_factory=list)
    rewrite_suggestion: str = ""
    negotiation_points: list[str] = Field(default_factory=list)
    explanation: str = ""


class ContractRiskSummary(BaseModel):
    contract_id: str
    overall_risk_score: int = Field(ge=1, le=100)
    power_imbalance_score: int = Field(ge=0, le=100)
    ambiguity_index: int = Field(ge=0, le=100)
    protection_coverage_score: int = Field(ge=0, le=100)
    leverage_index: int = Field(ge=0, le=100)
    category_scores: dict[str, int] = Field(default_factory=dict)
    weighted_contributions: dict[str, float] = Field(default_factory=dict)
    high_risk_clause_ids: list[str] = Field(default_factory=list)
    missing_protections: list[str] = Field(default_factory=list)


class ContractAnalysisResult(BaseModel):
    contract_id: str
    source_path: str
    clauses: list[ClauseAnalysis] = Field(default_factory=list)
    summary: ContractRiskSummary
    negotiation_email: str


class DeltaType(str, Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"


class ClauseDelta(BaseModel):
    delta_type: DeltaType
    baseline_clause_id: str | None = None
    revised_clause_id: str | None = None
    risk_delta: int
    reason: str


class ComparisonFlag(BaseModel):
    type: str
    clause_id: str
    description: str
    severity: Severity


class ComparisonResult(BaseModel):
    baseline_contract_id: str
    revised_contract_id: str
    baseline_overall_risk: int = Field(ge=1, le=100)
    revised_overall_risk: int = Field(ge=1, le=100)
    overall_risk_delta: int
    baseline_leverage_index: int = Field(ge=0, le=100)
    revised_leverage_index: int = Field(ge=0, le=100)
    leverage_delta: int = Field(ge=-100, le=100)
    deltas: list[ClauseDelta] = Field(default_factory=list)
    flags: list[ComparisonFlag] = Field(default_factory=list)

