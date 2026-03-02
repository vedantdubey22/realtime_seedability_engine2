# import folium
# from folium.raster_layers import ImageOverlay
# import numpy as np
# from PIL import Image
# import os

# def generate_folium_map(seed_map, region_cfg, output_name="interactive_map.html"):
#     """
#     Overlays seedability data using dynamic configuration from regions.json.
#     """
#     h, w = seed_map.shape
#     rgba_data = np.zeros((h, w, 4), dtype=np.uint8)

#     # 0: GRAY, 1: AMBER, 2: GREEN, -1: Transparent
#     rgba_data[seed_map == 0] = [217, 217, 217, 160] 
#     rgba_data[seed_map == 1] = [253, 174, 97, 255]  
#     rgba_data[seed_map == 2] = [26, 152, 80, 255]   
#     rgba_data[seed_map == -1] = [0, 0, 0, 0]        

#     img_path = "temp_layer.png"
#     Image.fromarray(rgba_data).save(img_path)

#     # Setup Map using JSON metadata
#     m = folium.Map(location=region_cfg['folium']['center'], zoom_start=7)

#     # Apply geographic bounds from JSON
#     ImageOverlay(
#         image=img_path,
#         bounds=region_cfg['folium']['bounds'],
#         opacity=0.7,
#         name="Real-Time Seedability"
#     ).add_to(m)

#     # Add dynamic marker
#     folium.Marker(
#         region_cfg['folium']['center'], 
#         popup=region_cfg['folium']['marker_label'],
#         icon=folium.Icon(color='red', icon='home')
#     ).add_to(m)

#     folium.LayerControl().add_to(m)
#     m.save(output_name)
    
#     if os.path.exists(img_path):
#         os.remove(img_path)

"""2 bqnds"""

# import folium
# from folium.raster_layers import ImageOverlay
# import numpy as np
# from PIL import Image
# import os

# def generate_folium_map(seed_map, region_cfg, output_name="interactive_map.html"):
#     """
#     Overlays seedability data using dynamic configuration from regions.json.
#     Includes categorization for Green, Amber, and Gray (Ice/Haze) flags.
#     """
#     h, w = seed_map.shape
#     # Create an RGBA image (Red, Green, Blue, Alpha)
#     rgba_data = np.zeros((h, w, 4), dtype=np.uint8)

#     # --- Color Mapping per Documentation ---
#     # 2: 🟢 GREEN (High Potential - Liquid Rich)
#     rgba_data[seed_map == 2] = [26, 152, 80, 255]   

#     # 1: 🟠 AMBER (Watch Zone - Marginal)
#     rgba_data[seed_map == 1] = [253, 174, 97, 255]  

#     # 0: ⚪ GRAY (Ineffective - Ice/Shallow Haze)
#     # Using 160 alpha to make it semi-transparent so you can see the ground
#     rgba_data[seed_map == 0] = [200, 200, 200, 160] 

#     # -1: 🟦 NONE (Clear Sky)
#     rgba_data[seed_map == -1] = [0, 0, 0, 0]        

#     # Save temporary image for Folium overlay
#     img_path = "temp_layer.png"
#     Image.fromarray(rgba_data).save(img_path)

#     # Setup Map centered on your region (e.g., Gohana/Haryana)
#     m = folium.Map(
#         location=region_cfg['folium']['center'], 
#         zoom_start=7,
#         tiles="OpenStreetMap"
#     )

#     # Apply geographic bounds to stretch the satellite pixels correctly
#     ImageOverlay(
#         image=img_path,
#         bounds=region_cfg['folium']['bounds'],
#         opacity=0.8,
#         name="Real-Time Seedability Analysis",
#         interactive=True
#     ).add_to(m)

#     # Add Marker for your Analysis Center
#     folium.Marker(
#         region_cfg['folium']['center'], 
#         popup=region_cfg['folium']['marker_label'],
#         icon=folium.Icon(color='red', icon='info-sign')
#     ).add_to(m)

#     # Add Layer Control to toggle the analysis on/off
#     folium.LayerControl().add_to(m)
    
#     m.save(output_name)
    
#     # Cleanup temporary file
#     if os.path.exists(img_path):
#         os.remove(img_path)
    
#     print(f"✅ Interactive Map saved as: {output_name}")

"""3 bands"""

# import folium
# from folium.raster_layers import ImageOverlay
# import numpy as np
# from PIL import Image
# import os

# def generate_folium_map(seed_map, region_cfg, bt08_crop=None, output_name="interactive_map.html"):
#     """
#     Overlays seedability data.
#     If bt08_crop is provided, adds a Water Vapor moisture layer as a background option.
#     """
#     h, w = seed_map.shape
#     rgba_data = np.zeros((h, w, 4), dtype=np.uint8)

#     # --- Color Mapping per Documentation ---
#     rgba_data[seed_map == 2] = [26, 152, 80, 255]   # GREEN
#     rgba_data[seed_map == 1] = [253, 174, 97, 255]  # AMBER
#     rgba_data[seed_map == 0] = [200, 200, 200, 160] # GRAY
#     rgba_data[seed_map == -1] = [0, 0, 0, 0]        # NONE

