from PIL import Image
from scipy.misc import imresize
import numpy as np
from keras.models import load_model
import tensorflow as tf
from logger import EdwardLogger

# define the tensorflow model input. Shape: (224, 224, 3).
DEFAULT_INPUT_SIZE = (224, 224)
THRESHOLD = 255 / 2

# declare variables for model and graph to be loaded in later
model = None
graph = None


def classify(image):
    """
    classify runs the prediction on the normalized input
    """

    with graph.as_default():
        classification = model.predict(image[None, :, :, :])

    return classification.reshape(
        (DEFAULT_INPUT_SIZE[0], DEFAULT_INPUT_SIZE[1], -1)
    )


def prepare():
    """
    Loads the keras model from disk into a module global variable if not
    already present
    """

    global model, graph

    if model is None:
        EdwardLogger.info("loading tensorflow model")
        model = load_model("./tfmodel/main_model.hdf5", compile=False)
        EdwardLogger.info("tensorflow model loaded")

    if graph is None:
        graph = tf.get_default_graph()


def normalize_input(image):
    """
    normalize the image to a format our trained model can work with.
    shrink image and convert to matrix of RGB values ranging between 0.0 to 1.0
    """

    image = image.resize(DEFAULT_INPUT_SIZE)
    return np.array(image) / 255.0


def process(image):
    """
    `process` takes an image, processes it using a nural network and
    returns the image with alpha values applied, separating the subject from
    its background.
    """

    # first things first; let's process the image
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
    return Image.fromarray(output)
