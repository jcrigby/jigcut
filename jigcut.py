import math
import random
import os
from PIL import Image, ImageDraw

###############################################################################
# CONFIGURATION
###############################################################################

IMAGE_PATH = "diagonal_pebble_gradient.png"  # Update to your image file
OUTPUT_DIR = "jigsaw_pieces"
ROWS = 5
COLS = 5

# How large each "knob" or "tab" should be, as fraction of the piece dimension
TAB_FRACTION = 0.25

# How many line segments to approximate the arc
ARC_STEPS = 20

###############################################################################
# HELPER FUNCTIONS
###############################################################################

def arc_points(cx, cy, radius, start_deg, end_deg, steps=ARC_STEPS):
    """
    Generate a list of (x, y) approximating an arc of a circle
    centered at (cx, cy), going from start_deg to end_deg (degrees).
    """
    pts = []
    for i in range(steps + 1):
        t = start_deg + (end_deg - start_deg) * i / steps
        rad = math.radians(t)
        x = cx + radius * math.cos(rad)
        y = cy + radius * math.sin(rad)
        pts.append((x, y))
    return pts

###############################################################################
# MAIN PUZZLE LOGIC
###############################################################################

def main():
    # Load image
    image = Image.open(IMAGE_PATH).convert("RGBA")
    width, height = image.size
    
    # Compute piece sizes
    piece_width = width // COLS
    piece_height = height // ROWS

    # Create output folder
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create patterns (top/bottom edges, left/right edges)
    #  0 = flat, +1 = outward knob, -1 = inward slot
    tab_patterns = {}
    for r in range(ROWS + 1):
        tab_patterns[r] = {}
        for c in range(COLS):
            if r == 0 or r == ROWS:
                tab_patterns[r][c] = 0
            else:
                tab_patterns[r][c] = random.choice([-1, 1])
                
    side_patterns = {}
    for r in range(ROWS):
        side_patterns[r] = {}
        for c in range(COLS + 1):
            if c == 0 or c == COLS:
                side_patterns[r][c] = 0
            else:
                side_patterns[r][c] = random.choice([-1, 1])
    
    # Generate every puzzle piece
    for row in range(ROWS):
        for col in range(COLS):
            piece = create_piece(
                image, row, col, 
                piece_width, piece_height, 
                tab_patterns, side_patterns
            )
            piece.save(os.path.join(OUTPUT_DIR, f"piece_{row}_{col}.png"))
        print(f"Row {row + 1}/{ROWS} completed")
    
    print(f"All pieces saved to {OUTPUT_DIR}")

