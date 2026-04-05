import numpy as np
import matplotlib.pyplot as plt

def get_color_map(values, cmap_name='viridis'):
    """
    Map values to colors using a colormap.

    Args:
        values (array-like): Values to map
        cmap_name (str): Matplotlib colormap name

    Returns:
        list: List of color strings
    """
    norm = plt.Normalize(vmin=np.min(values), vmax=np.max(values))
    cmap = plt.get_cmap(cmap_name)
    colors = [cmap(norm(v)) for v in values]
    # to hex
    hex_colors = ['#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255)) for r, g, b, a in colors]
    return hex_colors