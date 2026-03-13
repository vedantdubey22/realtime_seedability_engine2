

""" lets see"""
import numpy as np


def compute_cloud_mask(
    ctt_c: np.ndarray,
    lwp_score: np.ndarray | None = None
) -> np.ndarray:
    mask = np.full(ctt_c.shape, np.nan, dtype=np.float32)
    valid = ~np.isnan(ctt_c)

    # Mark ALL valid pixels as cloud — let seedability engine decide
    mask[valid] = 1.0

    print("\n☁️ Cloud mask: ALL valid pixels passed to seedability engine")
    print(f"  % Cloud pixels : {100 * np.count_nonzero(mask == 1.0) / np.count_nonzero(valid):.2f}%")

    return mask