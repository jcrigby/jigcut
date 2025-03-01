from PIL import Image, ImageDraw
import os
import random
import math

def main():
    # Configuration
    IMAGE_PATH = "diagonal_pebble_gradient.png"  # Update to your image file
    OUTPUT_PATH = "jigsaw_grid_output.png"
    ROWS = 5
    COLS = 5
    GRID_COLOR = (255, 0, 0)  # Red for basic grid
    DEBUG_COLOR = (0, 0, 0)    # Black for jigsaw curves
    GRID_WIDTH = 1
    CURVE_WIDTH = 3
    
    # Load the image
    try:
        image = Image.open(IMAGE_PATH).convert("RGBA")
        width, height = image.size
        print(f"Image loaded: {width}x{height} pixels")
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Create a copy to draw on
    grid_image = image.copy()
    draw = ImageDraw.Draw(grid_image)
    
    # Calculate cell dimensions
    cell_width = width // COLS
    cell_height = height // ROWS
    
    # Parameters for the jigsaw tab
    tab_height_h = min(cell_width, cell_height) * 0.25  # Horizontal tab height
    tab_width_h = min(cell_width, cell_height) * 0.6    # Horizontal tab width
    
    tab_height_v = min(cell_width, cell_height) * 0.25  # Vertical tab height
    tab_width_v = min(cell_width, cell_height) * 0.6    # Vertical tab width
    
    # Create a fixed pattern of innies and outies
    # Use a deterministic pattern or random generation with fixed seed
    random.seed(42)  # Fixed seed for reproducibility
    
    # Generate horizontal edge patterns (True = outie, False = innie)
    h_edges = {}
    v_edges = {}
    
    # For horizontal internal edges (ROWS-1 internal edges × COLS cells)
    for r in range(1, ROWS):
        for c in range(COLS):
            # At least one innie and one outie per edge
            h_edges[(r, c)] = random.choice([True, False])
    
    # For vertical internal edges (ROWS cells × COLS-1 internal edges)
    for r in range(ROWS):
        for c in range(1, COLS):
            v_edges[(r, c)] = random.choice([True, False])
    
    # Draw horizontal edges
    for r in range(ROWS + 1):
        for c in range(COLS):
            x_start = c * cell_width
            x_end = (c + 1) * cell_width
            y = r * cell_height
            
            if r == 0 or r == ROWS:
                # Draw straight lines for the outer edges
                draw.line([(x_start, y), (x_end, y)], fill=DEBUG_COLOR, width=CURVE_WIDTH)
            else:
                # Draw jigsaw curves for internal edges
                direction = 1 if h_edges[(r, c)] else -1  # 1 = outie (tab), -1 = innie (slot)
                draw_horizontal_edge(draw, x_start, x_end, y, direction, tab_height_h, tab_width_h, DEBUG_COLOR, CURVE_WIDTH)
    
    # Draw vertical edges
    for r in range(ROWS):
        for c in range(COLS + 1):
            x = c * cell_width
            y_start = r * cell_height
            y_end = (r + 1) * cell_height
            
            if c == 0 or c == COLS:
                # Draw straight lines for the outer edges
                draw.line([(x, y_start), (x, y_end)], fill=DEBUG_COLOR, width=CURVE_WIDTH)
            else:
                # Draw jigsaw curves for internal edges
                direction = 1 if v_edges[(r, c)] else -1  # 1 = outie (tab), -1 = innie (slot)
                draw_vertical_edge(draw, x, y_start, y_end, direction, tab_height_v, tab_width_v, DEBUG_COLOR, CURVE_WIDTH)
    
    # Save the result
    try:
        grid_image.save(OUTPUT_PATH)
        print(f"Jigsaw grid image saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error saving image: {e}")

