


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.ndimage import shift, zoom
from skimage.registration import phase_cross_correlation
import cartopy.crs as ccrs

# ── Visible pipeline constants ────────────────────────────────────────────────
VIS_CROP_COL = 0
VIS_STRETCH  = 1.5
VIS_TARGET_H = 400
VIS_TARGET_W = 1300
VIS_ZOOM_X   = 1.25

# ── IR pipeline constants ─────────────────────────────────────────────────────
IR_CROP_COL  = 750
IR_STRETCH   = 1.8
IR_TARGET_H  = 400
IR_TARGET_W  = 1300
IR_ZOOM_X    = 1.25

LON_MIN, LON_MAX = 72, 130
LAT_MIN, LAT_MAX =  9,  22

LEGEND = [
    mpatches.Patch(color=(0, 0.8, 0),        label="Green  — Seedable (High Potential)"),
    mpatches.Patch(color=(1, 0.7, 0),        label="Amber  — Watch (Marginal)"),
    mpatches.Patch(color=(0.55, 0.55, 0.55), label="Gray   — Do Not Seed"),
]


def _stretch_img(img):
    img = np.nan_to_num(img)
    p1, p99 = np.percentile(img, 1), np.percentile(img, 99)
    if p99 - p1 == 0:
        return img
    return np.clip((img - p1) / (p99 - p1), 0, 1)


def prepare_rgb(b01, b02):
    b01 = _stretch_img(b01)
    b02 = _stretch_img(b02)

    shift_detected, _, _ = phase_cross_correlation(b01, b02, upsample_factor=20)
    b02_aligned = shift(b02, shift_detected)

    rgb = np.dstack((b01, b02_aligned, np.zeros_like(b01)))
    rgb = np.clip(rgb, 0, 1)

    rgb = zoom(rgb, (1, VIS_ZOOM_X, 1))
    rgb = rgb[:, VIS_CROP_COL:, :]

    zh = VIS_TARGET_H / rgb.shape[0]
    zw = (VIS_TARGET_W / rgb.shape[1]) * VIS_STRETCH
    rgb = zoom(rgb, (zh, zw, 1))
    rgb = np.clip(rgb, 0, 1)

    return rgb


def _apply_pipeline_to_binary(mask2d):
    """
    Stretch a single binary mask (0.0 / 1.0) through the IR pipeline.
    Uses continuous interpolation then thresholds at 0.5 — accurate for binary data.
    """
    arr = zoom(mask2d.astype(np.float32), (1, IR_ZOOM_X))
    arr = arr[:, IR_CROP_COL:]

    zh = IR_TARGET_H / arr.shape[0]
    zw = (IR_TARGET_W / arr.shape[1]) * IR_STRETCH
    arr = zoom(arr, (zh, zw))

    if arr.shape[0] > IR_TARGET_H: arr = arr[:IR_TARGET_H, :]
    if arr.shape[1] > IR_TARGET_W: arr = arr[:, :IR_TARGET_W]
    if arr.shape[0] < IR_TARGET_H: arr = np.pad(arr, ((0, IR_TARGET_H - arr.shape[0]), (0, 0)))
    if arr.shape[1] < IR_TARGET_W: arr = np.pad(arr, ((0, 0), (0, IR_TARGET_W - arr.shape[1])))

    # Threshold at 0.5 — restores accurate binary values after interpolation
    return arr > 0.5


def build_flag_overlay(flag):
    """
    Option 2 — stretch each flag as a separate binary mask.
    No interpolation artifacts between categories.
    """
    # Separate binary masks per category
    green_mask = _apply_pipeline_to_binary((flag == 2).astype(np.float32))
    amber_mask = _apply_pipeline_to_binary((flag == 1).astype(np.float32))
    gray_mask  = _apply_pipeline_to_binary((flag == 0).astype(np.float32))

    H, W = green_mask.shape
    overlay = np.zeros((H, W, 4), dtype=np.float32)

    # Apply in priority order: Green > Amber > Gray
    overlay[gray_mask]  = [0.55, 0.55, 0.55, 1.0]
    overlay[amber_mask] = [1.0,  0.7,  0.0,  1.0]
    overlay[green_mask] = [0.0,  0.8,  0.0,  1.0]

    print(f"\n🖼️  Overlay pixel counts (after pipeline):")
    print(f"  Green : {np.count_nonzero(green_mask)}")
    print(f"  Amber : {np.count_nonzero(amber_mask)}")
    print(f"  Gray  : {np.count_nonzero(gray_mask)}")

    return overlay


