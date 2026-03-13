# import bz2
# import numpy as np
# import struct
# from pathlib import Path

# def read_b13_tile(file_path: str):
#     """
#     Updated Himawari HSD reader for JAXA P-Tree segments.
#     Fixed Endianness (Big-Endian >u2) to prevent data truncation over Himachal.
#     """
#     print(f"\n📥 READING B13 FILE: {file_path}")

#     try:
#         with bz2.open(Path(file_path), "rb") as bz_file:
#             raw = bz_file.read()
#     except Exception as e:
#         raise IOError(f"Decompression failed: {e}")

#     # ==========================================================
#     # 1️⃣ HEADER SIZE DETECTION
#     # ==========================================================
#     try:
#         # Standard HSD header detection
#         header_size = struct.unpack(">I", raw[11:15])[0]
#     except:
#         header_blocks = struct.unpack(">H", raw[0:2])[0]
#         header_size = header_blocks * 2880

#     if header_size >= len(raw) or header_size == 0:
#         header_size = 2880 * 15 

#     header = raw[:header_size]

#     # ==========================================================
#     # 2️⃣ BLOCK SEARCH (Calibration & Dimensions)
#     # ==========================================================
#     nline, npixel = 0, 0
#     gain, offset = None, None
    
#     # Standard Himawari-9 B13 R20 width for S0310 segments
#     KNOWN_WIDTH = 5500 

#     for i in range(0, len(header) - 150):
#         # Block 2: Image Information
#         if header[i] == 2 and header[i+1:i+3] == b'\x00\x32':
#             tmp_pixel = struct.unpack(">H", header[i+5:i+7])[0]
#             tmp_line = struct.unpack(">H", header[i+7:i+9])[0]
#             if tmp_pixel == KNOWN_WIDTH:
#                 npixel = tmp_pixel
#                 nline = tmp_line
        
#         # Block 5: Calibration Information
#         if header[i] == 5 and header[i+1:i+3] == b'\x00\x93':
#             gain = struct.unpack(">d", header[i+9:i+17])[0]
#             offset = struct.unpack(">d", header[i+17:i+25])[0]

#     # Fallback logic for truncated or misparsed headers
#     if npixel != KNOWN_WIDTH:
#         print(f"⚠️ Header dimensions unreadable. Forcing standard {KNOWN_WIDTH} width.")
#         npixel = KNOWN_WIDTH
#         nline = len(raw[header_size:]) // (npixel * 2)

#     gain = gain if gain is not None else 0.0003342
#     offset = offset if offset is not None else 0.0

#     # ==========================================================
#     # 3️⃣ IMAGE DATA EXTRACTION (FIXED ENDIANNESS)
#     # ==========================================================
#     image_bytes = raw[header_size:]
    
#     if len(image_bytes) % 2 != 0:
#         image_bytes = image_bytes[:-1]

#     # FIXED: Using Big-Endian ('>u2') as required by JAXA HSD format
#     data = np.frombuffer(image_bytes, dtype=">u2")
    
#     expected = nline * npixel
#     if data.size < expected:
#         print(f"⚠️ Data truncated: Adjusting lines to {data.size // npixel}")
#         nline = data.size // npixel
#         expected = nline * npixel

#     # Reshape and convert to float for processing
#     img = data[:expected].reshape(nline, npixel).astype(np.float32)

#     # Corrected Masking: Filler values in HSD are usually 65535 or > 4095
#     img[img > 4095] = np.nan

#     print(f"✅ Successfully Loaded: {img.shape}")
#     print(f"📡 Header Size: {header_size} | Total Pixels: {expected}")
    
#     return img, gain, offset

""" 2 bands"""

# import bz2
# import numpy as np
# import struct
# from pathlib import Path

# def read_hsd_tile(file_path: str):
#     """
#     Generalized Himawari HSD reader.
#     Works for both Band 13 and Band 14 segments.
#     """
#     # Extract band name for logging (e.g., 'B13' or 'B14')
#     band_id = "B14" if "B14" in file_path.upper() else "B13"
#     print(f"\n📥 READING {band_id} FILE: {file_path}")

