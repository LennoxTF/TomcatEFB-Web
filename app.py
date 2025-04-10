from flask import Flask, request, jsonify, render_template
import calc

app = Flask(__name__)

# Mapping of functions and parameters (same as in your GUI)
functions = {
    "Navigation": {
        "groundspeed": ["Distance (nm)", "Time (h)"],
        "time_to_dest": ["Distance (nm)", "Groundspeed (kt)"],
        "distance": ["Groundspeed (kt)", "Time (h)"],
        "ETA": ["Distance (nm)", "Groundspeed (kt)"],
        "required_groundspeed_to_waypoint": ["Distance (nm)", "Current Time (HH:MM)", "TOT (HH:MM)"]
    },
    "Climb / Descent": {
        "time_to_climb": ["Altitude Diff (ft)", "Climb Rate (ft/min)"],
        "climb_rate": ["Altitude Diff (ft)", "Time (min)"],
        "top_of_descent": ["Altitude Diff (ft)", "Gradient (e.g. 3)"],
        "descent_angle": ["Altitude Diff (ft)", "Distance (nm)"],
        "descent_rate_req": ["Altitude Diff (ft)", "Distance (nm)", "GS (kt)"],
        "descent_profile": ["Altitude Diff (ft)", "GS (kt)", "Target Distance (nm)"]
    },
    "Wind & Heading": {
        "WCA": ["TAS (kt)", "Wind Angle (°)", "Wind Speed (kt)"],
        "true_hdg": ["Track (°)", "WCA (°)"],
        "mag_hdg": ["True Heading (°)", "Mag. Deviation (°)"]
    },
    "Fuel & Range": {
        "fuel_per_nm": ["GS (kt)", "Fuel Flow (lb/h)"],
        "ranges": ["Fuel (lb)", "Fuel Rate (lb/h)", "GS (kt)"],
        "fuel_at_fix": ["Current Fuel (lb)", "Speed (kt)", "Fuel Flow (lb/h)", "Distance (nm)"],
        "endurance": ["Fuel (lb)", "Fuel Flow (lb/h)"]
    },
    "Temperature / ISA": {
        "isa_temperature": ["Altitude (ft)"],
        "isa_deviation": ["Current Temp (°C)", "Altitude (ft)"]
    }
}

@app.route("/")
def index():
    return render_template("index.html", functions=functions)

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.json
    func_name = data.get("function")
    args = data.get("args", [])

    try:
        func = getattr(calc, func_name)
        parsed_args = []

        for val in args:
            if isinstance(val, str) and ":" in val:
                parsed_args.append(val)
            else:
                parsed_args.append(float(val))

        result = func(*parsed_args)

        if isinstance(result, dict):
            return jsonify({"result": result})
        if isinstance(result, str):
            return jsonify({"result": result})
        if result is None:
            return jsonify({"error": "Target time exceeded!"})

        return jsonify({"result": round(result, 2)})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)

