# import numpy as np
# import os
# import webbrowser
# import matplotlib.pyplot as plt
# import json

# # Internal product modules
# from products.read_tile import read_b13_tile
# from products.ctt import dn_to_bt, bt_to_ctt_c
# from products.growth import compute_growth_rate
# from products.cloud_mask import compute_cloud_mask
# from products.cloud_depth import compute_cloud_depth_index
# from products.lwp import compute_lwp_proxy

# # Logic and Visualization modules
# from decision.decision_logic import decide_seedability
# from visualize.plot_seedability import plot_seedability
# from visualize.plot_folium import generate_folium_map

# # File Config
# FILE_CURR = "north_india_B13.dat.bz2"
# FILE_PREV = "north_india_B13_prev.dat.bz2"

# def main():
#     print("🚀 Starting Real-Time Seedability Analysis Engine")

#     # --- Configuration Loading ---
#     selected_region = "haryana_uttarakhand"
#     try:
#         with open('config/regions.json', 'r') as f:
#             configs = json.load(f)
#             region_cfg = configs[selected_region]
#         print(f"📍 Region Loaded: {selected_region.upper()}")
#     except Exception as e:
#         print(f"❌ Error loading config: {e}")
#         return

#     if not os.path.exists(FILE_CURR) or not os.path.exists(FILE_PREV):
#         print("❌ Error: Satellite data files missing.")
#         return

#     # 1. Processing Pipeline
#     dn_curr, gain_curr, offset_curr = read_b13_tile(FILE_CURR)
#     dn_prev, gain_prev, offset_prev = read_b13_tile(FILE_PREV)
    
#     ctt_curr = bt_to_ctt_c(dn_to_bt(dn_curr, gain_curr, offset_curr))
#     ctt_prev = bt_to_ctt_c(dn_to_bt(dn_prev, gain_prev, offset_prev))

#     # 2. Filtering & Config-Driven Cropping
#     ctt_curr[ctt_curr < -100.0] = np.nan
#     ctt_prev[ctt_prev < -100.0] = np.nan

#     min_h, min_w = min(ctt_curr.shape[0], ctt_prev.shape[0]), min(ctt_curr.shape[1], ctt_prev.shape[1])
#     ctt_curr, ctt_prev = ctt_curr[:min_h, :min_w], ctt_prev[:min_h, :min_w]

#     l_start, l_end = region_cfg['crop']['lon_start'], region_cfg['crop']['lon_end']
#     ctt_curr = ctt_curr[:, l_start:l_end]
#     ctt_prev = ctt_prev[:, l_start:l_end]

#     print(f"✅ Crop Applied ({ctt_curr.shape}). Warmest: {np.nanmax(ctt_curr):.2f}°C")

#     # 3. Decision Logic (FIXED ARGUMENT ORDER)
#     growth = compute_growth_rate(ctt_curr, ctt_prev)
#     mask   = compute_cloud_mask(ctt_curr)
#     depth  = compute_cloud_depth_index(ctt_curr)
#     lwp    = compute_lwp_proxy(ctt_curr, growth)

#     # RE-ALIGNED: (ctt, growth, depth, lwp, cloud_mask)
#     seed = decide_seedability(ctt_curr, growth, depth, lwp, mask)

#     # 4. Diagnostics & Dual-Visualization
#     valid_mask = ~np.isnan(ctt_curr)
#     valid_count = np.count_nonzero(valid_mask)
#     print(f"📊 Valid atmospheric pixels: {valid_count}")

#     if valid_count > 0:
#         # Final Percentages
#         p_green = (np.count_nonzero(seed == 2) / valid_count) * 100
#         p_amber = (np.count_nonzero(seed == 1) / valid_count) * 100
#         p_gray  = (np.count_nonzero(seed == 0) / valid_count) * 100
#         p_none  = (np.count_nonzero((seed == -1) & valid_mask) / valid_count) * 100
        
#         print(f"  🟢 GREEN: {p_green:.2f}% | 🟠 AMBER: {p_amber:.2f}% | ⚪ GRAY: {p_gray:.2f}% | 🟦 NONE: {p_none:.2f}%")

#         # Static Matplotlib Map
#         plot_seedability(seed)

#         # Generate Folium using JSON metadata
#         print("🌐 Generating Interactive Map...")
#         html_file = "interactive_map.html"
#         generate_folium_map(seed, region_cfg, output_name=html_file) 
        
#         webbrowser.open(f"file://{os.path.abspath(html_file)}")
#         input("\n✅ Done! Press Enter to exit...")
#         plt.close('all')

