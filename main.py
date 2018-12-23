from PIL import Image
from scipy.misc import imresize
import numpy as np
from keras.models import load_model
import tensorflow as tf

print("loading model")
model = load_model("./tfmodel/main_model.hdf5", compile=False)
graph = tf.get_default_graph()
print("model loaded..")

# define the tensorflow model input. Shape: (224, 224, 3).
DEFAULT_INPUT_SIZE = (224, 224)
THRESHOLD = 255 / 2


def classify(image):
    with graph.as_default():
        classification = model.predict(image[None, :, :, :])

    return classification.reshape((DEFAULT_INPUT_SIZE[0], DEFAULT_INPUT_SIZE[1], -1))


def normalize_input(image):
    """
    normalize the image to a format our trained model can work with.
    shrink image and convert to matrix of RGB values ranging between 0 to 1.
    """

    image = image.resize(DEFAULT_INPUT_SIZE)
    return np.array(image) / 255.0


def main():
    # read image from disk
    image = Image.open("input.jpg")
    normalized = normalize_input(image)

    # from the normalized image, make sure to only grab the RGB channels, so
    # that any alpha channels get dropped (if applicable)
    rgbs = normalized[:, :, 0:3]

    # feed the rgbs to our trained model and get a matrix of classifications.
    # the shape of the matrix is of shape: (224, 224, 2) where the z-axis
    # contains the classification of:
    # 0th index: background
    # 1st index: person
    classification = classify(rgbs)

    # grab the cells that our model has classified as person
    person = classification[:, :, 1]

    # once we have the classification; resize the matrix back to our original
    # image size so we can use the classification as a mask on our alpha channel
    classification = imresize(person, (image.height, image.width))

    # use classification as mask by writing 255 or 0 to the alpha channel
    # depending on the classification value.
    classification[classification > THRESHOLD] = 255
    classification[classification < THRESHOLD] = 0

    # combine our alpha matrix to the original image
    output = np.array(image)[:, :, 0:3]
    output = np.append(output, classification[:, :, None], axis=-1)
    output = Image.fromarray(output)
    output.save("output.png", mimetype="image/png")


# Kick off main program
if __name__ == "__main__":
    main()
