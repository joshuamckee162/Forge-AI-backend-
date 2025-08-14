from models import VehicleConfig
from costing import estimate_costs

def marketing_pack(cfg: VehicleConfig):
    costs = estimate_costs(cfg)
    name = "HyperVolt" if cfg.type == "hypercar" else "Outrider" if cfg.type == "military" else "TrailForge"
    tagline = (
        "Zero to awe in 2.8." if cfg.type == "hypercar"
        else "Built for the mission. Ready for the unknown." if cfg.type == "military"
        else "From commute to cataclysm."
    )
    bullets = [
        f"Powertrain: {cfg.power}",
        f"Drive: {'6x6 triple-lock' if cfg.sixBySix else 'adaptive 4x4'}",
        f"Armor index: {round(cfg.armor, 2)}",
        f"Lift: {cfg.lift} m, wheel scale: {cfg.wheelScale}",
        f"Retail guidance: ${costs['retail']:,}"
    ]
    socials = [
        f"Meet {name}: AI-forged performance with {'6x6 traction' if cfg.sixBySix else 'smart 4x4'}.",
        "From blueprint to road test in minutes — Forge AI.",
        f"Armor {round(cfg.armor*10)} • Sleeper {('yes' if cfg.sleeper else 'no')} • {cfg.power} drivetrain."
    ]
    return {
        "productName": f"{name} {'6x6' if cfg.sixBySix else '4x4'}",
        "tagline": tagline,
        "blurb": f"Designed by Forge AI: {name} blends intelligent packaging with {cfg.power} power and "
                 f"{'six-wheel' if cfg.sixBySix else 'four-wheel'} traction. Tuned for {cfg.type} duties.",
        "bullets": bullets,
        "socials": socials
    }
