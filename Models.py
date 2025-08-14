from pydantic import BaseModel, Field
from typing import Literal

class VehicleConfig(BaseModel):
    type: Literal["civilian","military","hypercar"] = "civilian"
    power: Literal["gas","diesel","electric","solar"] = "gas"
    sixBySix: bool = False
    armor: float = Field(0, ge=0, le=1)                # 0..1 normalized
    wheelScale: float = Field(1.0, ge=0.8, le=1.6)     # tire diameter scale
    lift: float = Field(0.0, ge=0.0, le=0.5)
