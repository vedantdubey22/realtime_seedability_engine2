

from ftplib import FTP
from datetime import datetime, timedelta
import os
import sys

# ==========================================================
# CONFIG
# ==========================================================

HOST = "ftp.ptree.jaxa.jp"
USER = ""
PASS = ""

SEGMENT = "S0410"   # Segment 4 of 10 (horizontal band)

LOG_FILE = "download_log.txt"

if not USER or not PASS:
    print("❌ ERROR: Set JAXA_USER and JAXA_PASS environment variables.")
    sys.exit(1)


# ==========================================================
# TIME LOGIC
# ==========================================================

def get_latest_slot():
    now = datetime.utcnow() - timedelta(minutes=20)
    minute = (now.minute // 10) * 10
    return now.replace(minute=minute, second=0, microsecond=0)


def build_remote_path(dt, band):
    year  = dt.strftime("%Y")
    month = dt.strftime("%m")
    day   = dt.strftime("%d")
    hour  = dt.strftime("%H")
    minute= dt.strftime("%M")

    # Resolution logic per band
    if band == "B03":
        resolution = "R05"      # 0.5 km
    elif band in ["B01", "B02", "B04"]:
        resolution = "R10"      # 1 km
    else:
        resolution = "R20"      # 2 km

    return (
        f"/jma/hsd/{year}{month}/{day}/{hour}/"
        f"HS_H09_{year}{month}{day}_{hour}{minute}_{band}_FLDK_{resolution}_{SEGMENT}.DAT.bz2"
    )


# ==========================================================
# DOWNLOAD LOGIC
# ==========================================================

def download_files(remote_local_map):
    try:
        ftp = FTP(HOST, timeout=300)
        ftp.login(USER, PASS)
        ftp.voidcmd('TYPE I')
        ftp.set_pasv(True)

        results = []

        for remote_path, local_name in remote_local_map.items():

            if os.path.exists(local_name):
                os.remove(local_name)
                print(f"🗑️ Deleted old {local_name}")

            print(f"\n⬇️ Downloading: {remote_path.split('/')[-1]}")

            try:
                expected_size = ftp.size(remote_path)
                print(f"📦 Expected size: {expected_size} bytes")

                with open(local_name, "wb") as f:
                    ftp.retrbinary(
                        f"RETR {remote_path}",
                        f.write,
                        blocksize=1024 * 1024
                    )

                actual_size = os.path.getsize(local_name)

                if expected_size and actual_size < expected_size:
                    print(f"❌ Incomplete: {actual_size}/{expected_size}")
                    results.append(False)
                else:
                    print(f"✅ Saved: {local_name} ({actual_size} bytes)")

                    with open(LOG_FILE, "a") as log:
                        log.write(f"{remote_path}  -->  {local_name}\n")

                    results.append(True)

            except Exception as e:
                print(f"❌ Download error: {e}")
                results.append(False)

        ftp.quit()
        return all(results)

    except Exception as e:
        print(f"❌ FTP Connection Error: {e}")
        return False


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("🚀 Himawari-9 Multi-Band Downloader (Segment S0410)")

    # Clear log
    open(LOG_FILE, "w").close()

    slot = get_latest_slot()
    prev_slot = slot - timedelta(minutes=10)

    print(f"🕒 Target UTC Slot: {slot.strftime('%Y-%m-%d %H:%M')}")

    # RGB bands
    REMOTE_B01_CURR = build_remote_path(slot, "B01")
    REMOTE_B02_CURR = build_remote_path(slot, "B02")
    REMOTE_B03_CURR = build_remote_path(slot, "B03")

    # Other bands
    REMOTE_B08_CURR = build_remote_path(slot, "B08")
    REMOTE_B13_CURR = build_remote_path(slot, "B13")
    REMOTE_B14_CURR = build_remote_path(slot, "B14")
    REMOTE_B13_PREV = build_remote_path(prev_slot, "B13")

    print("\n📂 Remote Files Being Requested:")
    print("B01      :", REMOTE_B01_CURR)
    print("B02      :", REMOTE_B02_CURR)
    print("B03      :", REMOTE_B03_CURR)
    print("B08      :", REMOTE_B08_CURR)
    print("B13      :", REMOTE_B13_CURR)
    print("B14      :", REMOTE_B14_CURR)
    print("B13_prev :", REMOTE_B13_PREV)

    LOCAL_FILES = {

        REMOTE_B01_CURR: "north_india_B01.dat.bz2",
        REMOTE_B02_CURR: "north_india_B02.dat.bz2",
        REMOTE_B03_CURR: "north_india_B03.dat.bz2",

        REMOTE_B08_CURR: "north_india_B08.dat.bz2",
        REMOTE_B13_CURR: "north_india_B13.dat.bz2",
        REMOTE_B13_PREV: "north_india_B13_prev.dat.bz2",
        REMOTE_B14_CURR: "north_india_B14.dat.bz2"
    }

    success = download_files(LOCAL_FILES)

    if success:
        print("\n🎯 MULTI-BAND DOWNLOAD COMPLETE (RGB + IR)")
        print(f"📝 Log saved to: {LOG_FILE}")
    else:
        print("\n⚠️ Some downloads failed. Check logs.")