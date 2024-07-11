from vesicle_picker import (
    postprocess,
    helpers,
    external_import,
    external_export
)
from tqdm import tqdm
import argparse
from cryosparc.tools import Dataset
import os

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

# Pull micrographs object from the output of a curate exposures job
micrographs = external_import.micrographs_from_csparc(
    cs=cs,
    project_id=parameters.get('csparc_input', 'PID'),
    job_id=parameters.get('csparc_input', 'JID'),
    job_type=parameters.get('csparc_input', 'type')
)

# Initialize the final Dataset
vesicle_picks = Dataset()
vesicle_picks.add_fields(
    ['location/micrograph_uid',
     'location/exp_group_id',
     'location/micrograph_path',
     'location/micrograph_shape',
     'location/center_x_frac',
     'location/center_y_frac',
     'location/micrograph_psize_A'],
    ["<u8", "<u4", "str", "<u4", "<f4", "<f4", "<f4"])

# Loop over all micrographs in the job directory
for micrograph in tqdm(micrographs[0:]):

    # Extract the micrograph UID
    uid = micrograph['uid']

    # Construct the filename of the file to import
    masks_filename = (
        parameters.get('input', 'directory')+str(uid)+"_vesicles_filtered.pkl"
    )

    # If the mask filename isn't in the input directory
    # then go to the next micrograph
    if not os.path.isfile(masks_filename):
        continue

    # Read in the masks from that UID
    masks = external_import.import_masks_from_disk(masks_filename)

    # Apply the erosion or dilation set in the parameters
    # and generate picks based on the masks.
    if int(parameters.get('picking', 'dilation_radius')) < 0:
        masks = postprocess.erode_masks(
            masks,
            erosion=-int(parameters.get('picking', 'dilation_radius')),
            psize=float(parameters.get('general', 'psize')),
            downsample=int(parameters.get('general', 'downsample'))
        )

    elif int(parameters.get('picking', 'dilation_radius')) > 0:
        masks = postprocess.dilate_masks(
            masks,
            dilation=int(parameters.get('picking', 'dilation_radius')),
            psize=float(parameters.get('general', 'psize')),
            downsample=int(parameters.get('general', 'downsample'))
        )

    else:
        # Re-find the edges for picking, since they're lost on saving
        masks = [postprocess.find_contour(mask) for mask in masks]

    pick_indices = postprocess.generate_picks(
        masks,
        psize=float(parameters.get('general', 'psize')),
        downsample=int(parameters.get('general', 'downsample')),
        box_size=int(parameters.get('picking', 'box_size')),
        mode=parameters.get('picking', 'mode')
    )

    # Generate the picks dataset
    pick_dataset = external_export.construct_csparc_dataset(
        micrograph,
        pick_indices
    )

    # Append it to the master dataset
    vesicle_picks = vesicle_picks.append(pick_dataset)

# Push vesicle_picks to cryosparc
# Initialize project and job
project = cs.find_project(parameters.get('csparc_input', 'PID'))
job = project.create_external_job(
    parameters.get('csparc_input', 'WID'),
    title="Vesicle Picks"
)

# Tell the job what kind of output to expect
job.add_output("particle", "vesicle_picks", slots=["location"])

# Start the job, push the output to cryosparc, stop the job
job.start()
job.save_output("vesicle_picks", vesicle_picks)
job.stop()
