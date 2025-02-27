import numpy as np
from PIL import Image, ImageDraw
import random
import os

# Load the gradient image
image_path = "diagonal_pebble_gradient.png"
image = Image.open(image_path)
width, height = image.size

# Define puzzle grid
rows, cols = 25, 25  # 25 x 25 grid = 500 pieces
piece_width = width // cols
piece_height = height // rows

# Directory to store pieces
output_dir = "jigsaw_pieces"
os.makedirs(output_dir, exist_ok=True)

# Generate jigsaw puzzle pieces
for row in range(rows):
    for col in range(cols):
        # Define the bounding box for the piece
        left = col * piece_width
        upper = row * piece_height
        right = left + piece_width
        lower = upper + piece_height

        # Extract the piece from the original image
        piece = image.crop((left, upper, right, lower))

        # Create a mask for the jigsaw edges
        mask = Image.new("L", (piece_width, piece_height), 0)
        draw = ImageDraw.Draw(mask)

        # Define tab size (proportional to piece size)
        tab_size = piece_width // 6

        # Randomly determine if each edge has a tab or a slot
        def get_tab_slot():
            return random.choice([-1, 1])  # -1 = slot, 1 = tab

        # Apply jigsaw edges
        top = get_tab_slot() if row > 0 else 0
        bottom = get_tab_slot() if row < rows - 1 else 0
        left_side = get_tab_slot() if col > 0 else 0
        right_side = get_tab_slot() if col < cols - 1 else 0

        # Function to draw a jigsaw tab or slot
        def draw_jigsaw_edge(draw, start, end, direction, horizontal=True):
            """Draws a jigsaw tab or slot on the piece mask."""
            mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
            tab_offset = tab_size * direction

            if horizontal:
                control1 = (mid[0] - tab_size // 2, mid[1] - tab_offset)
                control2 = (mid[0] + tab_size // 2, mid[1] - tab_offset)
            else:
                control1 = (mid[0] - tab_offset, mid[1] - tab_size // 2)
                control2 = (mid[0] - tab_offset, mid[1] + tab_size // 2)

            draw.line([start, control1, mid, control2, end], fill=255, width=2)

        # Draw edges
        draw.line([(0, 0), (piece_width, 0)], fill=255, width=2)  # Top
        draw.line([(0, 0), (0, piece_height)], fill=255, width=2)  # Left
        draw.line([(piece_width, 0), (piece_width, piece_height)], fill=255, width=2)  # Right
        draw.line([(0, piece_height), (piece_width, piece_height)], fill=255, width=2)  # Bottom

        # Add jigsaw tabs/slots
        if top:
            draw_jigsaw_edge(draw, (0, 0), (piece_width, 0), top)
        if bottom:
            draw_jigsaw_edge(draw, (0, piece_height), (piece_width, piece_height), bottom)
        if left_side:
            draw_jigsaw_edge(draw, (0, 0), (0, piece_height), left_side, horizontal=False)
        if right_side:
            draw_jigsaw_edge(draw, (piece_width, 0), (piece_width, piece_height), right_side, horizontal=False)

        # Apply mask
        piece.putalpha(mask)

        # Save the piece
        piece_path = os.path.join(output_dir, f"piece_{row}_{col}.png")
        piece.save(piece_path)

print(f"Jigsaw pieces saved to {output_dir}")