def draw_horizontal_edge(draw, x_start, x_end, y, direction, tab_height, tab_width, color, width):
    """
    Draw horizontal jigsaw edge (either tab or slot)
    
    Parameters:
    - draw: ImageDraw object
    - x_start, x_end: start and end x-coordinates
    - y: y-coordinate of the edge
    - direction: 1 for tab (outie), -1 for slot (innie)
    - tab_height: height of tab/slot
    - tab_width: width of tab/slot section
    - color: line color
    - width: line width
    """
    # Calculate points
    mid_x = (x_start + x_end) / 2
    tab_y = y - (direction * tab_height)  # Peak of tab or slot
    
    # Junction points - where curves meet
    j1_x = mid_x - tab_width * 0.15
    j1_y = y - direction * tab_height * 0.4
    j2_x = mid_x + tab_width * 0.15
    j2_y = y - direction * tab_height * 0.4
    
    # Set the slope for the connection points
    # We'll define as the angle from horizontal, going UP
    slope_angle = 30  # Degrees from horizontal, upward
    vector_len = tab_width * 0.2
    
    # LEFT JUNCTION (J1) - Control points calculation
    # For left junction, the slope goes up and to the right (+x, -y)
    j1_in_x = j1_x - vector_len * math.cos(math.radians(slope_angle))  # Left of junction
    j1_in_y = j1_y + direction * vector_len * math.sin(math.radians(slope_angle))  # Below/above junction
    
    j1_out_x = j1_x + vector_len * math.cos(math.radians(slope_angle))  # Right of junction
    j1_out_y = j1_y - direction * vector_len * math.sin(math.radians(slope_angle))  # Above/below junction
    
    # RIGHT JUNCTION (J2) - Control points calculation 
    # For right junction, the slope goes up and to the left (-x, -y)
    j2_in_x = j2_x - vector_len * math.cos(math.radians(slope_angle))  # Left of junction
    j2_in_y = j2_y - direction * vector_len * math.sin(math.radians(slope_angle))  # Above/below junction
    
    j2_out_x = j2_x + vector_len * math.cos(math.radians(slope_angle))  # Right of junction
    j2_out_y = j2_y + direction * vector_len * math.sin(math.radians(slope_angle))  # Below/above junction
    
    # Define the path
    path = [(x_start, y)]
    
    # First Bézier - from start to first junction
    bezier1 = bezier_points(
        (x_start, y),  # Start point
        (x_start + tab_width*0.25, y),  # First control - horizontal out
        (j1_in_x, j1_in_y),  # Second control - leading into junction
        (j1_x, j1_y)  # End at first junction
    )
    path.extend(bezier1[1:])
    
    # Second Bézier - middle-left curve to peak
    bezier2 = bezier_points(
        (j1_x, j1_y),  # Start at first junction
        (j1_out_x, j1_out_y),  # First control - leading out of junction
        (mid_x - tab_width*0.3, tab_y + direction*tab_height*0.1),  # Second control
        (mid_x, tab_y)  # End at top/bottom center
    )
    path.extend(bezier2[1:])
    
    # Third Bézier - middle-right curve from peak to second junction
    bezier3 = bezier_points(
        (mid_x, tab_y),  # Start at top/bottom center
        (mid_x + tab_width*0.3, tab_y + direction*tab_height*0.1),  # First control
        (j2_in_x, j2_in_y),  # Second control - leading into junction
        (j2_x, j2_y)  # End at second junction
    )
    path.extend(bezier3[1:])
    
    # Fourth Bézier - from second junction to end
    bezier4 = bezier_points(
        (j2_x, j2_y),  # Start at second junction
        (j2_out_x, j2_out_y),  # First control - leading out of junction
        (x_end - tab_width*0.25, y),  # Second control - horizontal in
        (x_end, y)  # End point
    )
    path.extend(bezier4[1:])
    
    # Draw the path
    for i in range(1, len(path)):
        draw.line([path[i-1], path[i]], fill=color, width=width)

