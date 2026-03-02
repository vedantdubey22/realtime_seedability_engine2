
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.colors import ListedColormap

# def plot_seedability(seed_map):
#     cmap = ListedColormap(["#d9d9d9", "#fdae61", "#1a9850"])
#     alpha = np.ones(seed_map.shape)
#     alpha[seed_map == -1] = 0.0

#     plt.figure(figsize=(8, 6))
#     img = plt.imshow(seed_map, cmap=cmap, vmin=0, vmax=2, alpha=alpha, interpolation='nearest')
    
#     # Gohana Marker
#     gohana_x, gohana_y = 210, 270 
#     plt.plot(gohana_x, gohana_y, 'ro', markersize=8, label='Gohana (Home)')
#     plt.text(gohana_x + 5, gohana_y, ' Gohana', color='red', fontweight='bold')

#     plt.title("Himawari-9 Real-Time Seedability Map\n(North India Focus)", fontsize=12)
#     cbar = plt.colorbar(img, ticks=[0, 1, 2], fraction=0.046, pad=0.04)
#     cbar.ax.set_yticklabels(['GRAY', 'AMBER', 'GREEN'])
    
#     plt.savefig("latest_seedability_map.png", dpi=300)
#     print("🎨 Map generated and saved as 'latest_seedability_map.png'")
    
#     # 🔥 FIX: Use non-blocking show
#     plt.show(block=False)
#     plt.pause(1) # Small pause to allow the window to render

"""2 bands"""

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.colors import ListedColormap

# def plot_seedability(seed_map):
#     # Colors: 0:Gray, 1:Amber, 2:Green
#     cmap = ListedColormap(["#d9d9d9", "#fdae61", "#1a9850"])
    
#     # Create transparency mask for Clear Sky (-1)
#     alpha = np.ones(seed_map.shape)
#     alpha[seed_map == -1] = 0.0

#     plt.figure(figsize=(10, 7))
#     img = plt.imshow(seed_map, cmap=cmap, vmin=0, vmax=2, alpha=alpha, interpolation='nearest')
    
#     # --- UPDATED: Dynamic Gohana Marker ---
#     # Note: If Gohana looks shifted, adjust these based on your current 1150-1850 crop
#     gohana_x, gohana_y = 180, 290 
#     plt.plot(gohana_x, gohana_y, 'ro', markersize=8, markeredgecolor='white', label='Gohana (Home)')
#     plt.text(gohana_x + 8, gohana_y, 'Gohana', color='red', fontweight='bold', 
#              bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

#     plt.title("Himawari-9 Real-Time Seedability Map\n(Dual-Band B13/B14 Filter Active)", fontsize=12)
#     plt.xlabel("Pixel Longitude (Relative to Crop)")
#     plt.ylabel("Pixel Latitude")

#     cbar = plt.colorbar(img, ticks=[0, 1, 2], fraction=0.046, pad=0.04)
#     cbar.ax.set_yticklabels(['GRAY (Ice/Haze)', 'AMBER (Watch)', 'GREEN (Seedable)'])
    
#     plt.grid(alpha=0.2, linestyle='--')
#     plt.savefig("latest_seedability_map.png", dpi=300, bbox_inches='tight')
#     print("🎨 Map generated and saved as 'latest_seedability_map.png'")
    
#     plt.show(block=False)
#     plt.pause(1)

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.colors import ListedColormap

# def plot_seedability(seed_map):
#     """
#     Static Seedability Plot with Tri-Band (B8+B13+B14) Logic metadata.
#     """
#     # Colors: 0:Gray, 1:Amber, 2:Green
#     cmap = ListedColormap(["#d9d9d9", "#fdae61", "#1a9850"])
    
#     # Create transparency mask for Clear Sky (-1)
#     alpha = np.ones(seed_map.shape)
#     alpha[seed_map == -1] = 0.0

#     plt.figure(figsize=(10, 7))
#     img = plt.imshow(seed_map, cmap=cmap, vmin=0, vmax=2, alpha=alpha, interpolation='nearest')
    
#     # --- Dynamic Gohana Marker (Center of Haryana) ---
#     gohana_x, gohana_y = 180, 290 
#     plt.plot(gohana_x, gohana_y, 'ro', markersize=8, markeredgecolor='white', label='Gohana (Home)')
#     plt.text(gohana_x + 8, gohana_y, 'Gohana', color='red', fontweight='bold', 
#              bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

#     # Updated Title to reflect B8 (Moisture) integration
#     plt.title("Himawari-9 Real-Time Seedability Map\n(Tri-Band B8/B13/B14 Filter Active)", fontsize=12)
#     plt.xlabel("Pixel Longitude (Gohana Focus Crop)")
#     plt.ylabel("Pixel Latitude")

#     # Legend indicating the strict Tri-Band criteria
#     cbar = plt.colorbar(img, ticks=[0, 1, 2], fraction=0.046, pad=0.04)
#     cbar.ax.set_yticklabels(['GRAY (Ice/Dry)', 'AMBER (Watch)', 'GREEN (Seedable)'])
    
#     # Grid and Save
#     plt.grid(alpha=0.1, linestyle='--')
#     plt.savefig("latest_seedability_map.png", dpi=300, bbox_inches='tight')
#     print("🎨 Tri-Band Map saved as 'latest_seedability_map.png'")
    
#     plt.show(block=False)
#     plt.pause(1)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def plot_seedability(seed_map):
    """
    Static Seedability Plot updated for Physically-Aligned Engine.
    Reflects Depth (>2.5km) and LWP thresholds per documentation.
    """
    # Colors: 0:Gray (Unsuitable), 1:Amber (Watch), 2:Green (High Potential)
    cmap = ListedColormap(["#d9d9d9", "#fdae61", "#1a9850"])
    
    # Create transparency mask for Clear Sky (-1)
    alpha = np.ones(seed_map.shape)
    alpha[seed_map == -1] = 0.0

    plt.figure(figsize=(10, 8))
    img = plt.imshow(seed_map, cmap=cmap, vmin=0, vmax=2, alpha=alpha, interpolation='nearest')
    
    # --- Gohana Marker ---
    gohana_x, gohana_y = 180, 290 
    plt.plot(gohana_x, gohana_y, 'ro', markersize=8, markeredgecolor='white')
    plt.text(gohana_x + 8, gohana_y, 'Gohana (Analysis Center)', color='red', 
             fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    # Title reflects physical alignment
    plt.title("Himawari-9 Real-Time Seedability Map\nPhysically Aligned: CTT / Growth / Depth / LWP", fontsize=12)
    plt.xlabel("Pixel Longitude")
    plt.ylabel("Pixel Latitude")

    # Legend indicating physical criteria
    cbar = plt.colorbar(img, ticks=[0, 1, 2], fraction=0.046, pad=0.04)
    cbar.ax.set_yticklabels([
        'GRAY (Shallow/Ice/Dry)', 
        'AMBER (Watch: 1-2km depth)', 
        'GREEN (Potential: >2.5km depth)'
    ])
    
    plt.grid(alpha=0.1, linestyle='--')
    plt.savefig("latest_seedability_map.png", dpi=300, bbox_inches='tight')
    print("🎨 Physically-aligned map saved as 'latest_seedability_map.png'")
    
    plt.show(block=False)
    plt.pause(1)