


import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import shift, zoom
from skimage.registration import phase_cross_correlation
from skimage.transform import resize
import cartopy.crs as ccrs
from products.read_tile import read_hsd_tile

FILE_B01 = "north_india_B01.dat.bz2"
FILE_B02 = "north_india_B02.dat.bz2"
FILE_B13 = "north_india_B13.dat.bz2"

# ── Visible parameters ────────────────────────────────────────────────────────
VIS_CROP_COL = 0
VIS_STRETCH  = 1.5
VIS_TARGET_H = 400
VIS_TARGET_W = 1300
VIS_ZOOM_X   = 1.25

# ── IR parameters (tune independently) ───────────────────────────────────────
IR_CROP_COL  = 750
IR_STRETCH   = 1.8
IR_TARGET_H  = 400
IR_TARGET_W  = 1300
IR_ZOOM_X    = 1.25

LON_MIN, LON_MAX = 72, 130
LAT_MIN, LAT_MAX =  9,  22


def stretch(img):
    img = np.nan_to_num(img)
    p1, p99 = np.percentile(img, 1), np.percentile(img, 99)
    if p99 - p1 == 0:
        return img
    return np.clip((img - p1) / (p99 - p1), 0, 1)


def downsample_2km(img):
    h, w = img.shape
    h2, w2 = h // 2, w // 2
    img = img[:h2 * 2, :w2 * 2]
    return img.reshape(h2, 2, w2, 2).mean(axis=(1, 3))


def prepare_rgb(b01, b02):
    shift_detected, _, _ = phase_cross_correlation(b01, b02, upsample_factor=20)
    b02_aligned = shift(b02, shift_detected)

    rgb = np.dstack((b01, b02_aligned, np.zeros_like(b01)))
    rgb = np.clip(rgb, 0, 1)

    rgb = zoom(rgb, (1, VIS_ZOOM_X, 1))
    rgb = rgb[:, VIS_CROP_COL:, :]

    zh = VIS_TARGET_H / rgb.shape[0]
    zw = (VIS_TARGET_W / rgb.shape[1]) * VIS_STRETCH
    rgb = zoom(rgb, (zh, zw, 1))

    return rgb


def prepare_ir(b13):
    b13 = stretch(b13)

    b13 = zoom(b13, (1, IR_ZOOM_X))
    b13 = b13[:, IR_CROP_COL:]

    zh = IR_TARGET_H / b13.shape[0]
    zw = (IR_TARGET_W / b13.shape[1]) * IR_STRETCH
    b13 = zoom(b13, (zh, zw))

    # crop or pad to exact target size — NO resize that would undo the stretch
    if b13.shape[0] > IR_TARGET_H:
        b13 = b13[:IR_TARGET_H, :]
    if b13.shape[1] > IR_TARGET_W:
        b13 = b13[:, :IR_TARGET_W]
    if b13.shape[0] < IR_TARGET_H:
        b13 = np.pad(b13, ((0, IR_TARGET_H - b13.shape[0]), (0, 0)))
    if b13.shape[1] < IR_TARGET_W:
        b13 = np.pad(b13, ((0, 0), (0, IR_TARGET_W - b13.shape[1])))

    cold_mask = b13 > 0.7
    b13_rgb = np.zeros((IR_TARGET_H, IR_TARGET_W, 3))
    b13_rgb[:, :, 2] = b13
    b13_rgb[:, :, 1] = b13 * 0.6
    b13_rgb[:, :, 0] = cold_mask.astype(float)

    return b13_rgb


def main():
    print("Reading bands...")
    b01, _, _ = read_hsd_tile(FILE_B01)
    b02, _, _ = read_hsd_tile(FILE_B02)
    b13, _, _ = read_hsd_tile(FILE_B13)

    b01_ds = downsample_2km(b01)
    b02_ds = downsample_2km(b02)

    b01_s = stretch(b01_ds)
    b02_s = stretch(b02_ds)

    rgb     = prepare_rgb(b01_s, b02_s)
    b13_rgb = prepare_ir(b13)

    print(f"Visible size: {rgb.shape}")
    print(f"IR size:      {b13_rgb.shape}")

    # --------------------------------
    # WINDOW 1 → VISIBLE RAW
    # --------------------------------
    plt.figure(figsize=(14, 5))
    plt.imshow(rgb)
    plt.title("Himawari Visible (Cropped & Resized)")
    plt.axis("off")
    plt.show()

    # --------------------------------
    # WINDOW 2 → IR RAW
    # --------------------------------
    plt.figure(figsize=(14, 5))
    plt.imshow(b13_rgb)
    plt.title("Himawari IR B13 (Cropped & Resized)")
    plt.axis("off")
    plt.show()

    # --------------------------------
    # WINDOW 3 → JAXA REGION MAP
    # --------------------------------
    fig = plt.figure(figsize=(14, 5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax.coastlines(resolution="10m", color="black", linewidth=1)
    ax.set_title("Target Region (JAXA Monitor Crop)")
    plt.show()

    # --------------------------------
    # WINDOW 4 → COMPARISON: VISIBLE + IR
    # --------------------------------
    fig = plt.figure(figsize=(14, 8))

    ax1 = fig.add_subplot(2, 1, 1, projection=ccrs.PlateCarree())
    ax1.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax1.imshow(rgb, origin="upper",
               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
               transform=ccrs.PlateCarree(), aspect=None, alpha=0.9)
    ax1.coastlines(resolution="10m", color="white", linewidth=1)
    ax1.set_title("Himawari Visible Overlaid on JAXA Region")

    ax2 = fig.add_subplot(2, 1, 2, projection=ccrs.PlateCarree())
    ax2.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax2.imshow(b13_rgb, origin="upper",
               extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
               transform=ccrs.PlateCarree(), aspect=None, alpha=0.9)
    ax2.coastlines(resolution="10m", color="white", linewidth=1)
    ax2.set_title("Himawari IR (B13) Overlaid on JAXA Region")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()