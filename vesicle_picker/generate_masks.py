from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import numpy as np
import cv2
from torch.cuda import is_available


def initialize_model(model_weights_path, model_type='vit_h', device='cuda'):

    """
    Initialize a Segment-Anything model.

    Arguments:
    model_weights_path (str): The path to SAM model weights, absolute
    or relative to working directory.
    model_type (str): The model type ('vit_h' by default).
    device (str): The device on which the model will run
    ('cuda', 'cpu', or 'mps'. 'cuda' by default).

    Outputs:
    model (PyTorch model): An initialized segment-anything model.
    """

    # Check if the specified device is available
    if not is_available() and device == 'cuda':
        print("GPU not available. Switching to CPU.")
        device = 'cpu'

    # Define what kind of model you want
    model = sam_model_registry[model_type](checkpoint=model_weights_path)

    # Send the model to GPU
    model.to(device=device)

    # Return the model
    return model


def generate_masks(preprocessed_micrograph, model,
                   psize, downsample, **kwargs):

    """
    Apply a Segment-Anything model to automatic segmentation of a micrograph.

    Arguments:
    preprocessed_micrograph (np.ndarray): A 2D numpy array of a downsampled,
    blurred micrograph.
    model (PyTorch model): An initialized segment-anything model.
    **kwargs: Keyword arguments to be passed on to the segment-anything
    model. For more information, visit the segment-anything GitHub.

    Outputs:
    masks (list): A list of dictionaries, each dictionary representing a
    detected mask in preprocessed_micrograph.
    """

    # Normalize the values
    preprocessed_micrograph_uint8 = (
        cv2.normalize(preprocessed_micrograph, None, 0, 255,
                      cv2.NORM_MINMAX).astype("uint8")
    )

    # Generate a pseudo-colour image for segmentation
    preprocessed_micrograph_colour = (
        np.expand_dims(preprocessed_micrograph_uint8, axis=2)
    )
    preprocessed_micrograph_colour = (
        np.repeat(preprocessed_micrograph_colour, 3, axis=2)
    )
    # Initialize automatic mask generator class with desired params
    mask_generator = SamAutomaticMaskGenerator(model=model, **kwargs)

    # Generate masks on the preprocessed_micrograph
    masks = mask_generator.generate(preprocessed_micrograph_colour)

    # Modify the area of each mask to be in Angstrom squared
    for mask in masks:
        mask['area_asq'] = mask['area']*(downsample**2)*(psize**2)

    # Return the list of masks
    return masks
