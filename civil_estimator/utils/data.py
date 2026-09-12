"""
Constants and reference data used by all calculators.
Civil teammate: this is the file to review/edit for formula accuracy.
"""

# --- Unit conversions ---
CEMENT_BAG_WEIGHT_KG = 50
CEMENT_DENSITY_KG_PER_M3 = 1440
CEMENT_BAG_VOLUME_M3 = CEMENT_BAG_WEIGHT_KG / CEMENT_DENSITY_KG_PER_M3  # ~0.03472 m3

M3_TO_CFT = 35.3147

# --- Wastage defaults (%) ---
WASTAGE_DEFAULTS = {
    "brickwork": 5,
    "plaster": 5,
    "concrete": 5,
    "steel": 3,
}

# --- Dry volume factors ---
MORTAR_DRY_FACTOR = 1.33      # wet mortar volume x this = dry material volume
CONCRETE_DRY_FACTOR = 1.54    # wet concrete volume x this = dry material volume

# --- Standard Pakistani brick size (with 10mm mortar joint), in meters ---
BRICK_SIZE_M = {"length": 0.228, "width": 0.114, "height": 0.076}
MORTAR_JOINT_M = 0.010
BRICK_SIZE_WITH_JOINT_M = {
    "length": BRICK_SIZE_M["length"] + MORTAR_JOINT_M,
    "width": BRICK_SIZE_M["width"] + MORTAR_JOINT_M,
    "height": BRICK_SIZE_M["height"] + MORTAR_JOINT_M,
}

# --- Mortar mix ratios (cement : sand) ---
MORTAR_RATIOS = {
    "1:3": {"cement": 1, "sand": 3},
    "1:4": {"cement": 1, "sand": 4},
    "1:6": {"cement": 1, "sand": 6},
}

# --- Concrete mix ratios (cement : sand : aggregate) ---
CONCRETE_RATIOS = {
    "1:1.5:3 (M20)": {"cement": 1, "sand": 1.5, "aggregate": 3},
    "1:2:4 (M15)": {"cement": 1, "sand": 2, "aggregate": 4},
    "1:3:6 (M10, PCC)": {"cement": 1, "sand": 3, "aggregate": 6},
    "1:4:8 (blinding)": {"cement": 1, "sand": 4, "aggregate": 8},
}

# --- Common steel bar diameters (mm) ---
STEEL_BAR_SIZES_MM = [6, 8, 10, 12, 16, 20, 25]

# --- Currency label for the optional cost-estimate fields ---
# This does NOT affect any quantity calculation above — it's only used to
# label the optional "unit rate" inputs in the UI. Change it if your rates
# are in a different currency.
CURRENCY_SYMBOL = "Rs."