def plot_all(data, products):
    rgb = prepare_rgb(data["b01"], data["b02"])

    flag    = products["flag"]
    overlay = build_flag_overlay(flag)

    # ── WINDOW 1 → VISIBLE RAW ────────────────────────────────────────────────
    plt.figure(figsize=(14, 5))
    plt.imshow(rgb)
    plt.title("Himawari Visible (B01 + B02)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

    # ── WINDOW 2 → SEEDABILITY OVERLAY ON VISIBLE ────────────────────────────
    fig = plt.figure(figsize=(14, 5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax.imshow(rgb, origin="upper",
              extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
              transform=ccrs.PlateCarree(), aspect=None)
    ax.imshow(overlay, origin="upper",
              extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
              transform=ccrs.PlateCarree(), aspect=None)
    ax.coastlines(resolution="10m", color="white", linewidth=1)
    ax.set_title("Seedability Decision Map")
    ax.legend(handles=LEGEND, loc="lower right", fontsize=9,
              framealpha=0.8, facecolor="black", labelcolor="white")
    plt.tight_layout()
    plt.show()

    # ── WINDOW 3 → SIDE BY SIDE: VISIBLE + SEEDABILITY ───────────────────────
    fig = plt.figure(figsize=(14, 10))

    ax1 = fig.add_subplot(2, 1, 1, projection=ccrs.PlateCarree())
    ax1.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax1.imshow(rgb, origin="upper",
               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
               transform=ccrs.PlateCarree(), aspect=None)
    ax1.coastlines(resolution="10m", color="white", linewidth=1)
    ax1.set_title("Himawari Visible")

    ax2 = fig.add_subplot(2, 1, 2, projection=ccrs.PlateCarree())
    ax2.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax2.set_facecolor("black")
    ax2.imshow(overlay, origin="upper",
               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
               transform=ccrs.PlateCarree(), aspect=None)
    ax2.coastlines(resolution="10m", color="white", linewidth=1)
    ax2.set_title("Seedability Decision Map (Green / Amber / Gray)")
    ax2.legend(handles=LEGEND, loc="lower right", fontsize=9,
               framealpha=0.8, facecolor="black", labelcolor="white")

    plt.tight_layout()
    plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# from scipy.ndimage import shift, zoom
# from skimage.registration import phase_cross_correlation
# import cartopy.crs as ccrs

# # ── Visible pipeline constants ────────────────────────────────────────────────
# VIS_CROP_COL = 0
# VIS_STRETCH  = 1.5
# VIS_TARGET_H = 400
# VIS_TARGET_W = 1300
# VIS_ZOOM_X   = 1.25

# # ── IR pipeline constants ─────────────────────────────────────────────────────
# IR_CROP_COL  = 750
# IR_STRETCH   = 1.8
# IR_TARGET_H  = 400
# IR_TARGET_W  = 1300
# IR_ZOOM_X    = 1.25

# LON_MIN, LON_MAX = 72, 130
# LAT_MIN, LAT_MAX =  9,  22

# LEGEND = [
#     mpatches.Patch(color=(0, 0.8, 0),        label="Green  — Seedable (High Potential)"),
#     mpatches.Patch(color=(1, 0.7, 0),        label="Amber  — Watch (Marginal)"),
#     mpatches.Patch(color=(0.55, 0.55, 0.55), label="Gray   — Do Not Seed"),
# ]


# def _stretch_img(img):
#     img = np.nan_to_num(img)
#     p1, p99 = np.percentile(img, 1), np.percentile(img, 99)
#     if p99 - p1 == 0:
#         return img
#     return np.clip((img - p1) / (p99 - p1), 0, 1)


# def prepare_rgb(b01, b02):
#     b01 = _stretch_img(b01)
#     b02 = _stretch_img(b02)

#     shift_detected, _, _ = phase_cross_correlation(b01, b02, upsample_factor=20)
#     b02_aligned = shift(b02, shift_detected)

#     rgb = np.dstack((b01, b02_aligned, np.zeros_like(b01)))
#     rgb = np.clip(rgb, 0, 1)

#     rgb = zoom(rgb, (1, VIS_ZOOM_X, 1))
#     rgb = rgb[:, VIS_CROP_COL:, :]

#     zh = VIS_TARGET_H / rgb.shape[0]
#     zw = (VIS_TARGET_W / rgb.shape[1]) * VIS_STRETCH
#     rgb = zoom(rgb, (zh, zw, 1))
#     rgb = np.clip(rgb, 0, 1)

#     return rgb


# def _apply_pipeline_to_binary(mask2d):
#     """
#     Stretch a single binary mask (0.0 / 1.0) through the IR pipeline.
#     Uses continuous interpolation then thresholds at 0.5 — accurate for binary data.
#     """
#     arr = zoom(mask2d.astype(np.float32), (1, IR_ZOOM_X))
#     arr = arr[:, IR_CROP_COL:]

#     zh = IR_TARGET_H / arr.shape[0]
#     zw = (IR_TARGET_W / arr.shape[1]) * IR_STRETCH
#     arr = zoom(arr, (zh, zw))

#     if arr.shape[0] > IR_TARGET_H: arr = arr[:IR_TARGET_H, :]
#     if arr.shape[1] > IR_TARGET_W: arr = arr[:, :IR_TARGET_W]
#     if arr.shape[0] < IR_TARGET_H: arr = np.pad(arr, ((0, IR_TARGET_H - arr.shape[0]), (0, 0)))
#     if arr.shape[1] < IR_TARGET_W: arr = np.pad(arr, ((0, 0), (0, IR_TARGET_W - arr.shape[1])))

#     # Threshold at 0.5 — restores accurate binary values after interpolation
#     return arr > 0.5


# def build_flag_overlay(flag):
#     """
#     Option 2 — stretch each flag as a separate binary mask.
#     No interpolation artifacts between categories.
#     """
#     # Separate binary masks per category
#     green_mask = _apply_pipeline_to_binary((flag == 2).astype(np.float32))
#     amber_mask = _apply_pipeline_to_binary((flag == 1).astype(np.float32))
#     gray_mask  = _apply_pipeline_to_binary((flag == 0).astype(np.float32))

#     H, W = green_mask.shape
#     overlay = np.zeros((H, W, 4), dtype=np.float32)

#     # Apply in priority order: Green > Amber > Gray
#     overlay[gray_mask]  = [0.55, 0.55, 0.55, 1.0]
#     overlay[amber_mask] = [1.0,  0.7,  0.0,  1.0]
#     overlay[green_mask] = [0.0,  0.8,  0.0,  1.0]

#     print(f"\n🖼️  Overlay pixel counts (after pipeline):")
#     print(f"  Green : {np.count_nonzero(green_mask)}")
#     print(f"  Amber : {np.count_nonzero(amber_mask)}")
#     print(f"  Gray  : {np.count_nonzero(gray_mask)}")

#     return overlay


# def plot_all(data, products):
#     rgb = prepare_rgb(data["b01"], data["b02"])

#     flag    = products["flag"]
#     overlay = build_flag_overlay(flag)

#     # ── WINDOW 1 → VISIBLE RAW ────────────────────────────────────────────────
#     plt.figure(figsize=(14, 5))
#     plt.imshow(rgb)
#     plt.title("Himawari Visible (B01 + B02)")
#     plt.axis("off")
#     plt.tight_layout()
#     plt.show()

#     # ── WINDOW 2 → SEEDABILITY OVERLAY ON VISIBLE ────────────────────────────
#     fig = plt.figure(figsize=(14, 5))
#     ax = plt.axes(projection=ccrs.PlateCarree())
#     ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
#     ax.imshow(rgb, origin="upper",
#               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#               transform=ccrs.PlateCarree(), aspect=None)
#     ax.imshow(overlay, origin="upper",
#               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#               transform=ccrs.PlateCarree(), aspect=None)
#     ax.coastlines(resolution="10m", color="white", linewidth=1)
#     ax.set_title("Seedability Decision Map")
#     ax.legend(handles=LEGEND, loc="lower right", fontsize=9,
#               framealpha=0.8, facecolor="black", labelcolor="white")
#     plt.tight_layout()
#     plt.show()

#     # ── WINDOW 3 → SIDE BY SIDE: VISIBLE + SEEDABILITY ───────────────────────
#     fig = plt.figure(figsize=(14, 10))

#     ax1 = fig.add_subplot(2, 1, 1, projection=ccrs.PlateCarree())
#     ax1.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
#     ax1.imshow(rgb, origin="upper",
#                extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#                transform=ccrs.PlateCarree(), aspect=None)
#     ax1.coastlines(resolution="10m", color="white", linewidth=1)
#     ax1.set_title("Himawari Visible")

#     ax2 = fig.add_subplot(2, 1, 2, projection=ccrs.PlateCarree())
#     ax2.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
#     ax2.set_facecolor("black")
#     ax2.imshow(overlay, origin="upper",
#                extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#                transform=ccrs.PlateCarree(), aspect=None)
#     ax2.coastlines(resolution="10m", color="white", linewidth=1)
#     ax2.set_title("Seedability Decision Map (Green / Amber / Gray)")
#     ax2.legend(handles=LEGEND, loc="lower right", fontsize=9,
#                framealpha=0.8, facecolor="black", labelcolor="white")

#     plt.tight_layout()
#     plt.show()

"""hello"""


# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# from scipy.ndimage import shift, zoom
# from skimage.registration import phase_cross_correlation
# import cartopy.crs as ccrs

# # ── Visible pipeline constants ────────────────────────────────────────────────
# VIS_CROP_COL = 0
# VIS_STRETCH  = 1.5
# VIS_TARGET_H = 400
# VIS_TARGET_W = 1300
# VIS_ZOOM_X   = 1.25

# # ── IR pipeline constants ─────────────────────────────────────────────────────
# IR_CROP_COL  = 750
# IR_STRETCH   = 1.8
# IR_TARGET_H  = 400
# IR_TARGET_W  = 1300
# IR_ZOOM_X    = 1.25

# LON_MIN, LON_MAX = 72, 130
# LAT_MIN, LAT_MAX =  9,  22

# LEGEND = [
#     mpatches.Patch(color=(0, 0.8, 0),        label="Green  — Seedable (High Potential)"),
#     mpatches.Patch(color=(1, 0.7, 0),        label="Amber  — Watch (Marginal)"),
#     mpatches.Patch(color=(0.55, 0.55, 0.55), label="Gray   — Do Not Seed"),
# ]


# def _stretch_img(img):
#     img = np.nan_to_num(img)
#     p1, p99 = np.percentile(img, 1), np.percentile(img, 99)
#     if p99 - p1 == 0:
#         return img
#     return np.clip((img - p1) / (p99 - p1), 0, 1)


# def prepare_rgb(b01, b02):
#     b01 = _stretch_img(b01)
#     b02 = _stretch_img(b02)

#     shift_detected, _, _ = phase_cross_correlation(b01, b02, upsample_factor=20)
#     b02_aligned = shift(b02, shift_detected)

#     rgb = np.dstack((b01, b02_aligned, np.zeros_like(b01)))
#     rgb = np.clip(rgb, 0, 1)

#     rgb = zoom(rgb, (1, VIS_ZOOM_X, 1))
#     rgb = rgb[:, VIS_CROP_COL:, :]

#     zh = VIS_TARGET_H / rgb.shape[0]
#     zw = (VIS_TARGET_W / rgb.shape[1]) * VIS_STRETCH
#     rgb = zoom(rgb, (zh, zw, 1))
#     rgb = np.clip(rgb, 0, 1)

#     return rgb


# def _apply_pipeline_to_binary(mask2d):
#     """
#     Stretch a single binary mask (0.0 / 1.0) through the IR pipeline.
#     Uses continuous interpolation then thresholds at 0.5 — accurate for binary data.
#     """
#     arr = zoom(mask2d.astype(np.float32), (1, IR_ZOOM_X))
#     arr = arr[:, IR_CROP_COL:]

#     zh = IR_TARGET_H / arr.shape[0]
#     zw = (IR_TARGET_W / arr.shape[1]) * IR_STRETCH
#     arr = zoom(arr, (zh, zw))

#     if arr.shape[0] > IR_TARGET_H: arr = arr[:IR_TARGET_H, :]
#     if arr.shape[1] > IR_TARGET_W: arr = arr[:, :IR_TARGET_W]
#     if arr.shape[0] < IR_TARGET_H: arr = np.pad(arr, ((0, IR_TARGET_H - arr.shape[0]), (0, 0)))
#     if arr.shape[1] < IR_TARGET_W: arr = np.pad(arr, ((0, 0), (0, IR_TARGET_W - arr.shape[1])))

#     return arr > 0.5


# def build_flag_overlay(flag):
#     """
#     Stretch each flag as a separate binary mask.
#     All classified pixels (flag >= 0) are at minimum Gray.
#     Black pixels only where flag == -1 (unclassified — should be near zero).
#     """
#     # Force copy so we don't mutate original
#     flag = flag.copy()

#     green_mask   = _apply_pipeline_to_binary((flag == 2).astype(np.float32))
#     amber_mask   = _apply_pipeline_to_binary((flag == 1).astype(np.float32))
#     # classified = flag 0, 1, or 2 — all get at minimum gray
#     classified   = _apply_pipeline_to_binary((flag >= 0).astype(np.float32))

#     H, W = green_mask.shape
#     overlay = np.zeros((H, W, 4), dtype=np.float32)  # transparent by default

#     # All classified pixels → Gray first
#     overlay[classified]                            = [0.55, 0.55, 0.55, 1.0]
#     # Override with Amber where applicable
#     overlay[amber_mask & classified & ~green_mask] = [1.0,  0.7,  0.0,  1.0]
#     # Override with Green (highest priority)
#     overlay[green_mask & classified]               = [0.0,  0.8,  0.0,  1.0]

#     print(f"\n🖼️  Overlay pixel counts (after pipeline):")
#     print(f"  Green      : {np.count_nonzero(green_mask & classified)}")
#     print(f"  Amber      : {np.count_nonzero(amber_mask & classified & ~green_mask)}")
#     print(f"  Gray       : {np.count_nonzero(classified & ~amber_mask & ~green_mask)}")
#     print(f"  Unclassified (black) : {np.count_nonzero(~classified)}")

#     return overlay


# def plot_all(data, products):
#     rgb = prepare_rgb(data["b01"], data["b02"])

#     flag = products["flag"].copy()
#     flag[flag == -1] = 0  # catch-all: force any -1 to Gray before pipeline

#     overlay = build_flag_overlay(flag)

#     # ── WINDOW 1 → VISIBLE RAW ────────────────────────────────────────────────
#     plt.figure(figsize=(14, 5))
#     plt.imshow(rgb)
#     plt.title("Himawari Visible (B01 + B02)")
#     plt.axis("off")
#     plt.tight_layout()
#     plt.show()

#     # ── WINDOW 2 → SEEDABILITY OVERLAY ON VISIBLE ────────────────────────────
#     fig = plt.figure(figsize=(14, 5))
#     ax = plt.axes(projection=ccrs.PlateCarree())
#     ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
#     ax.imshow(rgb, origin="upper",
#               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#               transform=ccrs.PlateCarree(), aspect=None)
#     ax.imshow(overlay, origin="upper",
#               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#               transform=ccrs.PlateCarree(), aspect=None)
#     ax.coastlines(resolution="10m", color="white", linewidth=1)
#     ax.set_title("Seedability Decision Map")
#     ax.legend(handles=LEGEND, loc="lower right", fontsize=9,
#               framealpha=0.8, facecolor="black", labelcolor="white")
#     plt.tight_layout()
#     plt.show()

#     # ── WINDOW 3 → SIDE BY SIDE: VISIBLE + SEEDABILITY ───────────────────────
#     fig = plt.figure(figsize=(14, 10))

#     ax1 = fig.add_subplot(2, 1, 1, projection=ccrs.PlateCarree())
#     ax1.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
#     ax1.imshow(rgb, origin="upper",
#                extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#                transform=ccrs.PlateCarree(), aspect=None)
#     ax1.coastlines(resolution="10m", color="white", linewidth=1)
#     ax1.set_title("Himawari Visible")

#     ax2 = fig.add_subplot(2, 1, 2, projection=ccrs.PlateCarree())
#     ax2.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
#     ax2.set_facecolor("black")
#     ax2.imshow(overlay, origin="upper",
#                extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
#                transform=ccrs.PlateCarree(), aspect=None)
#     ax2.coastlines(resolution="10m", color="white", linewidth=1)
#     ax2.set_title("Seedability Decision Map (Green / Amber / Gray)")
#     ax2.legend(handles=LEGEND, loc="lower right", fontsize=9,
#                framealpha=0.8, facecolor="black", labelcolor="white")

#     plt.tight_layout()
#     plt.show()