# if __name__ == "__main__":
#     main()

""" 2 bands"""

# import numpy as np
# import os
# import webbrowser
# import matplotlib.pyplot as plt
# import json

# # Internal product modules
# from products.read_tile import read_hsd_tile
# from products.ctt import dn_to_bt, bt_to_ctt_c, compute_swd
# from products.growth import compute_growth_rate
# from products.cloud_mask import compute_cloud_mask

# # Logic and Visualization modules
# from decision.decision_logic import decide_seedability
# from visualize.plot_seedability import plot_seedability
# from visualize.plot_folium import generate_folium_map

# # File Config (Now including B14)
# FILE_B13_CURR = "north_india_B13.dat.bz2"
# FILE_B13_PREV = "north_india_B13_prev.dat.bz2"
# FILE_B14_CURR = "north_india_B14.dat.bz2"

# def main():
#     print("🚀 Starting Dual-Band Seedability Analysis Engine")

#     # --- 1. Configuration Loading ---
#     selected_region = "haryana_uttarakhand"
#     try:
#         with open('config/regions.json', 'r') as f:
#             configs = json.load(f)
#             region_cfg = configs[selected_region]
#         print(f"📍 Region Loaded: {selected_region.upper()}")
#     except Exception as e:
#         print(f"❌ Error loading config: {e}")
#         return

#     # --- 2. Dual-Band Processing Pipeline ---
#     # Load B13 (Primary Thermal)
#     dn13_curr, g13, o13 = read_hsd_tile(FILE_B13_CURR)
#     dn13_prev, _, _ = read_hsd_tile(FILE_B13_PREV)
    
#     # Load B14 (Clean IR for Split-Window)
#     dn14_curr, g14, o14 = read_hsd_tile(FILE_B14_CURR)

#     # Convert to Brightness Temperature (Kelvin)
#     bt13_curr = dn_to_bt(dn13_curr, g13, o13, band="B13")
#     bt13_prev = dn_to_bt(dn13_prev, g13, o13, band="B13")
#     bt14_curr = dn_to_bt(dn14_curr, g14, o14, band="B14")

#     # --- 3. Crop & Product Generation ---
#     l_start, l_end = region_cfg['crop']['lon_start'], region_cfg['crop']['lon_end']
    
#     # Crop CTT (Celsius)
#     ctt_curr = bt_to_ctt_c(bt13_curr[:, l_start:l_end])
#     ctt_prev = bt_to_ctt_c(bt13_prev[:, l_start:l_end])
    
#     # Crop & Compute SWD (Split-Window Difference)
#     swd_crop = compute_swd(bt13_curr[:, l_start:l_end], bt14_curr[:, l_start:l_end])

#     # Standard Products
#     growth = compute_growth_rate(ctt_curr, ctt_prev)
#     mask   = compute_cloud_mask(ctt_curr)

#     # --- 4. Decision Logic (Adding SWD) ---
#     # RE-ALIGNED: (ctt, growth, swd, cloud_mask)
#     seed = decide_seedability(ctt_curr, growth, swd_crop, mask)

#     # --- 5. Diagnostics & Visualization ---
#     valid_mask = ~np.isnan(ctt_curr)
#     valid_count = np.count_nonzero(valid_mask)
    
#     if valid_count > 0:
#         p_green = (np.count_nonzero(seed == 2) / valid_count) * 100
#         p_amber = (np.count_nonzero(seed == 1) / valid_count) * 100
#         p_gray  = (np.count_nonzero(seed == 0) / valid_count) * 100
        
#         print(f"📊 Results: 🟢 GREEN: {p_green:.2f}% | 🟠 AMBER: {p_amber:.2f}% | ⚪ GRAY: {p_gray:.2f}%")

#         html_file = "interactive_map.html"
#         generate_folium_map(seed, region_cfg, output_name=html_file) 
#         webbrowser.open(f"file://{os.path.abspath(html_file)}")
        
#         input("\n✅ Done! Press Enter to exit...")
#         plt.close('all')

# if __name__ == "__main__":
#     main()

"""3 bands"""

# import numpy as np
# import os
# import webbrowser
# import matplotlib.pyplot as plt
# import json

# # Internal product modules
# from products.read_tile import read_hsd_tile
# from products.ctt import dn_to_bt, bt_to_ctt_c, compute_swd
# from products.growth import compute_growth_rate
# from products.cloud_mask import compute_cloud_mask
# from products.lwp import compute_lwp_proxy
# from products.cloud_depth import compute_cloud_depth

