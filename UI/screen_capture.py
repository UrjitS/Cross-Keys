"""
This script takes a screenshot and overlays the mouse cursor on top of it.
"""
# isort: off
import pyautogui
from PIL import Image
from mss import mss

# Load cursor image and convert to RGBA
cursor_image = Image.open("cursor.png").convert("RGBA")

# Scale down cursor image
cursor_image = cursor_image.resize((100, 100))

# Take screenshot
with mss() as sct:
    screenshot = sct.grab(sct.monitors[0])

# Convert screenshot to PIL Image object
screenshot = Image.frombytes(
    "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
).convert("RGBA")

# Get mouse cursor position
cursor_x, cursor_y = pyautogui.position()

# Create a new image with the same size as the screenshot and paste the cursor onto it
cursor_layer = Image.new("RGBA", screenshot.size)
cursor_layer.paste(cursor_image, (cursor_x, cursor_y))

# Composite the screenshot and cursor layer
final_image = Image.alpha_composite(screenshot, cursor_layer)

# Save the screenshot
final_image.save("screenshot_with_cursor.png")