def draw_vertical_edge(draw, x, y_start, y_end, direction, tab_height, tab_width, color, width):
    """
    Draw vertical jigsaw edge (either tab or slot)
    
    Parameters:
    - draw: ImageDraw object
    - x: x-coordinate of the edge
    - y_start, y_end: start and end y-coordinates
    - direction: 1 for tab (outie), -1 for slot (innie)
    - tab_height: height of tab/slot (actually width in vertical edges)
    - tab_width: width of tab/slot section (actually height in vertical edges)
    - color: line color
    - width: line width
    """
    # Calculate points
    mid_y = (y_start + y_end) / 2
    tab_x = x - (direction * tab_height)  # Peak of tab or slot
    
    # Junction points - where curves meet
    j1_y = mid_y - tab_width * 0.15
    j1_x = x - direction * tab_height * 0.4
    j2_y = mid_y + tab_width * 0.15
    j2_x = x - direction * tab_height * 0.4
    
    # Set the slope for the connection points
    # For vertical edges, we'll use the same angle but rotated 90 degrees
    slope_angle = 30  # Degrees from vertical, towards right/left
    vector_len = tab_width * 0.2
    
    # TOP JUNCTION (J1) - Control points calculation
    # We need to swap x and y calculations and adjust for vertical orientation
    j1_in_y = j1_y - vector_len * math.cos(math.radians(slope_angle))  
    j1_in_x = j1_x + direction * vector_len * math.sin(math.radians(slope_angle))
    
    j1_out_y = j1_y + vector_len * math.cos(math.radians(slope_angle))
    j1_out_x = j1_x - direction * vector_len * math.sin(math.radians(slope_angle))
    
    # BOTTOM JUNCTION (J2) - Control points calculation
    j2_in_y = j2_y - vector_len * math.cos(math.radians(slope_angle))
    j2_in_x = j2_x - direction * vector_len * math.sin(math.radians(slope_angle))
    
    j2_out_y = j2_y + vector_len * math.cos(math.radians(slope_angle))
    j2_out_x = j2_x + direction * vector_len * math.sin(math.radians(slope_angle))
    
    # Define the path
    path = [(x, y_start)]
    
    # First Bézier - from start to first junction
    bezier1 = bezier_points(
        (x, y_start),  # Start point
        (x, y_start + tab_width*0.25),  # First control - vertical down
        (j1_in_x, j1_in_y),  # Second control - leading into junction
        (j1_x, j1_y)  # End at first junction
    )
    path.extend(bezier1[1:])
    
    # Second Bézier - middle-top curve to peak
    bezier2 = bezier_points(
        (j1_x, j1_y),  # Start at first junction
        (j1_out_x, j1_out_y),  # First control - leading out of junction
        (tab_x + direction*tab_height*0.1, mid_y - tab_width*0.3),  # Second control
        (tab_x, mid_y)  # End at left/right center
    )
    path.extend(bezier2[1:])
    
    # Third Bézier - middle-bottom curve from peak to second junction
    bezier3 = bezier_points(
        (tab_x, mid_y),  # Start at left/right center
        (tab_x + direction*tab_height*0.1, mid_y + tab_width*0.3),  # First control
        (j2_in_x, j2_in_y),  # Second control - leading into junction
        (j2_x, j2_y)  # End at second junction
    )
    path.extend(bezier3[1:])
    
    # Fourth Bézier - from second junction to end
    bezier4 = bezier_points(
        (j2_x, j2_y),  # Start at second junction
        (j2_out_x, j2_out_y),  # First control - leading out of junction
        (x, y_end - tab_width*0.25),  # Second control - vertical up
        (x, y_end)  # End point
    )
    path.extend(bezier4[1:])
    
    # Draw the path
    for i in range(1, len(path)):
        draw.line([path[i-1], path[i]], fill=color, width=width)

def bezier_points(p0, p1, p2, p3, steps=20):
    """
    Calculate points along a cubic Bezier curve.
    p0 = start point
    p1, p2 = control points
    p3 = end point
    """
    points = []
    for t in range(steps + 1):
        t = t / steps
        # Cubic Bezier formula
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points

if __name__ == "__main__":
    main()