# # Logic and Visualization modules
# from decision.decision_logic import decide_seedability
# from visualize.plot_seedability import plot_seedability
# from visualize.plot_folium import generate_folium_map

# # File Configuration for Tri-Band Data
# FILE_B08_CURR = "north_india_B08.dat.bz2"
# FILE_B13_CURR = "north_india_B13.dat.bz2"
# FILE_B13_PREV = "north_india_B13_prev.dat.bz2"
# FILE_B14_CURR = "north_india_B14.dat.bz2"

# def main():
#     print("🚀 Starting Physically-Aligned Tri-Band Engine")

#     # --- 1. Configuration Loading ---
#     selected_region = "active_data_zone"
#     try:
#         with open('config/regions.json', 'r') as f:
#             configs = json.load(f)
#             region_cfg = configs[selected_region]
#         print(f"📍 Region Loaded: {selected_region.upper()}")
#     except Exception as e:
#         print(f"❌ Config Error: {e}")
#         return

#     # --- 2. Tri-Band Processing & Radiance Conversion ---
#     dn08_curr, g08, o08 = read_hsd_tile(FILE_B08_CURR)
#     dn13_curr, g13, o13 = read_hsd_tile(FILE_B13_CURR)
#     dn13_prev, _, _     = read_hsd_tile(FILE_B13_PREV)
#     dn14_curr, g14, o14 = read_hsd_tile(FILE_B14_CURR)

#     bt08_curr = dn_to_bt(dn08_curr, g08, o08, band="B08")
#     bt13_curr = dn_to_bt(dn13_curr, g13, o13, band="B13")
#     bt13_prev = dn_to_bt(dn13_prev, g13, o13, band="B13")
#     bt14_curr = dn_to_bt(dn14_curr, g14, o14, band="B14")

#     # --- 3. Crop & Physically-Aligned Product Generation ---
#     l_start, l_end = region_cfg['crop']['lon_start'], region_cfg['crop']['lon_end']
    
#     ctt_curr = bt_to_ctt_c(bt13_curr[:, l_start:l_end])
#     ctt_prev = bt_to_ctt_c(bt13_prev[:, l_start:l_end])
#     bt08_crop = bt08_curr[:, l_start:l_end]
#     bt13_crop = bt13_curr[:, l_start:l_end]

#     # Calculate indicators defined in documentation
#     swd_crop  = compute_swd(bt13_crop, bt14_curr[:, l_start:l_end])
#     lwp_score = compute_lwp_proxy(bt08_crop, bt13_crop)
#     depth_km  = compute_cloud_depth(ctt_curr, surface_temp_c=40.0) 
#     growth    = compute_growth_rate(ctt_curr, ctt_prev)
#     mask      = compute_cloud_mask(ctt_curr)

#     # --- 4. Decision Logic (Executing Physical Constraints) ---
#     # Aligned with CTT < -10C, Depth > 2.5km, and LWP 20-35 dBZ proxy
#     seed = decide_seedability(ctt_curr, growth, swd_crop, depth_km, lwp_score, mask)

#     # --- 5. Diagnostics & Visualization ---
#     valid_count = np.count_nonzero(~np.isnan(ctt_curr))
#     if valid_count > 0:
#         print(f"📊 Green: {(np.sum(seed==2)/valid_count)*100:.2f}% | Amber: {(np.sum(seed==1)/valid_count)*100:.2f}%")
        
#         # Updated Visuals to include Depth Overlay
#         plot_seedability(seed)
#         generate_folium_map(
#             seed, 
#             region_cfg, 
#             bt08_crop=bt08_crop, 
#             # depth_km=depth_km, 
#             output_name="interactive_map.html"
#         )
        
#         webbrowser.open(f"file://{os.path.abspath('interactive_map.html')}")
#         print("\n✅ Seedability Engine Cycle Complete.")

# if __name__ == "__main__":
#     main()


""" to show sir"""
# import numpy as np
# import os
# import webbrowser
# import matplotlib.pyplot as plt
# import json

# # Internal product modules
# from products.read_tile import read_hsd_tile, print_tile_bounds
# from products.ctt import dn_to_bt, bt_to_ctt_c, compute_swd
# from products.growth import compute_growth_rate
# from products.cloud_mask import compute_cloud_mask
# from products.lwp import compute_lwp_proxy
# from products.cloud_depth import compute_cloud_depth

# # Logic and Visualization modules
# from decision.decision_logic import decide_seedability
# from visualize.plot_seedability import plot_seedability
# from visualize.plot_folium import generate_folium_map


