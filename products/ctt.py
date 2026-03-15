

# """3 bands show sir"""

# import numpy as np

# # =========================
# # Planck constants
# # =========================
# C1 = 1.191042e-5
# C2 = 1.4387752

# # Wavenumbers (cm-1) for Himawari-9 Bands
# # B08: 6.2 μm (Water Vapor), B13: 10.4 μm (Thermal), B14: 11.2 μm (Clean IR)
# WAVENUMBERS = {
#     "B08": 1612.9,
#     "B13": 961.5,
#     "B14": 892.8
# }

# def dn_to_bt(dn: np.ndarray, gain: float, offset: float, band: str = "B13") -> np.ndarray:
#     """ DN → Radiance → Brightness Temperature (Kelvin) """
#     v = WAVENUMBERS.get(band, 961.5)
#     rad = (dn * gain + offset) * 10.0
#     rad = np.where(np.isnan(rad), np.nan, np.maximum(rad, 1e-10))

#     with np.errstate(divide='ignore', invalid='ignore'):
#         bt_k = (C2 * v) / np.log((C1 * v**3 / rad) + 1.0)

#     # Dynamic scaling recovery
#     if np.nanmean(bt_k) < 200:
#         rad = (dn * gain + offset) * 100.0
#         bt_k = (C2 * v) / np.log((C1 * v**3 / rad) + 1.0)
#     return bt_k

# def compute_swd(bt13: np.ndarray, bt14: np.ndarray) -> np.ndarray:
    
#     """ 
#     Computes BT13 - BT14 (Split Window Difference).
#     Used to filter ice-dominated clouds (>80% ice phase).
#     """
#     swd = bt13 - bt14
#     swd = np.clip(swd, -5.0, 15.0)
#     return swd

# def compute_moisture_proxy(bt08: np.ndarray, bt13: np.ndarray) -> np.ndarray:
#     """
#     Computes BT08 - BT13 (Moisture Proxy).
#     Satisfies 'Sufficient mid-level moisture' for Amber Flags.
#     """
#     m_proxy = bt08 - bt13
#     print(f"💧 Moisture Proxy Mean: {np.nanmean(m_proxy):.2f}K")
#     return m_proxy

# def bt_to_ctt_c(bt_k: np.ndarray) -> np.ndarray:
#     """ Kelvin → Celsius """
#     return bt_k - 273.15








"""3 bands show sir"""

import numpy as np

# =========================
# Planck constants
# =========================
C1 = 1.191042e-5
C2 = 1.4387752

# Wavenumbers (cm-1) for Himawari-9 Bands
# B08: 6.2 μm (Water Vapor), B13: 10.4 μm (Thermal), B14: 11.2 μm (Clean IR)
WAVENUMBERS = {
    "B08": 1612.9,
    "B13": 961.5,
    "B14": 892.8
}

def dn_to_bt(dn: np.ndarray, gain: float, offset: float, band: str = "B13") -> np.ndarray:
    """ DN → Radiance → Brightness Temperature (Kelvin) """
    v = WAVENUMBERS.get(band, 961.5)
    rad = (dn * gain + offset) * 10.0
    rad = np.where(np.isnan(rad), np.nan, np.maximum(rad, 1e-10))

    with np.errstate(divide='ignore', invalid='ignore'):
        bt_k = (C2 * v) / np.log((C1 * v**3 / rad) + 1.0)

    # Dynamic scaling recovery
    if np.nanmean(bt_k) < 200:
        rad = (dn * gain + offset) * 100.0
        bt_k = (C2 * v) / np.log((C1 * v**3 / rad) + 1.0)
    return bt_k

def compute_swd(bt13: np.ndarray, bt14: np.ndarray) -> np.ndarray:
    """
    Split Window Difference with band bias correction.
    """

    raw_swd = bt13 - bt14

    # Remove systematic band bias
    bias = np.nanmean(raw_swd)

    swd = raw_swd - bias

    # Clip unrealistic values
    swd = np.clip(swd, -5.0, 5.0)

    print("\n🧊 SWD diagnostics (Bias Corrected):")
    print(f"  Raw Mean SWD   : {bias:.3f}")
    print(f"  Corrected Mean : {np.nanmean(swd):.3f}")
    print(f"  % SWD < 1.5    : {100*np.nanmean(swd < 1.5):.2f}%")

    return swd

def compute_moisture_proxy(bt08: np.ndarray, bt13: np.ndarray) -> np.ndarray:
    """
    Computes BT08 - BT13 (Moisture Proxy).
    Satisfies 'Sufficient mid-level moisture' for Amber Flags.
    """
    m_proxy = bt08 - bt13
    print(f"💧 Moisture Proxy Mean: {np.nanmean(m_proxy):.2f}K")
    return m_proxy

def bt_to_ctt_c(bt_k: np.ndarray) -> np.ndarray:
    """ Kelvin → Celsius """
    return bt_k - 273.15