#     try:
#         with bz2.open(Path(file_path), "rb") as bz_file:
#             raw = bz_file.read()
#     except Exception as e:
#         raise IOError(f"Decompression failed for {file_path}: {e}")

#     # ==========================================================
#     # 1️⃣ HEADER SIZE DETECTION
#     # ==========================================================
#     try:
#         header_size = struct.unpack(">I", raw[11:15])[0]
#     except:
#         header_blocks = struct.unpack(">H", raw[0:2])[0]
#         header_size = header_blocks * 2880

#     if header_size >= len(raw) or header_size == 0:
#         header_size = 2880 * 15 

#     header = raw[:header_size]

#     # ==========================================================
#     # 2️⃣ BLOCK SEARCH (Calibration & Dimensions)
#     # ==========================================================
#     nline, npixel = 0, 0
#     gain, offset = None, None
    
#     # Standard Himawari-9 B13/B14 R20 width for S0310 segments
#     KNOWN_WIDTH = 5500 

#     for i in range(0, len(header) - 150):
#         # Block 2: Image Information
#         if header[i] == 2 and header[i+1:i+3] == b'\x00\x32':
#             tmp_pixel = struct.unpack(">H", header[i+5:i+7])[0]
#             tmp_line = struct.unpack(">H", header[i+7:i+9])[0]
#             if tmp_pixel == KNOWN_WIDTH:
#                 npixel = tmp_pixel
#                 nline = tmp_line
        
#         # Block 5: Calibration Information
#         if header[i] == 5 and header[i+1:i+3] == b'\x00\x93':
#             gain = struct.unpack(">d", header[i+9:i+17])[0]
#             offset = struct.unpack(">d", header[i+17:i+25])[0]

#     # Fallback logic
#     if npixel != KNOWN_WIDTH:
#         npixel = KNOWN_WIDTH
#         nline = len(raw[header_size:]) // (npixel * 2)

#     # Use band-specific defaults if calibration block parsing fails
#     if gain is None:
#         gain = 0.0003342 if band_id == "B13" else 0.0003310

#     offset = offset if offset is not None else 0.0

#     # ==========================================================
#     # 3️⃣ IMAGE DATA EXTRACTION
#     # ==========================================================
#     image_bytes = raw[header_size:]
#     if len(image_bytes) % 2 != 0:
#         image_bytes = image_bytes[:-1]

#     data = np.frombuffer(image_bytes, dtype=">u2")
#     expected = nline * npixel

#     img = data[:expected].reshape(nline, npixel).astype(np.float32)

#     # Corrected Masking for satellite filler values
#     img[img > 4095] = np.nan

#     print(f"✅ {band_id} Successfully Loaded: {img.shape}")
#     return img, gain, offset

"""3 bands"""

# import bz2
# import numpy as np
# import struct
# from pathlib import Path

# def read_hsd_tile(file_path: str):
#     """
#     Generalized Himawari HSD reader.
#     Supports Band 08 (Water Vapor), Band 13 (Thermal), and Band 14 (Clean IR).
#     """
#     # 🔎 Band Detection Logic
#     file_upper = file_path.upper()
#     if "B08" in file_upper:
#         band_id = "B08"
#     elif "B14" in file_upper:
#         band_id = "B14"
#     else:
#         band_id = "B13"
        
#     print(f"\n📥 READING {band_id} FILE: {file_path}")

#     try:
#         with bz2.open(Path(file_path), "rb") as bz_file:
#             raw = bz_file.read()
#     except Exception as e:
#         raise IOError(f"Decompression failed for {file_path}: {e}")

#     # ==========================================================
#     # 1️⃣ HEADER SIZE DETECTION
#     # ==========================================================
#     try:
#         header_size = struct.unpack(">I", raw[11:15])[0]
#     except:
#         header_blocks = struct.unpack(">H", raw[0:2])[0]
#         header_size = header_blocks * 2880

#     if header_size >= len(raw) or header_size == 0:
#         header_size = 2880 * 15 

#     header = raw[:header_size]

