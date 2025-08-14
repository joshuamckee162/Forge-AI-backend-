from flask import Flask, request, jsonify
from models import VehicleConfig
from blueprints import generate_blueprints, compile_vehicle_blueprint
from costing import estimate_costs
from marketing import marketing_pack
from physics import simulate_drive, quick_stats

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "autogenesis-ai"})

# ---- Blueprints ----
@app.post("/blueprints")
def blueprints():
    data = request.get_json(force=True) or {}
    cfg = VehicleConfig(**data)
    parts = generate_blueprints(cfg)
    vehicle = compile_vehicle_blueprint(cfg, parts)
    return jsonify({"parts": parts, "vehicle": vehicle})

# ---- Cost Estimator ----
@app.post("/cost-estimation")
def cost_estimation():
    data = request.get_json(force=True) or {}
    cfg = VehicleConfig(**data)
    costs = estimate_costs(cfg)
    return jsonify(costs)

# ---- Marketing Pack ----
@app.post("/marketing")
def marketing():
    data = request.get_json(force=True) or {}
    cfg = VehicleConfig(**data)
    pack = marketing_pack(cfg)
    return jsonify(pack)

# ---- Test Drive Simulator ----
@app.post("/testdrive")
def testdrive():
    payload = request.get_json(force=True) or {}
    cfg = VehicleConfig(**payload.get("config", payload))
    seconds = float(payload.get("seconds", 20))
    dt = float(payload.get("dt", 0.05))
    terrain = payload.get("terrain", "urban")
    grade_pct = float(payload.get("grade_pct", 0.0))
    wind_mps = float(payload.get("wind_mps", 0.0))
    tgt_speed_kmh = float(payload.get("target_speed_kmh", 120))
    driving_mode = payload.get("mode", "mixed")  # "accel" | "cruise" | "mixed"

    telemetry = simulate_drive(
        cfg, seconds=seconds, dt=dt, terrain=terrain, grade_pct=grade_pct,
        wind_mps=wind_mps, target_speed_kmh=tgt_speed_kmh, mode=driving_mode
    )
    stats = quick_stats(cfg, telemetry)
    return jsonify({"telemetry": telemetry, "stats": stats})

if __name__ == "__main__":
    app.run(port=8000)
