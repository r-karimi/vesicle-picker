from cryosparc.tools import downsample as csparc_downsample
from cv2 import GaussianBlur, medianBlur, bilateralFilter


def preprocess_micrograph(image_fullres,
                          downsample,
                          lowpass_mode,
                          **kwargs):

    """
    Take a full-resolution image (2D numpy array) from download_mrc,
    downsample it by a given factor, and apply a user-defined lowpass filter.

    Arguments:
    image_fullres (np.ndarray): A two-dimensional numpy array
    from download_mrc.
    downsample (int): The image will be downsampled
    by this factor.
    lowpass_mode (str): The smoothing filter applied to the downsampled
    image; "gaussian" for Gaussian blur, "median" for Median filtering,
    and "bilateral" for Bilateral filtering.
    **kwargs: Keyword arguments to pass to the lowpass function of choice.

    Outputs:
    blur (np.ndarray): A two-dimensional numpy array with
    downsampling and smoothing filtering applied.
    """

    # Downsample the micrograph using cryosparc-tools
    image = csparc_downsample(image_fullres, downsample)

    # Apply a lowpass blurring function to the micrograph
    if lowpass_mode == "gaussian":
        blur = GaussianBlur(image, **kwargs)
    elif lowpass_mode == "median":
        blur = medianBlur(image, **kwargs)
    elif lowpass_mode == "bilateral":
        blur = bilateralFilter(image,  **kwargs)
    else:
        raise Exception(
            "Please input a valid lowpass mode (gaussian, median, bilateral)."
        )

    # Return the blurred micrograph
    return blur