#     # ==========================================================
#     # 2️⃣ BLOCK SEARCH (Calibration & Dimensions)
#     # ==========================================================
#     nline, npixel = 0, 0
#     gain, offset = None, None
#     KNOWN_WIDTH = 5500 

#     for i in range(0, len(header) - 150):
#         # Block 2: Image Information
#         if header[i] == 2 and header[i+1:i+3] == b'\x00\x32':
#             tmp_pixel = struct.unpack(">H", header[i+5:i+7])[0]
#             tmp_line = struct.unpack(">H", header[i+7:i+9])[0]
#             if tmp_pixel == KNOWN_WIDTH:
#                 npixel = tmp_pixel
#                 nline = tmp_line
        
#         # Block 5: Calibration Information
#         if header[i] == 5 and header[i+1:i+3] == b'\x00\x93':
#             gain = struct.unpack(">d", header[i+9:i+17])[0]
#             offset = struct.unpack(">d", header[i+17:i+25])[0]

#     if npixel != KNOWN_WIDTH:
#         npixel = KNOWN_WIDTH
#         nline = len(raw[header_size:]) // (npixel * 2)

#     # 🛠️ Updated Band-Specific Defaults
#     if gain is None:
#         defaults = {"B08": 0.0003250, "B13": 0.0003342, "B14": 0.0003310}
#         gain = defaults.get(band_id, 0.0003342)

#     offset = offset if offset is not None else 0.0

#     # ==========================================================
#     # 3️⃣ IMAGE DATA EXTRACTION
#     # ==========================================================
#     image_bytes = raw[header_size:]
#     if len(image_bytes) % 2 != 0:
#         image_bytes = image_bytes[:-1]

#     data = np.frombuffer(image_bytes, dtype=">u2")
#     expected = nline * npixel

#     img = data[:expected].reshape(nline, npixel).astype(np.float32)
#     img[img > 4095] = np.nan

#     print(f"✅ {band_id} Successfully Loaded: {img.shape}")
#     return img, gain, offset


import bz2
import numpy as np
import struct
from pathlib import Path


# ==========================================================
# HIMAWARI-9 GEO CONSTANTS (OFFICIAL)
# ==========================================================

SUB_LON = 140.7

CFAC = 10233137
LFAC = 10233137
COFF = 2750.5
LOFF = 2750.5

REQ = 6378.137
RPOL = 6356.7523
H = 42164.0

SUB_LON_RAD = np.deg2rad(SUB_LON)

TOTAL_LINES = 5500
TOTAL_SEGMENTS = 10
SEGMENT_HEIGHT = TOTAL_LINES // TOTAL_SEGMENTS


# ==========================================================
# HSD TILE READER
# ==========================================================