# # ==========================================================
# # FILE CONFIG
# # ==========================================================

# FILE_B08_CURR = "north_india_B08.dat.bz2"
# FILE_B13_CURR = "north_india_B13.dat.bz2"
# FILE_B13_PREV = "north_india_B13_prev.dat.bz2"
# FILE_B14_CURR = "north_india_B14.dat.bz2"


# def main():

#     print("🚀 Starting Physically-Aligned Tri-Band Engine")

#     # ------------------------------------------------------
#     # 1️⃣ LOAD REGION CONFIG
#     # ------------------------------------------------------
#     selected_region = "active_data_zone"

#     try:
#         with open('config/regions.json', 'r') as f:
#             configs = json.load(f)
#             region_cfg = configs[selected_region]

#         print(f"📍 Region Loaded: {selected_region.upper()}")

#     except Exception as e:
#         print(f"❌ Config Error: {e}")
#         return

#     # ------------------------------------------------------
#     # 2️⃣ READ HIMAWARI DATA
#     # ------------------------------------------------------
#     dn08_curr, g08, o08 = read_hsd_tile(FILE_B08_CURR)
#     dn13_curr, g13, o13 = read_hsd_tile(FILE_B13_CURR)
#     dn13_prev, _, _     = read_hsd_tile(FILE_B13_PREV)
#     dn14_curr, g14, o14 = read_hsd_tile(FILE_B14_CURR)

#     # 🔥 GEO DEBUG (VERY IMPORTANT)
#     # S0410 = segment 4 (India tile)
#     print_tile_bounds(dn13_curr, segment_index=4)

#     # ------------------------------------------------------
#     # 3️⃣ RADIANCE → BRIGHTNESS TEMP
#     # ------------------------------------------------------
#     bt08_curr = dn_to_bt(dn08_curr, g08, o08, band="B08")
#     bt13_curr = dn_to_bt(dn13_curr, g13, o13, band="B13")
#     bt13_prev = dn_to_bt(dn13_prev, g13, o13, band="B13")
#     bt14_curr = dn_to_bt(dn14_curr, g14, o14, band="B14")

#     # ------------------------------------------------------
#     # 4️⃣ REGION CROP
#     # ------------------------------------------------------
#     l_start = region_cfg['crop']['lon_start']
#     l_end   = region_cfg['crop']['lon_end']

#     ctt_curr = bt_to_ctt_c(bt13_curr[:, l_start:l_end])
#     ctt_prev = bt_to_ctt_c(bt13_prev[:, l_start:l_end])

#     bt08_crop = bt08_curr[:, l_start:l_end]
#     bt13_crop = bt13_curr[:, l_start:l_end]

#     # ------------------------------------------------------
#     # 5️⃣ PHYSICAL PRODUCTS
#     # ------------------------------------------------------
#     swd_crop  = compute_swd(bt13_crop, bt14_curr[:, l_start:l_end])
#     lwp_score = compute_lwp_proxy(bt08_crop, bt13_crop)
#     depth_km  = compute_cloud_depth(ctt_curr, surface_temp_c=40.0)
#     growth    = compute_growth_rate(ctt_curr, ctt_prev)
#     mask      = compute_cloud_mask(ctt_curr)

#     # ------------------------------------------------------
#     # 6️⃣ DECISION ENGINE
#     # ------------------------------------------------------
#     seed = decide_seedability(
#         ctt_curr,
#         growth,
#         swd_crop,
#         depth_km,
#         lwp_score,
#         mask
#     )

#     # ------------------------------------------------------
#     # 7️⃣ VISUALIZATION
#     # ------------------------------------------------------
#     valid_count = np.count_nonzero(~np.isnan(ctt_curr))

#     if valid_count > 0:

#         print(
#             f"📊 Green: {(np.sum(seed==2)/valid_count)*100:.2f}% | "
#             f"Amber: {(np.sum(seed==1)/valid_count)*100:.2f}%"
#         )

#         plot_seedability(seed)

#         generate_folium_map(
#             seed,
#             region_cfg,
#             bt08_crop=bt08_crop,
#             output_name="interactive_map.html"
#         )

#         webbrowser.open(
#             f"file://{os.path.abspath('interactive_map.html')}"
#         )

#         print("\n✅ Seedability Engine Cycle Complete.")


# if __name__ == "__main__":
#     main()



import numpy as np
import os
import webbrowser
import matplotlib.pyplot as plt
import json

