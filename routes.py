"""
routes.py — 3 ML API routes for KrushiCare

/api/predict-disease  → Leaf disease detection (CNN)
/api/recommend-crop   → Crop recommendation (Random Forest)
/api/rotation-plan    → Crop rotation plan (ML)

Abhi MOCK responses hain.
Jab friend ke trained models aayenge:
  1. "MODEL LOADING" section mein models load karo
  2. "TODO: Real model" wale comments uncomment karo
  Baaki code same rahega!
"""

from flask import Blueprint, request, jsonify
from auth import token_required

api_bp = Blueprint("api", __name__)


# ══════════════════════════════════════════════════════════════════════════════
# MODEL LOADING — Yahan friend ke models aayenge
# ══════════════════════════════════════════════════════════════════════════════

disease_model  = None   # CNN  .h5  file
crop_model     = None   # RF   .pkl file
rotation_model = None   # ML   .pkl file

# Jab models ready ho, yeh uncomment karo:
#
# import pickle
# import numpy as np
# import tensorflow as tf
# from PIL import Image
# import io
#
# disease_model  = tf.keras.models.load_model("models/disease_cnn.h5")
# with open("models/crop_rf.pkl",   "rb") as f: crop_model     = pickle.load(f)
# with open("models/rotation.pkl",  "rb") as f: rotation_model = pickle.load(f)
#
# DISEASE_CLASSES = [...]   # friend se list lo
# CROP_CLASSES    = [...]
#
# def preprocess_image(file, target_size=(224, 224)):
#     img = Image.open(io.BytesIO(file.read())).convert("RGB").resize(target_size)
#     arr = np.array(img) / 255.0
#     return np.expand_dims(arr, axis=0)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 1 — POST /api/predict-disease
# ══════════════════════════════════════════════════════════════════════════════

@api_bp.route("/predict-disease", methods=["POST"])
@token_required
def predict_disease(current_user):
    """
    Frontend se aata hai (multipart/form-data):
      image      — leaf ki photo
      crop_type  — optional (tomato, wheat, etc.)
    """
    if "image" not in request.files:
        return jsonify({"success": False, "message": "Leaf image upload karo"}), 400

    image_file = request.files["image"]
    crop_type  = request.form.get("crop_type", "")

    # TODO: Real model yahan use karo
    # arr = preprocess_image(image_file)
    # pred = disease_model.predict(arr)
    # disease_name = DISEASE_CLASSES[np.argmax(pred)]
    # confidence   = float(np.max(pred))

    # ── MOCK ──────────────────────────────────────────────────────────────────
    return jsonify({
        "success":     True,
        "disease":     "Tomato Late Blight",
        "confidence":  0.91,
        "severity":    "Moderate",
        "description": "Phytophthora infestans fungus ke kaaran. Dark brown spots with yellow border dikhai dete hain.",
        "treatment": [
            "Mancozeb 75% WP @ 2g/litre spray karo",
            "Infected leaves turant hatao aur jalao",
            "Overhead irrigation band karo",
            "Copper-based fungicide 10 din baad dobara spray karo"
        ],
        "crop_type": crop_type or "Auto-detected",
    })


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 2 — POST /api/recommend-crop
# ══════════════════════════════════════════════════════════════════════════════

