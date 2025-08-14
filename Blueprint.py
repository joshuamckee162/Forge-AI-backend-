from typing import List, Dict
from models import VehicleConfig

PARTS = [
    "Engine/Power Module",
    "Gearbox/Transmission",
    "Suspension (coil-over)",
    "6x6 Axle Pack",
    "Armor Panels",
    "Door & Security System",
    "Sleeper Kit Pod",
    "Cabin Electronics + 32\" TV",
    "Lighting (UV/IR/White)",
    "Snorkel + Mini Stacks",
    "Roof Dispenser Subsystem",
    "Resealing Tires Kit"
]

def generate_blueprints(cfg: VehicleConfig) -> List[Dict]:
    items = []
    for i, name in enumerate(PARTS, start=1):
        spec = {
            "application": cfg.type,
            "powertrain": cfg.power,
            "note": None
        }
        if name.startswith("Engine"):
            spec["output_hint_kw"] = 450 if cfg.power == "electric" else (300 if cfg.power == "diesel" else 260)
        if name.startswith("Suspension"):
            spec["lift_m"] = round(cfg.lift, 3)
            spec["wheel_scale"] = cfg.wheelScale
        if "Armor" in name:
            spec["armor_index_0_1"] = cfg.armor
        if "6x6" in name:
            spec["enabled"] = cfg.sixBySix
        if "Roof Dispenser" in name:
            spec["enabled"] = bool(cfg.pepperSpray)  # boolean only; no construction details
        if "Door & Security" in name:
            spec["tactile_deterrent"] = bool(cfg.tazerHandles)  # boolean only; no construction details
        if "Snorkel" in name:
            spec["enabled"] = cfg.snorkels

        items.append({
            "id": i,
            "name": name,
            "status": "Ready",
            "spec": spec
        })
    return items

def compile_vehicle_blueprint(cfg: VehicleConfig, parts: List[Dict]):
    return {
        "title": f"AutoGenesis {cfg.type} {'6x6' if cfg.sixBySix else '4x4'}",
        "summary": {
            "power": cfg.power,
            "armor_index_0_1": cfg.armor,
            "lift_m": cfg.lift,
            "wheel_scale": cfg.wheelScale
        },
        "parts": parts
    }
