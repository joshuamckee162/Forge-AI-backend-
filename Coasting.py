from models import VehicleConfig

FEATURE_COST = {
    "armor":       lambda v: v * 3500,
    "sixBySix":    lambda v: 9500 if v else 0,
    "resealTires": lambda v: 1800 if v else 0,
    "pepperSpray": lambda v: 1200 if v else 0,   # boolean only; no device details
    "tazerHandles":lambda v: 900  if v else 0,   # boolean only; no device details
    "sleeper":     lambda v: 6500 if v else 0,
    "snorkels":    lambda v: 1100 if v else 0,
    "tacticalLights": lambda v: 750 if v else 0
}

def estimate_costs(cfg: VehicleConfig):
    base = 48000 if cfg.type == "hypercar" else 42000 if cfg.type == "military" else 28000
    powertrain = 16000 if cfg.power == "electric" else 9000 if cfg.power == "diesel" else 22000 if cfg.power == "solar" else 8000
    labor = 120 * 65
    features = (
        FEATURE_COST["armor"](cfg.armor) +
        FEATURE_COST["sixBySix"](cfg.sixBySix) +
        FEATURE_COST["resealTires"](cfg.resealTires) +
        FEATURE_COST["pepperSpray"](cfg.pepperSpray) +
        FEATURE_COST["tazerHandles"](cfg.tazerHandles) +
        FEATURE_COST["sleeper"](cfg.sleeper) +
        FEATURE_COST["snorkels"](cfg.snorkels) +
        FEATURE_COST["tacticalLights"](cfg.tacticalLights)
    )
    complexity = (cfg.wheelScale - 1) * 3000 + cfg.lift * 2000
    subtotal = base + powertrain + labor + features + complexity
    overhead = subtotal * 0.12
    factory = round(subtotal + overhead)
    retail = round(factory * 1.65)
    fleet  = round(factory * 1.30)
    return {
        "factory": factory,
        "retail": retail,
        "fleet": fleet,
        "breakdown": {
            "base": base, "powertrain": powertrain, "labor": labor,
            "features": round(features), "complexity": round(complexity), "overhead": round(overhead)
        }
    }
