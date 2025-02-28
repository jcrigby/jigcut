from PIL import Image, ImageDraw
import os

def main():
    # Configuration
    IMAGE_PATH = "diagonal_pebble_gradient.png"  # Update to your image file
    OUTPUT_PATH = "grid_output.png"
    ROWS = 5
    COLS = 5
    LINE_COLOR = (255, 0, 0)  # Red lines
    LINE_WIDTH = 2

    # Create output folder if needed
    output_dir = os.path.dirname(OUTPUT_PATH)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

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

    # Draw horizontal grid lines
    for r in range(1, ROWS):
        y = r * cell_height
        draw.line([(0, y), (width, y)], fill=LINE_COLOR, width=LINE_WIDTH)
        print(f"Drawing horizontal line at y={y}")

    # Draw vertical grid lines
    for c in range(1, COLS):
        x = c * cell_width
        draw.line([(x, 0), (x, height)], fill=LINE_COLOR, width=LINE_WIDTH)
        print(f"Drawing vertical line at x={x}")

    # Save the result
    try:
        grid_image.save(OUTPUT_PATH)
        print(f"Grid image saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error saving image: {e}")

if __name__ == "__main__":
    main()

