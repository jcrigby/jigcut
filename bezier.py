from PIL import Image, ImageDraw
import math

def main():
    # Configuration
    OUTPUT_PATH = "reference_bezier.png"
    IMAGE_SIZE = (800, 400)  # Width, Height
    BG_COLOR = (255, 255, 255)  # White
    CURVE_COLOR = (0, 0, 0)    # Black for curve
    CONTROL_COLOR = (255, 0, 0)  # Red for control points
    END_POINT_COLOR = (0, 0, 255)  # Blue for end points
    CONTROL_LINE_COLOR = (200, 200, 200)  # Light gray for control lines
    CURVE_WIDTH = 3
    POINT_RADIUS = 5
    
    # Create a new image
    image = Image.new("RGB", IMAGE_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(image)
    
    # Define the normalized reference jigsaw tab
    # Points are defined in the format:
    # [(x, y), (control1_x, control1_y), (control2_x, control2_y), (next_x, next_y)]
    ref_curve = [
        # First segment: straight section to first curve
        [(0.0, 0.0), (0.33, 0.0), (0.38, 0.0), (0.4, 0.05)],
        
        # Second segment: rising to peak
        [(0.4, 0.05), (0.42, 0.1), (0.46, 0.9), (0.5, 1.0)],
        
        # Third segment: falling from peak
        [(0.5, 1.0), (0.54, 0.9), (0.58, 0.1), (0.6, 0.05)],
        
        # Fourth segment: straight section to end
        [(0.6, 0.05), (0.62, 0.0), (0.67, 0.0), (1.0, 0.0)]
    ]
    
    # Scale the curve to fit the image
    margin = 50  # Pixels
    scale_x = IMAGE_SIZE[0] - 2 * margin
    scale_y = IMAGE_SIZE[1] - 2 * margin
    
    # Function to transform normalized coordinates to image coordinates
    def transform(point):
        return (
            margin + point[0] * scale_x,
            IMAGE_SIZE[1] - margin - point[1] * scale_y  # Flip y to make tab point upward
        )
    
    # Draw control lines for each segment
    for segment in ref_curve:
        # Transform points
        p0 = transform(segment[0])  # Start point
        p1 = transform(segment[1])  # Control point 1
        p2 = transform(segment[2])  # Control point 2
        p3 = transform(segment[3])  # End point
        
        # Draw control lines
        draw.line([p0, p1], fill=CONTROL_LINE_COLOR, width=1)
        draw.line([p2, p3], fill=CONTROL_LINE_COLOR, width=1)
    
    # Draw the curve
    path = []
    for segment in ref_curve:
        # Transform points
        p0 = transform(segment[0])  # Start point
        p1 = transform(segment[1])  # Control point 1
        p2 = transform(segment[2])  # Control point 2
        p3 = transform(segment[3])  # End point
        
        # Calculate Bezier points
        bezier = bezier_points(p0, p1, p2, p3, steps=30)
        
        # Add to the path (avoid duplicating points)
        if not path:
            path.extend(bezier)
        else:
            path.extend(bezier[1:])
    
    # Draw the Bezier curve
    for i in range(1, len(path)):
        draw.line([path[i-1], path[i]], fill=CURVE_COLOR, width=CURVE_WIDTH)
    
    # Draw the control points and end points for each segment
    for i, segment in enumerate(ref_curve):
        # Transform points
        p0 = transform(segment[0])  # Start point
        p1 = transform(segment[1])  # Control point 1
        p2 = transform(segment[2])  # Control point 2
        p3 = transform(segment[3])  # End point
        
        # Draw control points (red)
        draw.ellipse([
            (p1[0] - POINT_RADIUS, p1[1] - POINT_RADIUS),
            (p1[0] + POINT_RADIUS, p1[1] + POINT_RADIUS)
        ], fill=CONTROL_COLOR)
        
        draw.ellipse([
            (p2[0] - POINT_RADIUS, p2[1] - POINT_RADIUS),
            (p2[0] + POINT_RADIUS, p2[1] + POINT_RADIUS)
        ], fill=CONTROL_COLOR)
        
        # Draw end points (blue) - but avoid duplicates
        if i == 0 or segment[0] != ref_curve[i-1][3]:  # Start point
            draw.ellipse([
                (p0[0] - POINT_RADIUS, p0[1] - POINT_RADIUS),
                (p0[0] + POINT_RADIUS, p0[1] + POINT_RADIUS)
            ], fill=END_POINT_COLOR)
        
        # Last end point of each segment
        draw.ellipse([
            (p3[0] - POINT_RADIUS, p3[1] - POINT_RADIUS),
            (p3[0] + POINT_RADIUS, p3[1] + POINT_RADIUS)
        ], fill=END_POINT_COLOR)
    
    # Label the segments and points
    labels = ["Segment 1", "Segment 2", "Segment 3", "Segment 4"]
    for i, segment in enumerate(ref_curve):
        # Calculate position for the label (near the middle of each segment)
        mid_t = 0.5  # Middle of the segment
        mid_x = (1-mid_t)**3 * segment[0][0] + 3*(1-mid_t)**2 * mid_t * segment[1][0] + 3*(1-mid_t) * mid_t**2 * segment[2][0] + mid_t**3 * segment[3][0]
        mid_y = (1-mid_t)**3 * segment[0][1] + 3*(1-mid_t)**2 * mid_t * segment[1][1] + 3*(1-mid_t) * mid_t**2 * segment[2][1] + mid_t**3 * segment[3][1]
        
        # Transform to image coordinates
        label_pos = transform((mid_x, mid_y + 0.05))  # Offset slightly for readability
        
        # Draw the label
        draw.text(label_pos, labels[i], fill=(0, 0, 0))
    
    # Save the result
    try:
        image.save(OUTPUT_PATH)
        print(f"Reference Bezier curve image saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error saving image: {e}")

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
