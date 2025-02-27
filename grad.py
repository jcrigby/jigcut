import numpy as np
from PIL import Image
from noise import pnoise2  # Install with: pip install noise

# Image size (for high-quality 500-piece puzzle)
width, height = 4800, 4800  

# Define crayon colors in (R, G, B)
colors = np.array([
    [255, 0, 0],     # Red
    [255, 165, 0],   # Orange
    [255, 255, 0],   # Yellow
    [0, 255, 0],     # Green
    [0, 0, 255]      # Blue
])

# Define stops based on diagonal distance
diag_length = np.sqrt(width**2 + height**2)  # Diagonal distance
stops = np.linspace(0, diag_length, len(colors))

# Create a grid of x, y coordinates
x, y = np.meshgrid(np.arange(width), np.arange(height))
dist_from_corner = np.sqrt(x**2 + y**2)  # Compute distance from (0,0)

# Initialize gradient array
gradient = np.zeros((height, width, 3), dtype=np.uint8)

# Interpolate colors along the diagonal
for i in range(len(colors) - 1):
    mask = (dist_from_corner >= stops[i]) & (dist_from_corner < stops[i + 1])
    weight = (dist_from_corner[mask] - stops[i]) / (stops[i + 1] - stops[i])

    for j in range(3):  # Loop over R, G, B channels
        gradient[..., j][mask] = (
            (1 - weight) * colors[i, j] + weight * colors[i + 1, j]
        )

# Convert to an image
gradient_image = Image.fromarray(gradient)

# --- Apply Perlin Noise Pebble Texture ---
# Perlin noise settings
scale = 500  # Controls pebble size (higher = larger pebbles)
octaves = 6  # More octaves = more detail
persistence = 0.5  # Controls smoothness
lacunarity = 2.0  # Frequency change per octave

# Generate Perlin noise texture
noise_texture = np.zeros((height, width), dtype=np.float32)
for y in range(height):
    for x in range(width):
        noise_texture[y, x] = pnoise2(x / scale, y / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)

# Normalize Perlin noise to 0-255 range
noise_texture = (noise_texture - noise_texture.min()) / (noise_texture.max() - noise_texture.min()) * 255
pebble_texture = Image.fromarray(noise_texture.astype(np.uint8)).convert("L")  # Convert to grayscale

# Blend gradient with Perlin noise texture
blended_image = Image.blend(gradient_image, pebble_texture.convert("RGB"), alpha=0.2)  # Adjust alpha for strength

# Save and show final textured gradient
blended_image.save("diagonal_pebble_gradient.png")
blended_image.show()

