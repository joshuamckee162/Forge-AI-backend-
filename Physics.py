from typing import List, Dict
import numpy as np
from models import VehicleConfig

TERRAIN = {
    "urban":     {"mu": 0.95, "c_rr": 0.012},
    "highway":   {"mu": 0.92, "c_rr": 0.010},
    "offroad":   {"mu": 0.65, "c_rr": 0.018},
    "desert":    {"mu": 0.55, "c_rr": 0.028},
    "snow":      {"mu": 0.35, "c_rr": 0.035},
    "mud":       {"mu": 0.30, "c_rr": 0.045},
}

def vehicle_params(cfg: VehicleConfig):
    mass_base = 1600 if cfg.type == "hypercar" else 3500 if cfg.type == "military" else 2400
    armor_mass = cfg.armor * 800
    drivetrain_mass = 250 if cfg.sixBySix else 0
    mass = mass_base + armor_mass + drivetrain_mass  # kg

    power_kw = 450 if cfg.power == "electric" else 300 if cfg.power == "diesel" else 180 if cfg.power == "solar" else 260
    drag_cd = 0.28 if cfg.type == "hypercar" else 0.42
    area_m2 = 2.0 if cfg.type == "hypercar" else 2.8 * (1 + 0.05*cfg.lift)
    rho = 1.225
    frontal = 0.5 * rho * drag_cd * area_m2

    # Simple gearing curve: force tapers with speed to keep P ~ const
    max_wheel_force = (power_kw * 1000) / 18.0  # N near 18 m/s
    if cfg.sixBySix:
        max_wheel_force *= 1.08  # more contact & gearing

    regen_power_kw = 120 if cfg.power == "electric" else 0
    return dict(mass=mass, power_kw=power_kw, frontal=frontal,
                max_force=max_wheel_force, regen_kw=regen_power_kw)

def simulate_drive(
    cfg: VehicleConfig,
    seconds: float = 20.0,
    dt: float = 0.05,
    terrain: str = "urban",
    grade_pct: float = 0.0,
    wind_mps: float = 0.0,
    target_speed_kmh: float = 120.0,
    mode: str = "mixed"  # accel | cruise | mixed
) -> List[Dict]:
    params = vehicle_params(cfg)
    terr = TERRAIN.get(terrain, TERRAIN["urban"])

    g = 9.81
    n = int(seconds / dt)
    v = 0.0        # m/s
    s = 0.0        # m
    e_wh = 0.0     # Wh (positive draw, negative regen)
    wheel_radius = 0.34 * cfg.wheelScale
    mass = params["mass"]
    frontal = params["frontal"]
    F_max = params["max_force"]
    mu = terr["mu"]
    c_rr = terr["c_rr"]
    grade = grade_pct / 100.0

    v_target = target_speed_kmh / 3.6
    telemetry = []

    for i in range(n):
        # Resistive forces
        F_roll = c_rr * mass * g * np.cos(np.arctan(grade))
        F_grade = mass * g * grade
        # wind adds/subtracts from apparent air speed
        v_air = max(0.0, v + wind_mps)
        F_drag = frontal * v_air * v_air

        # Available traction limit
        F_trac_limit = mu * mass * g

        # Driver strategy
        if mode == "accel" or (mode == "mixed" and v < 0.9 * v_target):
            # throttle open but capped by power and traction
            F_wheel = min(F_max, F_trac_limit)
        elif mode == "cruise":
            # just enough to maintain target (PID-ish)
            dv = v_target - v
            F_wheel = np.clip(dv * mass * 0.4, -F_trac_limit, F_trac_limit)
        else:
            # mixed: hold near target
            dv = v_target - v
            F_wheel = np.clip(dv * mass * 0.6, -F_trac_limit, F_trac_limit)

        # Net longitudinal force
        F_net = F_wheel - (F_roll + F_grade + F_drag)

        # Power cap (cannot exceed motor/engine power)
        P_cap_w = params["power_kw"] * 1000.0
        if F_net * v > P_cap_w and v > 1e-3:
            F_net = P_cap_w / v

        # Regen if braking (negative wheel force) and EV
        if F_wheel < 0 and params["regen_kw"] > 0:
            P_regen = min(abs(F_wheel * v), params["regen_kw"] * 1000.0)
            e_wh -= (P_regen * dt) / 3600.0  # regen subtracts consumption

        # Physics integrate
        a = F_net / mass
        v = max(0.0, v + a * dt)
        s += v * dt

        # Instantaneous power draw (>0 draw, <0 regen)
        P_w = F_wheel * v
        e_wh += max(0.0, P_w) * dt / 3600.0  # Wh

        telemetry.append({
            "t": round((i+1)*dt, 3),
            "v_mps": v,
            "v_kmh": v * 3.6,
            "a_mps2": a,
            "s_m": s,
            "F_wheel_N": F_wheel,
            "F_drag_N": F_drag,
            "F_roll_N": F_roll,
            "F_grade_N": F_grade,
            "e_Wh": e_wh
        })

    return telemetry

def quick_stats(cfg: VehicleConfig, telemetry: List[Dict]):
    v = np.array([p["v_mps"] for p in telemetry])
    t = np.array([p["t"] for p in telemetry])

    # 0-60 mph
    target = 60 * 0.44704
    idx = np.where(v >= target)[0]
    zero_to_sixty = float(t[idx[0]]) if len(idx) else None

    # 100-0 km/h braking (estimate using mu)
    mu = TERRAIN["urban"]["mu"] if not cfg.tacticalLights else 0.85
    g = 9.81
    v0 = 100/3.6
    d_brake = (v0*v0)/(2*mu*g)

    # energy / fuel
    e_wh = telemetry[-1]["e_Wh"] if telemetry else 0.0
    if cfg.power == "electric":
        wh_per_km = e_wh / max(0.001, telemetry[-1]["s_m"]/1000.0)
        efficiency = {"wh_per_km": round(wh_per_km, 1)}
    else:
        # crude equivalent: convert Wh to liters using 8.9 kWh/l (diesel approx) or 8.6 (gas)
        kwh = e_wh / 1000.0
        kwh_per_l = 8.9 if cfg.power == "diesel" else 8.6
        liters = kwh / kwh_per_l
        l_per_100km = (liters / max(0.001, telemetry[-1]["s_m"]/1000.0)) * 100
        efficiency = {"l_per_100km_eq": round(l_per_100km, 2)}

    return {
        "zero_to_sixty_s": zero_to_sixty,
        "est_braking_distance_m_100_to_0": round(d_brake, 1),
        "efficiency": efficiency,
        "distance_m": telemetry[-1]["s_m"] if telemetry else 0.0,
        "top_speed_kmh": max([p["v_kmh"] for p in telemetry]) if telemetry else 0.0
          }
