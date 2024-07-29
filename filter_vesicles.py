from vesicle_picker import (
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

# Pull micrographs object from the output of a curate exposures job
micrographs = external_import.micrographs_from_csparc(
    cs=cs,
    project_id=parameters.get('csparc_input', 'PID'),
    job_id=parameters.get('csparc_input', 'JID'),
    job_type=parameters.get('csparc_input', 'type')
)

# Loop over all micrographs in the job directory
for micrograph in tqdm(micrographs[:]):

    # Extract the micrograph UID
    uid = micrograph['uid']

    # Construct the filename of the file to import
    masks_filename = (
        parameters.get('input', 'directory')+str(uid)+"_vesicles.pkl"
    )

    # Read in the masks from that UID
    masks = external_import.import_masks_from_disk(masks_filename)

    # Filter these masks based on min and max values recorded in job parameters
    filtered_masks = postprocess.apply_filters(masks, parameters_filepath)

    # Don't write out if no masks pass filtering
    if len(filtered_masks) == 0:
        continue

    # Construct the filepath of the masks to save to disk
    filtered_masks_filename = (
        parameters.get('output', 'directory')+str(uid)+"_vesicles_filtered.pkl"
    )

    # Save the vesicles to the output directory
    # on a micrograph-by-micrograph basis
    external_export.export_masks_to_disk(
        filtered_masks,
        filtered_masks_filename,
        micrograph_uid=uid,
        compression='uint64')
