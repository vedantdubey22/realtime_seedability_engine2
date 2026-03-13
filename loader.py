import numpy as np
from products.read_tile import read_hsd_tile
from products.ctt import dn_to_bt, bt_to_ctt_c

FILE_B01  = "north_india_B01.dat.bz2"
FILE_B02  = "north_india_B02.dat.bz2"
FILE_B08  = "north_india_B08.dat.bz2"
FILE_B13  = "north_india_B13.dat.bz2"
FILE_B13P = "north_india_B13_prev.dat.bz2"
FILE_B14  = "north_india_B14.dat.bz2"


def downsample_2km(img):
    h, w = img.shape
    h2, w2 = h // 2, w // 2
    img = img[:h2 * 2, :w2 * 2]
    return img.reshape(h2, 2, w2, 2).mean(axis=(1, 3))


def load_all():
    """
    Reads all Himawari tiles and returns:
        - b01, b02       : visible raw DN (downsampled to 2km)
        - bt08, bt13, bt13_prev, bt14 : brightness temperatures (K)
        - ctt_c, ctt_prev_c           : cloud top temperature (°C)
    """
    print("=" * 50)
    print("📡 LOADING ALL HIMAWARI TILES")
    print("=" * 50)

    # Visible
    b01, _, _ = read_hsd_tile(FILE_B01)
    b02, _, _ = read_hsd_tile(FILE_B02)
    b01 = downsample_2km(b01)
    b02 = downsample_2km(b02)

    # IR bands
    b08,  g08,  o08  = read_hsd_tile(FILE_B08)
    b13,  g13,  o13  = read_hsd_tile(FILE_B13)
    b13p, g13p, o13p = read_hsd_tile(FILE_B13P)
    b14,  g14,  o14  = read_hsd_tile(FILE_B14)

    # Brightness temperatures
    bt08      = dn_to_bt(b08,  g08,  o08,  "B08")
    bt13      = dn_to_bt(b13,  g13,  o13,  "B13")
    bt13_prev = dn_to_bt(b13p, g13p, o13p, "B13")
    bt14      = dn_to_bt(b14,  g14,  o14,  "B14")

    # CTT in Celsius
    ctt_c      = bt_to_ctt_c(bt13)
    ctt_prev_c = bt_to_ctt_c(bt13_prev)

    print(f"\n🌡️  CTT range : {np.nanmin(ctt_c):.1f}°C → {np.nanmax(ctt_c):.1f}°C")
    print(f"   CTT mean  : {np.nanmean(ctt_c):.1f}°C")

    return {
        "b01": b01,
        "b02": b02,
        "bt08": bt08,
        "bt13": bt13,
        "bt13_prev": bt13_prev,
        "bt14": bt14,
        "ctt_c": ctt_c,
        "ctt_prev_c": ctt_prev_c,
    }