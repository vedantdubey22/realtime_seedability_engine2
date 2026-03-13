
import numpy as np


def decide_seedability(ctt_c, growth, swd, depth_km, lwp_score, cloud_mask):
    """
    REAL-TIME PHYSICALLY ALIGNED SEEDABILITY DECISION ENGINE
    Strictly aligned to document:

        2  → GREEN  (High Potential)
        1  → AMBER  (Marginal / Watch)
        0  → GRAY   (Do Not Seed)
       -1  → NONE   (Unclassified cloud)
    """

    # -------------------------------------------------
    # Initialization
    # -------------------------------------------------
    seed = np.full(ctt_c.shape, -1, dtype=np.int8)

    valid = ~np.isnan(ctt_c)

    # -------------------------------------------------
    # Cloud mask boolean conversion
    # -------------------------------------------------
    if cloud_mask.dtype == bool:
        cloud_bool = cloud_mask
    else:
        cloud_bool = np.nan_to_num(cloud_mask) > 0.5

    is_cloud = cloud_bool & valid

    # -------------------------------------------------
    # 🔬 Diagnostics
    # -------------------------------------------------
    print("\n🔬 Decision Diagnostics:")

    if np.count_nonzero(valid) > 0:
        print("  SWD Mean:", np.nanmean(swd))
        print("  % SWD > 1.5 (Ice dominated):",
              100*np.count_nonzero(swd > 1.5)/np.count_nonzero(~np.isnan(swd)))

        print("  Growth Mean:", np.nanmean(growth))
        print("  % Growth >= 2:",
              100*np.count_nonzero(growth >= 2.0)/np.count_nonzero(~np.isnan(growth)))

        print("  % CTT <= -10:",
              100*np.count_nonzero(ctt_c <= -10.0)/np.count_nonzero(valid))

    # =================================================
    # 🟢 GREEN — HIGH POTENTIAL (STRICT DOC MATCH)
    # =================================================
    green_mask = (
        is_cloud &
        (ctt_c < -10.0) &              # cold cloud top
        (depth_km > 2.5) &             # deep cloud
        (growth >= 2.0) &              # strong cooling/updraft
        (lwp_score >= 0.6) &           # strong liquid water
        (swd < 0.6)                    # liquid-dominated phase
    )

    seed[green_mask] = 2

    # =================================================
    # 🟠 AMBER — MARGINAL / WATCH
    # =================================================
    amber_mask = (
        is_cloud &
        (seed == -1) &
        (ctt_c > -10.0) & (ctt_c <= -5.0) &   # moderate cold
        (depth_km >= 1.0) & (depth_km <= 2.5) &
        (growth > 0.5) &                      # weak updraft allowed
        (lwp_score >= 0.3) &
        (swd < 1.5)                           # mixed phase allowed
    )

    seed[amber_mask] = 1

    # =================================================
    # ⚪ GRAY — DO NOT SEED (STRICT DOC CONDITIONS)
    # =================================================
    gray_mask = (
        is_cloud &
        (seed == -1) &
        (
            (ctt_c > -5.0) |          # too warm
            (depth_km < 1.0) |        # very shallow
            (lwp_score < 0.3) |       # weak liquid
            (swd > 1.5) |             # ice-dominated (>80% ice proxy)
            (growth <= 0)             # no active updraft
        )
    )

    seed[gray_mask] = 0

    # =================================================
    # Final Diagnostics
    # =================================================
    total_cloud = np.count_nonzero(is_cloud)

    print("\n📊 Seedability Breakdown (Doc-Aligned):")

    if total_cloud > 0:

        n_green = np.count_nonzero((seed == 2) & is_cloud)
        n_amber = np.count_nonzero((seed == 1) & is_cloud)
        n_gray  = np.count_nonzero((seed == 0) & is_cloud)
        n_none  = np.count_nonzero((seed == -1) & is_cloud)

        print(f"  🟢 GREEN : {100*n_green/total_cloud:.2f}%")
        print(f"  🟠 AMBER : {100*n_amber/total_cloud:.2f}%")
        print(f"  ⚪ GRAY  : {100*n_gray/total_cloud:.2f}%")
        print(f"  ⬜ NONE  : {100*n_none/total_cloud:.2f}%")

    return seed

