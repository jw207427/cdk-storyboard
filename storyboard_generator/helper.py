from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap

# Define function to create scene images with descriptions
def create_scene_images(description, image):

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        print("Error: Unable to load font file 'arial.ttf'")
        return None

    draw = ImageDraw.Draw(image)
    lines = wrap(description, width=75)  # Adjust the width value as needed
    text = "\n".join(lines)

    # Use getbbox() method for better efficiency
    bbox = draw.multiline_textbbox((10, 10), text, font=font)
    box_height = abs(bbox[3] - bbox[1])
    box_width = abs(bbox[2] - bbox[0])
    box_x = (image.width - box_width) // 2 - 10
    box_y = 20  # Set the vertical offset from the top border

    # Use a single draw.rectangle() call for better efficiency
    draw.rectangle(
        [(box_x, box_y), (box_x + box_width + 20, box_y + box_height + 10)],
        fill=(255, 255, 255)
    )
    draw.multiline_text((box_x + 5, box_y + 5), "\n".join(lines), font=font, fill=(0, 0, 0))
    return image