def read_hsd_tile(file_path: str):
    """
    Generalized Himawari HSD reader.
    Supports B08, B13, B14.
    """

    # ---------------- BAND DETECTION ----------------
    file_upper = file_path.upper()

    if "B08" in file_upper:
        band_id = "B08"
    elif "B14" in file_upper:
        band_id = "B14"
    else:
        band_id = "B13"

    print(f"\n📥 READING {band_id} FILE: {file_path}")

    # ---------------- LOAD FILE ----------------
    with bz2.open(Path(file_path), "rb") as bz_file:
        raw = bz_file.read()

    # ==========================================================
    # HEADER SIZE DETECTION
    # ==========================================================
    try:
        header_size = struct.unpack(">I", raw[11:15])[0]
    except:
        header_blocks = struct.unpack(">H", raw[0:2])[0]
        header_size = header_blocks * 2880

    if header_size >= len(raw) or header_size == 0:
        header_size = 2880 * 15

    header = raw[:header_size]

    # ==========================================================
    # READ IMAGE DIMENSIONS + CALIBRATION
    # ==========================================================
    nline, npixel = 0, 0
    gain, offset = None, None

    KNOWN_WIDTH = 5500

    for i in range(0, len(header) - 150):

        # ---- Block 2 (image info)
        if header[i] == 2 and header[i+1:i+3] == b'\x00\x32':
            tmp_pixel = struct.unpack(">H", header[i+5:i+7])[0]
            tmp_line = struct.unpack(">H", header[i+7:i+9])[0]

            if tmp_pixel == KNOWN_WIDTH:
                npixel = tmp_pixel
                nline = tmp_line

        # ---- Block 5 (calibration)
        if header[i] == 5 and header[i+1:i+3] == b'\x00\x93':
            gain = struct.unpack(">d", header[i+9:i+17])[0]
            offset = struct.unpack(">d", header[i+17:i+25])[0]

    if npixel != KNOWN_WIDTH:
        npixel = KNOWN_WIDTH
        nline = len(raw[header_size:]) // (npixel * 2)

    # default calibration
    defaults = {
        "B08": 0.0003250,
        "B13": 0.0003342,
        "B14": 0.0003310
    }

    if gain is None:
        gain = defaults.get(band_id, 0.0003342)

    offset = offset if offset is not None else 0.0

    # ==========================================================
    # IMAGE EXTRACTION
    # ==========================================================
    image_bytes = raw[header_size:]

    if len(image_bytes) % 2 != 0:
        image_bytes = image_bytes[:-1]

    data = np.frombuffer(image_bytes, dtype=">u2")

    expected = nline * npixel
    img = data[:expected].reshape(nline, npixel).astype(np.float32)

    img[img > 4095] = np.nan

    print(f"✅ {band_id} Successfully Loaded: {img.shape}")
    print(f"{band_id} gain: {gain}")
    print(f"{band_id} offset: {offset}")

    return img, gain, offset


# ==========================================================
# GEO CONVERSION
# ==========================================================

def pixel_latlon(line, col, segment_index):
    """
    Convert pixel → latitude/longitude
    """

    # line_offset = (segment_index - 1) * SEGMENT_HEIGHT
    line_offset = 0

    l = line + line_offset
    c = col

    x = np.deg2rad((c - COFF) / CFAC * 2**16)
    y = np.deg2rad((l - LOFF) / LFAC * 2**16)

    cosx = np.cos(x)
    cosy = np.cos(y)
    siny = np.sin(y)

    a = (H*cosx*cosy)**2 - (
        cosy**2 + (REQ**2/RPOL**2)*siny**2
    ) * (H**2 - REQ**2)

    if a <= 0:
        return np.nan, np.nan

    sd = np.sqrt(a)

    sn = (H*cosx*cosy - sd) / (
        cosy**2 + (REQ**2/RPOL**2)*siny**2
    )

    s1 = H - sn*cosx*cosy
    s2 = sn*np.sin(x)*cosy
    s3 = -sn*siny

    lat = np.rad2deg(
        np.arctan((REQ**2/RPOL**2) *
        (s3 / np.sqrt(s1**2 + s2**2)))
    )

    lon = np.rad2deg(
        SUB_LON_RAD + np.arctan2(s2, s1)
    )
    # Normalize longitude to -180 to 180
    if lon > 180:
        lon -= 360
    elif lon < -180:
        lon += 360

    return lat, lon


# ==========================================================
# DEBUG TILE BOUNDS
# ==========================================================

def print_tile_bounds(img, segment_index):

    h, w = img.shape

    print("\n🌍 TILE GEO BOUNDS (VALID EARTH PIXELS):")

    lat_list = []
    lon_list = []

    # sample grid instead of corners
    for r in range(0, h, 20):
        for c in range(0, w, 50):

            lat, lon = pixel_latlon(r, c, segment_index)

            if not np.isnan(lat) and not np.isnan(lon):
                lat_list.append(lat)
                lon_list.append(lon)

    if len(lat_list) == 0:
        print("❌ No valid earth pixels found")
        return

    print(f"LAT range: {min(lat_list):.2f} → {max(lat_list):.2f}")
    print(f"LON range: {min(lon_list):.2f} → {max(lon_list):.2f}")

    center_lat = np.mean(lat_list)
    center_lon = np.mean(lon_list)

    print(f"📍 Center (computed): LAT={center_lat:.2f}, LON={center_lon:.2f}")
