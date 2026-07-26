from pydantic import BaseModel
from typing import Literal

class PoolRiskAssessment(BaseModel):
    pool_name: str # e.g. "saturn SUSDAT" (project + symbol), not the raw pool UUID
    apy: float
    tvl_usd: float
    risk_level: Literal["low", "medium", "high"]
    reasons: list[str]
    recommended: bool

class PoolRiskAssessments(BaseModel):
    assessments: list[PoolRiskAssessment]