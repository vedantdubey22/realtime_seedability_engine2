import numpy as np
from products.ctt import compute_swd, compute_moisture_proxy
from products.cloud_depth import compute_cloud_depth
from products.lwp import compute_lwp_proxy
from products.growth import compute_growth_rate
from products.cloud_mask import compute_cloud_mask
from products.seedability import decide_seedability


def run_seedability_engine(data: dict) -> dict:
    print("\n" + "=" * 50)
    print("🔬 RUNNING SEEDABILITY ENGINE")
    print("=" * 50)

    ctt_c      = data["ctt_c"]
    ctt_prev_c = data["ctt_prev_c"]
    bt08       = data["bt08"]
    bt13       = data["bt13"]
    bt14       = data["bt14"]

    depth_km       = compute_cloud_depth(ctt_c)
    lwp_score      = compute_lwp_proxy(bt08, bt13)
    growth         = compute_growth_rate(ctt_c, ctt_prev_c, time_interval_min=10.0)
    swd            = compute_swd(bt13, bt14)
    moisture_proxy = compute_moisture_proxy(bt08, bt13)
    cloud_mask     = compute_cloud_mask(ctt_c, lwp_score)

    flag = decide_seedability(ctt_c, growth, swd, depth_km, lwp_score, cloud_mask)

    return {
        "ctt_c":          ctt_c,
        "depth_km":       depth_km,
        "lwp_score":      lwp_score,
        "growth":         growth,
        "swd":            swd,
        "moisture_proxy": moisture_proxy,
        "cloud_mask":     cloud_mask,
        "flag":           flag,
    }