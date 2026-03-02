

from ftplib import FTP
from datetime import datetime, timedelta
import os
import sys

# ==========================================================
# CONFIG (USE ENV VARIABLES — DO NOT HARDCODE PASSWORD)
# ==========================================================

HOST = "ftp.ptree.jaxa.jp"
USER = ""
PASS = ""

SEGMENT = "S0410"  # North India band (segment 4)

if not USER or not PASS:
    print("❌ ERROR: Set JAXA_USER and JAXA_PASS environment variables.")
    sys.exit(1)


# ==========================================================
# TIME LOGIC (UTC BASED, 10-MIN SLOT)
# ==========================================================

def get_latest_slot():
    """
    Returns latest safe UTC slot.
    Subtract 20 minutes to avoid file-not-yet-uploaded issue.
    """
    now = datetime.utcnow() - timedelta(minutes=20)

    minute = (now.minute // 10) * 10
    slot = now.replace(minute=minute, second=0, microsecond=0)

    return slot


def build_remote_path(dt, band):
    year  = dt.strftime("%Y")
    month = dt.strftime("%m")
    day   = dt.strftime("%d")
    hour  = dt.strftime("%H")
    minute= dt.strftime("%M")

    return (
        f"/jma/hsd/{year}{month}/{day}/{hour}/"
        f"HS_H09_{year}{month}{day}_{hour}{minute}_{band}_FLDK_R20_{SEGMENT}.DAT.bz2"
    )


# ==========================================================
# DOWNLOAD LOGIC (SINGLE FTP SESSION)
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

    print("🚀 Himawari-9 Dynamic Multi-Band Downloader (Segment S0410)")

    slot = get_latest_slot()
    prev_slot = slot - timedelta(minutes=10)

    print(f"🕒 Target UTC Slot: {slot.strftime('%Y-%m-%d %H:%M')}")

    REMOTE_B08_CURR = build_remote_path(slot, "B08")
    REMOTE_B13_CURR = build_remote_path(slot, "B13")
    REMOTE_B14_CURR = build_remote_path(slot, "B14")
    REMOTE_B13_PREV = build_remote_path(prev_slot, "B13")

    LOCAL_FILES = {
        REMOTE_B08_CURR: "north_india_B08.dat.bz2",
        REMOTE_B13_CURR: "north_india_B13.dat.bz2",
        REMOTE_B13_PREV: "north_india_B13_prev.dat.bz2",
        REMOTE_B14_CURR: "north_india_B14.dat.bz2"
    }

    success = download_files(LOCAL_FILES)

    if success:
        print("\n🎯 TRI-BAND DOWNLOAD COMPLETE (Dynamic UTC Mode)")
    else:
        print("\n⚠️ Some downloads failed. Check logs.")