"""
Quantity takeoff formulas. No cost calculation here (quantity-only phase).
Each function returns a dict of labeled results so app.py can display them directly.
"""

from utils.data import (
    CEMENT_BAG_VOLUME_M3, M3_TO_CFT, MORTAR_DRY_FACTOR, CONCRETE_DRY_FACTOR,
    BRICK_SIZE_M, BRICK_SIZE_WITH_JOINT_M, MORTAR_RATIOS, CONCRETE_RATIOS
)


def brick_volume_with_joint():
    b = BRICK_SIZE_WITH_JOINT_M
    return b["length"] * b["width"] * b["height"]


def brick_volume_plain():
    b = BRICK_SIZE_M
    return b["length"] * b["width"] * b["height"]


def calc_brickwork(length_m, height_m, thickness_m, quantity, mortar_ratio_key,
                    wastage_percent, opening_area_m2=0.0):
    """opening_area_m2: total area of doors/windows to subtract (W x H summed)."""
    gross_volume = length_m * height_m * thickness_m * quantity
    opening_volume = opening_area_m2 * thickness_m
    net_volume = max(gross_volume - opening_volume, 0)
    volume_with_wastage = net_volume * (1 + wastage_percent / 100)

    bv_joint = brick_volume_with_joint()
    bv_plain = brick_volume_plain()

    bricks_exact = volume_with_wastage / bv_joint
    mortar_wet_m3 = volume_with_wastage - (bricks_exact * bv_plain)
    mortar_wet_m3 = max(mortar_wet_m3, 0)
    mortar_dry_m3 = mortar_wet_m3 * MORTAR_DRY_FACTOR

    ratio = MORTAR_RATIOS[mortar_ratio_key]
    total_parts = ratio["cement"] + ratio["sand"]
    cement_m3 = mortar_dry_m3 * ratio["cement"] / total_parts
    sand_m3 = mortar_dry_m3 * ratio["sand"] / total_parts
    cement_bags = cement_m3 / CEMENT_BAG_VOLUME_M3

    return {
        "Gross Volume (m³)": round(gross_volume, 3),
        "Opening Volume (m³)": round(opening_volume, 3),
        "Net Volume (m³)": round(net_volume, 3),
        "Volume with Wastage (m³)": round(volume_with_wastage, 3),
        "Bricks Required (nos)": round(bricks_exact),
        "Mortar Wet Volume (m³)": round(mortar_wet_m3, 3),
        "Mortar Dry Volume (m³)": round(mortar_dry_m3, 3),
        "Cement Volume (m³)": round(cement_m3, 3),
        "Cement Bags (50kg)": round(cement_bags, 1),
        "Sand Volume (m³)": round(sand_m3, 3),
        "Sand Volume (cft)": round(sand_m3 * M3_TO_CFT, 1),
    }


def calc_plaster(length_m, height_m, quantity, thickness_mm, mortar_ratio_key,
                  wastage_percent, opening_area_m2=0.0):
    gross_area = length_m * height_m * quantity
    net_area = max(gross_area - opening_area_m2, 0)
    area_with_wastage = net_area * (1 + wastage_percent / 100)

    thickness_m = thickness_mm / 1000
    wet_volume = area_with_wastage * thickness_m
    dry_volume = wet_volume * MORTAR_DRY_FACTOR

    ratio = MORTAR_RATIOS[mortar_ratio_key]
    total_parts = ratio["cement"] + ratio["sand"]
    cement_m3 = dry_volume * ratio["cement"] / total_parts
    sand_m3 = dry_volume * ratio["sand"] / total_parts
    cement_bags = cement_m3 / CEMENT_BAG_VOLUME_M3

    return {
        "Gross Area (m²)": round(gross_area, 3),
        "Net Area (m²)": round(net_area, 3),
        "Area with Wastage (m²)": round(area_with_wastage, 3),
        "Wet Volume (m³)": round(wet_volume, 3),
        "Dry Volume (m³)": round(dry_volume, 3),
        "Cement Volume (m³)": round(cement_m3, 3),
        "Cement Bags (50kg)": round(cement_bags, 1),
        "Sand Volume (m³)": round(sand_m3, 3),
        "Sand Volume (cft)": round(sand_m3 * M3_TO_CFT, 1),
    }


def calc_concrete(length_m, width_m, thickness_m, quantity, mix_ratio_key, wastage_percent):
    wet_volume = length_m * width_m * thickness_m * quantity
    wet_volume_wastage = wet_volume * (1 + wastage_percent / 100)
    dry_volume = wet_volume_wastage * CONCRETE_DRY_FACTOR

    ratio = CONCRETE_RATIOS[mix_ratio_key]
    total_parts = ratio["cement"] + ratio["sand"] + ratio["aggregate"]
    cement_m3 = dry_volume * ratio["cement"] / total_parts
    sand_m3 = dry_volume * ratio["sand"] / total_parts
    aggregate_m3 = dry_volume * ratio["aggregate"] / total_parts
    cement_bags = cement_m3 / CEMENT_BAG_VOLUME_M3

    return {
        "Wet Volume (m³)": round(wet_volume_wastage, 3),
        "Dry Volume (m³)": round(dry_volume, 3),
        "Cement Volume (m³)": round(cement_m3, 3),
        "Cement Bags (50kg)": round(cement_bags, 1),
        "Sand Volume (m³)": round(sand_m3, 3),
        "Sand Volume (cft)": round(sand_m3 * M3_TO_CFT, 1),
        "Aggregate Volume (m³)": round(aggregate_m3, 3),
        "Aggregate Volume (cft)": round(aggregate_m3 * M3_TO_CFT, 1),
    }


def calc_steel(bar_dia_mm, bar_length_m, no_of_bars, wastage_percent):
    unit_weight_kg_per_m = (bar_dia_mm ** 2) / 162
    total_length_m = bar_length_m * no_of_bars
    total_weight_kg = total_length_m * unit_weight_kg_per_m * (1 + wastage_percent / 100)

    return {
        "Unit Weight (kg/m)": round(unit_weight_kg_per_m, 3),
        "Total Bar Length (m)": round(total_length_m, 2),
        "Total Steel Weight (kg)": round(total_weight_kg, 2),
        "Total Steel Weight (tons)": round(total_weight_kg / 1000, 3),
    }
