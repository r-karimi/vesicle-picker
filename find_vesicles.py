from vesicle_picker import (
    preprocess,
    generate_masks,
    postprocess,
    helpers,
    external_import,
    external_export
)
from tqdm import tqdm
import argparse

# Read in the job parameters file
parser = argparse.ArgumentParser(description='Description of your script')
parser.add_argument(
    'parameters',
    type=str,
    help='Path to .ini file containing the parameters for vesicle picking.'
)
args = parser.parse_args()
parameters_filepath = args.parameters
parameters = helpers.read_config(parameters_filepath)

# Use the csparc_import module to initialize a cryosparc session
cs = external_import.load_cryosparc(parameters.get('csparc_input', 'login'))

# Define the project
project = cs.find_project(parameters.get('csparc_input', 'PID'))

# Pull micrographs object from the output of a curate exposures job
micrographs = external_import.micrographs_from_csparc(
    cs=cs,
    project_id=parameters.get('csparc_input', 'PID'),
    job_id=parameters.get('csparc_input', 'JID'),
    job_type=parameters.get('csparc_input', 'type')
)

# Initialize the model
model = generate_masks.initialize_model(
    model_weights_path=parameters.get('segmentation', 'model_weights_path'),
    model_type=parameters.get('segmentation', 'model_type'),
    device=parameters.get('segmentation', 'device')
)

# Loop over all micrographs in the job directory
for micrograph in tqdm(micrographs[:]):

    # Extract the image
    header, image_fullres = project.download_mrc(
        micrograph["micrograph_blob/path"]
    )
    image_fullres = image_fullres[0]

    # Extract the micrograph UID
    uid = micrograph['uid']

    # Use the preprocess module to get micrograph ready for segmentation.
    # This script uses bilateral filtering,
    # can be adjusted for Gaussian if desired.
    preprocessed_micrograph = preprocess.preprocess_micrograph(
        image_fullres,
        downsample_factor=parameters.getint('general', 'downsample'),
        lowpass_mode=parameters.get('preprocessing', 'lowpass_mode'),
        d=parameters.getint('preprocessing', 'd'),
        sigmaColor=parameters.getint('preprocessing', 'sigmaColor'),
        sigmaSpace=parameters.getint('preprocessing', 'sigmaSpace'))

    # Generate masks with user-optimized parameters
    masks = generate_masks.generate_masks(
        preprocessed_micrograph,
        model,
        psize=parameters.getfloat('general', 'psize'),
        downsample=parameters.getint('general', 'downsample'),
        points_per_side=parameters.getint('segmentation', 'points_per_side'),
        points_per_batch=parameters.getint('segmentation', 'points_per_batch'),
        pred_iou_thresh=parameters.getfloat('segmentation', 'pred_iou_thresh'),
        stability_score_thresh=(
            parameters.getfloat('segmentation', 'stability_score_thresh')
        ),
        crop_n_layers=parameters.getint('segmentation', 'crop_n_layers'),
        crop_n_points_downscale_factor=(
            parameters.getint('segmentation', 'crop_n_points_downscale_factor')
        ),
        crop_nms_thresh=parameters.getfloat('segmentation', 'crop_nms_thresh'),
        min_mask_region_area=(
            parameters.getint('segmentation', 'min_mask_region_area')
        )
    )

    if len(masks) == 0:
        continue

    # Use the postprocess module to compute statistics
    # on the vesicles for downstream filtering
    postprocessed_masks = postprocess.postprocess_masks(
        masks,
        eval(parameters.get('postprocessing', 'functions')),
        preprocessed_micrograph
    )

    # Modify the ellipse fitting key-value pairs to convert to Angstrom
    for mask in postprocessed_masks:
        if 'average_radius' in mask:
            psize = parameters.getfloat('general', 'psize')
            downsample = parameters.getint('general', 'downsample')
            mask['average_radius_A'] = (
                mask['average_radius'] * psize * downsample
            )
            mask['semi_minor_A'] = (
                mask['semi_minor'] * psize * downsample
            )
            mask['semi_major_A'] = (
                mask['semi_major'] * psize * downsample
            )

    # Construct the filepath of the masks to save to disk
    masks_filename = (
        parameters.get('output', 'directory')+str(uid)+"_vesicles.pkl"
    )

    # Save the vesicles to the output directory
    # on a micrograph-by-micrograph basis
    external_export.export_masks_to_disk(
        postprocessed_masks,
        masks_filename,
        micrograph_uid=uid,
        compression='uint64'
    )