# Internal product modules
from products.read_tile import read_hsd_tile, print_tile_bounds
from products.ctt import dn_to_bt, bt_to_ctt_c, compute_swd
from products.growth import compute_growth_rate
from products.cloud_mask import compute_cloud_mask
from products.lwp import compute_lwp_proxy
from products.cloud_depth import compute_cloud_depth

# Logic and Visualization modules
from decision.decision_logic import decide_seedability
from visualize.plot_seedability import plot_seedability
from visualize.plot_folium import generate_folium_map


# ==========================================================
# FILE CONFIG
# ==========================================================

FILE_B08_CURR = "north_india_B08.dat.bz2"
FILE_B13_CURR = "north_india_B13.dat.bz2"
FILE_B13_PREV = "north_india_B13_prev.dat.bz2"
FILE_B14_CURR = "north_india_B14.dat.bz2"


def main():

    print("🚀 Starting Physically-Aligned Tri-Band Engine")

    # ------------------------------------------------------
    # 1️⃣ LOAD REGION CONFIG
    # ------------------------------------------------------
    selected_region = "active_data_zone"

    try:
        with open('config/regions.json', 'r') as f:
            configs = json.load(f)
            region_cfg = configs[selected_region]

        print(f"📍 Region Loaded: {selected_region.upper()}")

    except Exception as e:
        print(f"❌ Config Error: {e}")
        return

    # ------------------------------------------------------
    # 2️⃣ READ HIMAWARI DATA
    # ------------------------------------------------------
    dn08_curr, g08, o08 = read_hsd_tile(FILE_B08_CURR)
    dn13_curr, g13, o13 = read_hsd_tile(FILE_B13_CURR)
    dn13_prev, _, _     = read_hsd_tile(FILE_B13_PREV)
    dn14_curr, g14, o14 = read_hsd_tile(FILE_B14_CURR)

    # 🔥 GEO DEBUG (VERY IMPORTANT)
    # S0410 = segment 4 (India tile)
    print_tile_bounds(dn13_curr, segment_index=4)

    # ------------------------------------------------------
    # 3️⃣ RADIANCE → BRIGHTNESS TEMP
    # ------------------------------------------------------
    bt08_curr = dn_to_bt(dn08_curr, g08, o08, band="B08")
    bt13_curr = dn_to_bt(dn13_curr, g13, o13, band="B13")
    bt13_prev = dn_to_bt(dn13_prev, g13, o13, band="B13")
    bt14_curr = dn_to_bt(dn14_curr, g14, o14, band="B14")

    # ------------------------------------------------------
    # 4️⃣ REGION CROP
    # ------------------------------------------------------
    l_start = region_cfg['crop']['lon_start']
    l_end   = region_cfg['crop']['lon_end']

    ctt_curr = bt_to_ctt_c(bt13_curr[:, l_start:l_end])
    ctt_prev = bt_to_ctt_c(bt13_prev[:, l_start:l_end])

    bt08_crop = bt08_curr[:, l_start:l_end]
    bt13_crop = bt13_curr[:, l_start:l_end]

    # ------------------------------------------------------
    # 5️⃣ PHYSICAL PRODUCTS
    # ------------------------------------------------------
    swd_crop  = compute_swd(bt13_crop, bt14_curr[:, l_start:l_end])
    lwp_score = compute_lwp_proxy(bt08_crop, bt13_crop)
    depth_km = compute_cloud_depth(ctt_curr, surface_temp_c=15.0)

    growth    = compute_growth_rate(ctt_curr, ctt_prev)
    mask = compute_cloud_mask(ctt_curr, lwp_score)


    # ------------------------------------------------------
    # 6️⃣ DECISION ENGINE
    # ------------------------------------------------------
    seed = decide_seedability(
        ctt_curr,
        growth,
        swd_crop,
        depth_km,
        lwp_score,
        mask
    )

    # ------------------------------------------------------
    # 7️⃣ VISUALIZATION
    # ------------------------------------------------------
    valid_count = np.count_nonzero(~np.isnan(ctt_curr))

    if valid_count > 0:

        print(
            f"📊 Green: {(np.sum(seed==2)/valid_count)*100:.2f}% | "
            f"Amber: {(np.sum(seed==1)/valid_count)*100:.2f}%"
        )

        plot_seedability(seed)

        generate_folium_map(
            seed,
            region_cfg,
            bt08_crop=bt08_crop,
            output_name="interactive_map.html"
        )

        webbrowser.open(
            f"file://{os.path.abspath('interactive_map.html')}"
        )

        print("\n✅ Seedability Engine Cycle Complete.")


if __name__ == "__main__":
    main()
