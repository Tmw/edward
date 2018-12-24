from PIL import Image
from processor import process


def main():
    # read image from disk
    image = Image.open("input.jpg")
    processed = process(image)
    processed.save("output.png", mimetype="image/png")


# Kick off main program
if __name__ == "__main__":
    main()