#     img_path = "temp_layer.png"
#     Image.fromarray(rgba_data).save(img_path)

#     # Setup Map
#     m = folium.Map(
#         location=region_cfg['folium']['center'], 
#         zoom_start=7,
#         tiles="OpenStreetMap"
#     )

#     # 1️⃣ Add Seedability Layer
#     ImageOverlay(
#         image=img_path,
#         bounds=region_cfg['folium']['bounds'],
#         opacity=0.8,
#         name="Seedability Analysis",
#         interactive=True
#     ).add_to(m)

#     # 2️⃣ Add Optional Moisture Background (B08)
#     if bt08_crop is not None:
#         # Normalize BT08 (Water Vapor) to grayscale for visualization
#         # Standard range for mid-level vapor is ~210K to 270K
#         b08_norm = np.clip((bt08_crop - 210) / (270 - 210) * 255, 0, 255).astype(np.uint8)
#         b08_path = "temp_b08.png"
#         Image.fromarray(b08_norm).save(b08_path)
        
#         ImageOverlay(
#             image=b08_path,
#             bounds=region_cfg['folium']['bounds'],
#             opacity=0.4,
#             name="Water Vapor (Moisture Fuel)",
#             show=False # Hidden by default, toggleable in Layer Control
#         ).add_to(m)

#     # Add Marker and Controls
#     folium.Marker(
#         region_cfg['folium']['center'], 
#         popup=region_cfg['folium']['marker_label'],
#         icon=folium.Icon(color='red', icon='info-sign')
#     ).add_to(m)

#     folium.LayerControl().add_to(m)
#     m.save(output_name)
    
#     # Cleanup
#     for path in [img_path, "temp_b08.png"]:
#         if os.path.exists(path):
#             os.remove(path)
    
#     print(f"✅ Interactive Map saved as: {output_name}")
import folium
from folium.raster_layers import ImageOverlay
import numpy as np
from PIL import Image
import os


def generate_folium_map(
    seed_map,
    region_cfg,
    bt08_crop=None,
    output_name="interactive_map.html"
):
    """
    Interactive Folium visualization.

    Layers:
    - Seedability classification (Green / Amber / Gray)
    - Optional Water Vapor (B08) moisture background
    """

    h, w = seed_map.shape

    # =====================================================
    # 1️⃣ CREATE RGBA SEEDABILITY IMAGE
    # =====================================================
    rgba_data = np.zeros((h, w, 4), dtype=np.uint8)

    # --- Documentation aligned colors ---
    rgba_data[seed_map == 2] = [26, 152, 80, 255]    # GREEN
    rgba_data[seed_map == 1] = [253, 174, 97, 255]   # AMBER
    rgba_data[seed_map == 0] = [200, 200, 200, 160]  # GRAY
    rgba_data[seed_map == -1] = [0, 0, 0, 0]         # NONE (transparent)

    img_path = "temp_layer.png"
    Image.fromarray(rgba_data).save(img_path)

    # =====================================================
    # 2️⃣ CREATE BASE MAP
    # =====================================================
    m = folium.Map(
        location=region_cfg['folium']['center'],
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    # =====================================================
    # 3️⃣ SEEDABILITY OVERLAY
    # =====================================================
    ImageOverlay(
        image=img_path,
        bounds=region_cfg['folium']['bounds'],
        opacity=0.8,
        name="Seedability Analysis",
        interactive=True
    ).add_to(m)

    # =====================================================
    # 4️⃣ OPTIONAL WATER VAPOR BACKGROUND (B08)
    # =====================================================
    if bt08_crop is not None:

        # ---- SAFE NaN HANDLING ----
        # replace NaNs with dry baseline
        b08_clean = np.nan_to_num(bt08_crop, nan=210.0)

        # ---- NORMALIZATION RANGE (WV standard) ----
        vmin = 210.0   # dry upper atmosphere
        vmax = 270.0   # moist clouds

        b08_norm = (b08_clean - vmin) / (vmax - vmin)
        b08_norm = np.clip(b08_norm, 0, 1)

        # convert → uint8 safely
        b08_norm = (b08_norm * 255).astype(np.uint8)

        b08_path = "temp_b08.png"
        Image.fromarray(b08_norm).save(b08_path)

        ImageOverlay(
            image=b08_path,
            bounds=region_cfg['folium']['bounds'],
            opacity=0.4,
            name="Water Vapor (Moisture Fuel)",
            show=False
        ).add_to(m)

    # =====================================================
    # 5️⃣ TARGET MARKER
    # =====================================================
    folium.Marker(
        region_cfg['folium']['center'],
        popup=region_cfg['folium']['marker_label'],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # =====================================================
    # 6️⃣ LAYER CONTROL
    # =====================================================
    folium.LayerControl().add_to(m)

    m.save(output_name)

    # =====================================================
    # 7️⃣ CLEAN TEMP FILES
    # =====================================================
    for path in ["temp_layer.png", "temp_b08.png"]:
        if os.path.exists(path):
            os.remove(path)

    print(f"✅ Interactive Map saved as: {output_name}")
