from cryosparc.tools import CryoSPARC
from vesicle_picker.helpers import read_config
import pickle

# Functions to take a cryosparc initialization, test the connection,
# load the project and job, and find the input micrographs depending
# on what kind of job led into it (i.e. curate exposures or patch ctf).


def load_cryosparc(csparc_login_path):

    """
    Initialize a cryosparc session with the credentials in
    a csparc_login.ini file.

    Arguments:
    csparc_login_path (str): Absolute or relative filepath to the
    csparc_login file containing email, password, etc.

    Outputs:
    cs (cryosparc object): A valid cryosparc session for further
    use downstream.
    """

    # Read the cryosparc login credentials
    config = read_config(csparc_login_path)

    # Initialize a cryosparc object
    cs = CryoSPARC(
        license=config.get('General', 'license'),
        host=config.get('General', 'host'),
        base_port=int(config.get('General', 'base_port')),
        email=config.get('UserCredentials', 'email'),
        password=config.get('UserCredentials', 'password')
    )

    # Test the connection to cryosparc
    assert cs.test_connection()

    # Return the object
    return cs


def micrographs_from_csparc(cs, project_id, job_id, job_type):

    """
    Initialize a cryosparc session with various user parameters.

    Arguments:
    cs (cryosparc object): A valid cryosparc session.
    project_id (str): A project ID within the cryosparc session (e.g. P12)
    job_id (str): A job ID within a project (e.g. J34)
    job_type: The job from which micrographs are being imported.
    Can be either a Curate Exposures job ("curate")
    or a patch CTF job ("patch_ctf").

    Outputs:
    micrographs (cryosparc Micrographs object): A collection
    of micrographs and associated parameters as a cryosparc object.
    """

    # Define the job
    job = cs.find_job(project_id, job_id)

    # Pull the micrographs object from cryosparc depending on job output
    if job_type == "curate":
        micrographs = job.load_output('exposures_accepted')
    elif job_type == "patch_ctf":
        micrographs = job.load_output('exposures')
    else:
        raise Exception("Please input a valid job_type (curate or patch_ctf).")

    return micrographs


def import_masks_from_disk(filename):

    """
    Import a pickle object containing masks compressed
    by export_masks_to_disk().

    Arguments:
    filename (str): The filename of the compressed masks on disk.

    Outputs:
    masks (list): The uncompressed masks with the 'segmentation' key
    repopulated and prepared for downstream analysis.
    """

    # Read in the exported masks from disk
    with open(filename, 'rb') as file:
        # Read the pickle file
        loaded_masks_pickle = pickle.load(file)

    # Regenerate the segmentation arrays
    for mask in loaded_masks_pickle['masks']:
        mask['segmentation'] = (
            loaded_masks_pickle['composite_mask'] % mask['prime_key'] == 0
        )
    return loaded_masks_pickle['masks']
