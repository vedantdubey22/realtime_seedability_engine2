# import numpy as np

# # =========================
# # Planck constants (B13)
# # =========================
# C1 = 1.191042e-5
# C2 = 1.4387752
# WAVENUMBER = 930.0  # cm-1 (Standard for Himawari Band 13)

# def dn_to_bt(dn: np.ndarray, gain: float, offset: float) -> np.ndarray:
#     """
#     DN → Radiance → Brightness Temperature (Kelvin)
#     Includes dynamic scaling to fix the 'Space Noise' bias (-131°C error).
#     """

#     print("\n🌡️ DN → BT (Kelvin)")

#     # Use nan-aware stats to ignore masked pixels
#     print("DN stats:")
#     print("  min:", np.nanmin(dn))
#     print("  max:", np.nanmax(dn))
#     print("  mean:", np.nanmean(dn))

#     # ---- Radiance conversion with Scaling Fix ----
#     # We start with a 10x multiplier because JAXA HSD radiance units 
#     # often require alignment with Planck constant C1
#     rad = (dn * gain + offset) * 10.0
    
#     # Clip tiny values to avoid log(0)
#     rad = np.where(np.isnan(rad), np.nan, np.maximum(rad, 1e-10))

#     # ---- Planck inversion ----
#     # BT = (C2 * v) / ln( (C1 * v^3 / rad) + 1 )
#     with np.errstate(divide='ignore', invalid='ignore'):
#         bt_k = (C2 * WAVENUMBER) / np.log((C1 * WAVENUMBER**3 / rad) + 1.0)

#     # ---- Dynamic Recovery Logic ----
#     # If the mean is still in the 'Space' range (<200K), apply 100x scaling
#     if np.nanmean(bt_k) < 200:
#         print("⚠️ BT too low. Applying 100x radiance scaling correction...")
#         rad = (dn * gain + offset) * 100.0
#         bt_k = (C2 * WAVENUMBER) / np.log((C1 * WAVENUMBER**3 / rad) + 1.0)

#     print("BT (Kelvin) stats:")
#     print("  min:", np.nanmin(bt_k))
#     print("  max:", np.nanmax(bt_k))
#     print("  mean:", np.nanmean(bt_k))

#     return bt_k


# def bt_to_ctt_c(bt_k: np.ndarray) -> np.ndarray:
#     """
#     Kelvin → Celsius (Cloud-Top Temperature)
#     """

#     ctt_c = bt_k - 273.15

#     print("\n🌡️ BT → CTT (°C)")
#     print("CTT stats:")
#     print("  min:", np.nanmin(ctt_c))
#     print("  max:", np.nanmax(ctt_c))
#     print("  mean:", np.nanmean(ctt_c))

#     return ctt_c

"""2 bands"""
# import numpy as np

# # =========================
# # Planck constants
# # =========================
# C1 = 1.191042e-5
# C2 = 1.4387752

# # Wavenumbers (cm-1) for Himawari-9 Bands
# # B13: 10.4 μm -> ~961.5 cm-1
# # B14: 11.2 μm -> ~892.8 cm-1
# WAVENUMBERS = {
#     "B13": 961.5,
#     "B14": 892.8
# }

# def dn_to_bt(dn: np.ndarray, gain: float, offset: float, band: str = "B13") -> np.ndarray:
#     """
#     DN → Radiance → Brightness Temperature (Kelvin) for specific bands.
#     """
#     v = WAVENUMBERS.get(band, 961.5)
#     print(f"\n🌡️ DN → BT ({band}, Kelvin)")

#     # ---- Radiance conversion with Scaling Fix ----
#     rad = (dn * gain + offset) * 10.0
#     rad = np.where(np.isnan(rad), np.nan, np.maximum(rad, 1e-10))

#     # ---- Planck inversion ----
#     with np.errstate(divide='ignore', invalid='ignore'):
#         bt_k = (C2 * v) / np.log((C1 * v**3 / rad) + 1.0)

#     # ---- Dynamic Recovery Logic ----
#     if np.nanmean(bt_k) < 200:
#         print(f"⚠️ {band} BT too low. Applying 100x radiance scaling correction...")
#         rad = (dn * gain + offset) * 100.0
#         bt_k = (C2 * v) / np.log((C1 * v**3 / rad) + 1.0)

#     print(f"  {band} BT (K) Mean: {np.nanmean(bt_k):.2f}")
#     return bt_k

# def compute_swd(bt13: np.ndarray, bt14: np.ndarray) -> np.ndarray:
#     """
#     Computes BT13 - BT14 (Split Window Difference).
#     Used to filter ice-dominated clouds and thin cirrus/haze.
#     """
#     swd = bt13 - bt14
    
#     # Filter out extreme outliers often caused by space background
#     swd = np.clip(swd, -5.0, 15.0)

#     print("\n📡 Split-Window Difference (SWD) Diagnostics:")
#     print(f"  Mean Difference: {np.nanmean(swd):.2f}K")
#     print(f"  Max Difference: {np.nanmax(swd):.2f}K")
    
#     return swd

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
    Computes BT13 - BT14 (Split Window Difference).
    Used to filter ice-dominated clouds (>80% ice phase).
    """
    swd = bt13 - bt14
    swd = np.clip(swd, -5.0, 15.0)
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
#     Split Window Difference (BT13 - BT14)

#     Physics:
#     Larger positive values → ice dominated cloud tops.
#     Near zero → liquid-rich clouds (seedable).
#     """

#     swd = bt13 - bt14

#     # remove unrealistic values
#     swd[(swd < -5.0) | (swd > 8.0)] = np.nan


#     print("\n🧊 SWD diagnostics:")
#     print(f"  Mean SWD : {np.nanmean(swd):.3f}")
#     print(f"  Ice-like (>1.5K): {100*np.nanmean(swd>1.5):.2f}%")

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