def create_piece(image, row, col, pw, ph, tpat, spat):
    """
    Create a single puzzle piece using arcs for curved tabs.
    row, col = which piece in puzzle grid
    pw, ph = piece width/height
    tpat = tab_patterns
    spat = side_patterns
    """
    # Coordinates for the piece in the source image
    x1, y1 = col * pw, row * ph
    x2, y2 = x1 + pw, y1 + ph
    
    # We add a buffer so that outward knobs fit
    buffer = int(min(pw, ph) * 0.5)  # bigger buffer ensures arcs won't get cut
    canvas_width = pw + 2 * buffer
    canvas_height = ph + 2 * buffer
    
    # Create new canvas & mask
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    mask = Image.new("L", (canvas_width, canvas_height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Edge definitions
    top_type = tpat[row][col]           # 0=flat, +1=outward, -1=inward
    bottom_type = tpat[row + 1][col]    # next row
    left_type = spat[row][col]          # 0=flat, +1=outward, -1=inward
    right_type = spat[row][col + 1]     # next col

    # For bottom & right, invert (so adjacent pieces match)
    bottom_type = -bottom_type if bottom_type != 0 else 0
    right_type = -right_type if right_type != 0 else 0

    # "Knob" or "tab" size
    tab_size = min(pw, ph) * TAB_FRACTION

    # We build up a polygon path (list of points) around the piece, clockwise.
    # The key is to have all edge functions return paths without the final point
    # (except for the last edge function call)
    # Start at top-left corner of the piece (in local coords).
    path = []
    
    # Add each edge's points to the path
    top_edge = edge_top(buffer, buffer, pw, top_type, tab_size)
    right_edge = edge_right(buffer + pw, buffer, ph, right_type, tab_size)
    bottom_edge = edge_bottom(buffer, buffer + ph, pw, bottom_type, tab_size)
    left_edge = edge_left(buffer, buffer, ph, left_type, tab_size)
    
    # Combine all edges to create the full path
    path = top_edge + right_edge + bottom_edge + left_edge
    
    # Draw the polygon
    draw.polygon(path, fill=255)
    
    # Copy the piece from original image
    piece_im = image.crop((x1, y1, x2, y2))
    canvas.paste(piece_im, (buffer, buffer))
    canvas.putalpha(mask)
    return canvas

###############################################################################
# EDGE SHAPES
###############################################################################

def edge_top(x_left, y_top, width_px, edge_type, tab_size):
    """
    Return a list of points from (x_left, y_top) to (x_left+width_px, y_top)
    with a possible half-circle arc in the middle if edge_type != 0.
    """
    # Start list with top-left corner
    pts = [(x_left, y_top)]
    x_right = x_left + width_px

    if edge_type == 0:
        # Flat line
        pts.append((x_right, y_top))

    else:
        mid_x = (x_left + x_right) / 2
        # The arc center is above (for outward=+1) or below (for inward=-1)
        arc_center_y = y_top - tab_size if edge_type == 1 else y_top + tab_size
        radius = abs(tab_size)

        # Move from left corner to ~1/4 across
        quarter_x = x_left + width_px / 4
        pts.append((quarter_x, y_top))

        # Arc from quarter_x to three_quarter_x 
        three_quarter_x = x_left + 3 * width_px / 4
        if edge_type == 1:
            # outward
            arc = arc_points(
                mid_x, arc_center_y, 
                radius,
                180, 0,
                steps=ARC_STEPS
            )
        else:
            # inward
            arc = arc_points(
                mid_x, arc_center_y, 
                radius,
                0, 180,
                steps=ARC_STEPS
            )
        pts.extend(arc)

        # Then go to top-right corner
        pts.append((three_quarter_x, y_top))
        pts.append((x_right, y_top))

    return pts

def edge_right(x_right, y_top, height_px, edge_type, tab_size):
    """
    Return a list of points going down the right edge.
    """
    pts = []
    y_bottom = y_top + height_px
    
    if edge_type == 0:
        pts.append((x_right, y_bottom))
    else:
        mid_y = (y_top + y_bottom) / 2
        arc_center_x = x_right + tab_size if edge_type == 1 else x_right - tab_size
        radius = abs(tab_size)

        # Move down ~1/4
        quarter_y = y_top + height_px / 4
        pts.append((x_right, quarter_y))

        # Arc from quarter_y to three_quarter_y
        three_quarter_y = y_top + 3 * height_px / 4
        if edge_type == 1:
            # outward
            arc = arc_points(arc_center_x, mid_y, radius, 270, 90, steps=ARC_STEPS)
        else:
            # inward
            arc = arc_points(arc_center_x, mid_y, radius, 90, 270, steps=ARC_STEPS)
        pts.extend(arc)

        # Then go to bottom-right corner
        pts.append((x_right, three_quarter_y))
        pts.append((x_right, y_bottom))

    return pts

def edge_bottom(x_left, y_bottom, width_px, edge_type, tab_size):
    """
    Return points for bottom edge, right to left
    """
    pts = []
    x_right = x_left + width_px

    if edge_type == 0:
        # Straight line to bottom-left
        pts.append((x_left, y_bottom))
    else:
        mid_x = (x_left + x_right) / 2
        arc_center_y = y_bottom + tab_size if edge_type == 1 else y_bottom - tab_size
        radius = abs(tab_size)

        # Move ~1/4 from the right
        quarter_x = x_right - width_px / 4
        pts.append((quarter_x, y_bottom))

        # Arc from quarter_x to one_quarter_x
        one_quarter_x = x_left + width_px / 4
        if edge_type == 1:
            # outward
            arc = arc_points(mid_x, arc_center_y, radius, 0, 180, steps=ARC_STEPS)
        else:
            # inward
            arc = arc_points(mid_x, arc_center_y, radius, 180, 0, steps=ARC_STEPS)
        pts.extend(arc)

        # Then to bottom-left corner
        pts.append((one_quarter_x, y_bottom))
        pts.append((x_left, y_bottom))

    return pts

def edge_left(x_left, y_top, height_px, edge_type, tab_size):
    """
    Return points for left edge, bottom to top
    """
    pts = []
    y_bottom = y_top + height_px

    if edge_type == 0:
        pts.append((x_left, y_top))
    else:
        mid_y = (y_top + y_bottom) / 2
        arc_center_x = x_left - tab_size if edge_type == 1 else x_left + tab_size
        radius = abs(tab_size)

        three_quarter_y = y_bottom - height_px / 4
        pts.append((x_left, three_quarter_y))

        if edge_type == 1:
            # outward
            arc = arc_points(arc_center_x, mid_y, radius, 90, 270, steps=ARC_STEPS)
        else:
            # inward
            arc = arc_points(arc_center_x, mid_y, radius, 270, 90, steps=ARC_STEPS)
        pts.extend(arc)

        quarter_y = y_top + height_px / 4
        pts.append((x_left, quarter_y))
        pts.append((x_left, y_top))

    return pts

###############################################################################
# EXECUTE
###############################################################################

if __name__ == "__main__":
    main()