@api_bp.route("/recommend-crop", methods=["POST"])
@token_required
def recommend_crop(current_user):
    """
    Frontend se aata hai (multipart/form-data):
      image       — field/soil photo (optional)
      N, P, K     — nutrients (mg/kg)
      pH          — soil pH
      temperature — °C
      humidity    — %
      rainfall    — mm/year
    """
    try:
        N    = float(request.form.get("N",           60))
        P    = float(request.form.get("P",           50))
        K    = float(request.form.get("K",           45))
        pH   = float(request.form.get("pH",          6.8))
        temp = float(request.form.get("temperature", 26))
        hum  = float(request.form.get("humidity",    70))
        rain = float(request.form.get("rainfall",    900))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Parameter values sahi nahi hain"}), 400

    # TODO: Real model
    # features = [N, P, K, pH, temp, hum, rain]
    # if "image" in request.files:
    #     img_feat = extract_image_features(request.files["image"])
    #     features += img_feat
    # probs    = crop_model.predict_proba([features])[0]
    # top_crops = sorted(zip(CROP_CLASSES, probs), key=lambda x: -x[1])[:5]

    # ── MOCK ──────────────────────────────────────────────────────────────────
    return jsonify({
        "success":           True,
        "top_crop":          "Wheat",
        "scientific_name":   "Triticum aestivum",
        "suitability_score": 88,
        "reason":            f"pH {pH} aur N={N} mg/kg wheat ke liye optimal conditions hain.",
        "alternatives": [
            {"crop": "Chickpea", "score": 79},
            {"crop": "Mustard",  "score": 72},
            {"crop": "Soybean",  "score": 61},
            {"crop": "Rice",     "score": 38},
        ],
        "tips": [
            "Oct 15 – Nov 15 ke beech baao (Rabi season)",
            "120 kg N/ha daalein — 50% baai pe, 50% pehli sinchai pe",
            "CRI, jointing aur grain filling pe sinchai zaroori hai",
            "Recommended variety: GW 322 ya HI 8498",
        ],
        "input_params": {"N": N, "P": P, "K": K, "pH": pH,
                         "temperature": temp, "humidity": hum, "rainfall": rain},
    })


# ══════════════════════════════════════════════════════════════════════════════
# ROUTE 3 — POST /api/rotation-plan
# ══════════════════════════════════════════════════════════════════════════════

@api_bp.route("/rotation-plan", methods=["POST"])
@token_required
def rotation_plan(current_user):
    """
    Frontend se aata hai (multipart/form-data):
      image         — current crop/field photo (optional)
      current_crop  — abhi jo crop hai
      soil_type     — mitti ka type
      seasons       — kitne seasons ka plan chahiye
      goal          — maximize yield / restore soil / etc.
      area          — acres mein
    """
    current_crop = request.form.get("current_crop", "Wheat")
    soil_type    = request.form.get("soil_type",    "Black (Regur)")
    seasons      = int(request.form.get("seasons",  3))
    goal         = request.form.get("goal",         "Maximise yield")
    area         = float(request.form.get("area",   5))

    # TODO: Real model
    # features = encode_rotation_inputs(current_crop, soil_type, seasons, goal, area)
    # plan     = rotation_model.predict([features])

    # ── Simple rule-based mock (real model aane tak) ─────────────────────────
    RULES = {
        "Wheat":     ["Green Gram", "Maize"],
        "Rice":      ["Mustard",    "Chickpea"],
        "Maize":     ["Soybean",    "Wheat"],
        "Soybean":   ["Wheat",      "Sorghum"],
        "Cotton":    ["Wheat",      "Green Gram"],
        "Sugarcane": ["Wheat",      "Pulses"],
        "Potato":    ["Mustard",    "Green Gram"],
        "Tomato":    ["Wheat",      "Chickpea"],
    }
    next_crops = RULES.get(current_crop, ["Green Gram", "Maize"])
    sequence   = ([current_crop] + next_crops * 10)[:seasons]

    return jsonify({
        "success":  True,
        "strategy": f"{seasons}-Season Rotation Strategy",
        "summary":  (
            f"{current_crop} ke baad legume crop nitrogen fix karegi "
            f"(~80 kg N/ha), phir deep-rooted crop hardpan todegi. "
            f"Goal: {goal}."
        ),
        "rotation": [
            {"season": i + 1, "crop": crop}
            for i, crop in enumerate(sequence)
        ],
        "benefits": {
            "nitrogen_improvement": "+35–45 kg/ha (legume phase ke baad)",
            "fertilizer_saving":    "Season 3 mein ~30% kam fertiliser lagega",
            "recommended_additive": "Zinc sulphate 25 kg/ha — Maize se pehle daalein",
        },
        "input": {
            "current_crop": current_crop,
            "soil_type":    soil_type,
            "goal":         goal,
            "area_acres":   area,
        },
    })
