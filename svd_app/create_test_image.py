from PIL import Image, ImageDraw
import os

def create_test_image():
    # Create a simple 512x512 gradient image
    img = Image.new('RGB', (512, 512), color='blue')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 400, 400], fill='red')
    draw.ellipse([200, 200, 300, 300], fill='yellow')
    img.save("test_input.png")
    print("Created test_input.png")

if __name__ == "__main__":
    create_test_image()
