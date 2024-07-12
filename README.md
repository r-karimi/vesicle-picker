![banner](docs/vesicle_picker_banner_withtext.png)

## Installation ##

1. Ensure [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.anaconda.com/miniconda/) is installed on your machine.  
2. If you wish to run the Segment Anything model on GPU, ensure [CUDA](https://docs.nvidia.com/cuda/) is installed on your machine. CUDA is not necessary if you wish to only run Segment Anything on your machine's CPU. 
3. Clone this repository:  
	```
	git clone https://github.com/r-karimi/vesicle-picker.git
	```
4. Enter this repository:
	```
	cd vesicle-picker
	```
5. Create a clean conda virtual environment.
	```
	conda create -n vesicle-picker
 	conda activate vesicle-picker
 	conda install pip
 	```
6. Edit the [`pyproject.toml`](pyproject.toml) file in the base directory to install the correction version of PyTorch, PyTorch vision, and PyTorch audio for your machine. These instructions differ based on whether you are installing PyTorch for CPU or GPU usage.

	### CPU Installation ###
	- Visit the [PyTorch](https://pytorch.org/get-started/locally/) installation page and select the appropriate options, ensuring that Pip is selected as the package manager and CPU is selected as the compute platform. Note the given install command.
 
	- Modify `install-pytorch` in `pyproject.toml` with this install command:
		```
 		# For CPU
 		install-pytorch = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
 		```

	### GPU Installation ###
	- Note your version of CUDA and Python by running:
		```
		nvcc --version
		python --version
		```
	- Browse the [PyTorch wheels](https://download.pytorch.org/whl/torch/) to find the appropriate versions of PyTorch, PyTorch vision, and PyTorch audio for your installed versions of CUDA and Python (e.g. `cu118` for CUDA 11.8 and `cp39` for Python 3.9).
 
	- Modify the `install-pytorch` command in `pyproject.toml` to match these versions:
		```
 		# For Python 3.9.X and CUDA 11.8
 		install-pytorch = "pip install torch==2.1.1+cu118 torchvision==0.16.1+cu118 torchaudio==2.1.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html"
 		```
  
8. Install `vesicle-picker` and dependencies:
	```
	pip install .
	poe install-pytorch
 	```
9. Download the Segment Anything [model weights](https://github.com/facebookresearch/segment-anything#model-checkpoints) and place them in the `vesicle-picker` repository. We recommend trying with the ViT-L model weights first.
10. Modify csparc_login.ini to match your active CryoSPARC instance from which micrographs will be imported into Vesicle Picker and into which particle locations will be exported.

## Usage ##

Before processing your own dataset, we recommend working through the introductory Jupyter notebook [`find_vesicles.ipynb`](tests/find_vesicles.ipynb). This notebook describes how the program imports data residing in cryosparc and describes each step of the processing pipeline.

To process your own dataset, follow the steps below:

### In CryoSPARC: ###

1. [Import](https://guide.cryosparc.com/processing-data/all-job-types-in-cryosparc/import/job-import-movies) your movies, then perform [patch motion correction](https://guide.cryosparc.com/processing-data/all-job-types-in-cryosparc/motion-correction/job-patch-motion-correction) and [patch CTF estimation](https://guide.cryosparc.com/processing-data/all-job-types-in-cryosparc/ctf-estimation/job-patch-ctf-estimation).
2. [Curate](https://guide.cryosparc.com/processing-data/all-job-types-in-cryosparc/exposure-curation/interactive-job-manually-curate-exposures) your motion-corrected micrographs.
3. Note the project ID, workspace ID, and job ID of your Curate Exposures job.

### In Python: ###

4. Find the optimal mask pre-processing and postprocessing parameters for your data by importing a test micrograph using the [`find_vesicles.ipynb`](tests/find_vesicles.ipynb) Jupyter notebook. We note in our paper that a combination of roundness and area postprocessing filters are sufficient to obtain high precision and recall in the task of finding synaptic vesicles. If these are sufficient for your dataset as well, then the parameters that need to be set by the user are as follows.
   
	- $\sigma_{space}$, $\sigma_{colour}$, and $d$ for the bilateral filter.
	- $roundness_{min}$ for the roundness filter.
	- $Area_{min}$ and $Area_{max}$ for the area filter.
 	- $r_{dilation}$ or $r_{erosion}$ for particle picks offset from the membrane edge.
	- Box size to control the density of the picks.	 

There are a variety of other postprocessing filters that can be applied to your data as well. These filters are commented out in [`parameters/filter_vesicles.ini`](parameters/filter_vesicles.ini) by default. More information about the various postprocessing methods implemented in this library can be found in [`vesicle_picker/postprocessing.py`](vesicle_picker/postprocessing.py).

5. Find vesicles by modifying the [`find_vesicles.ini`](parameters/find_vesicles.ini) parameter file with your desired parameters, ensuring to fill in the correct CryoSPARC information. Also make sure to fill in your CryoSPARC login information, using [`csparc_login.ini`](csparc_login.ini) as a template. Finally, indicate an appropriate output directory for the detected vesicles. These will be stored in Python `.pkl` files. We have pre-filled this parameter file with a reasonable set of starting parameters.

	When you're ready, run the [`find_vesicles.py`](find_vesicles.py) script. The script takes a file path to the parameters file as its only argument:
		```
		python find_vesicles.py parameters/find_vesicles.ini
 		```
7. Filter the found vesicles by modifying the [`filter_vesicles.ini`](parameters/filter_vesicles.ini) parameter file, uncommenting the types of filters that you want to use and setting their minimum and maximum values. **Ensure to set the input directory for this script as the output directory of `find_vesicles.py`.** Again, we have pre-filled this parameter file with a reasonable set of starting parameters.
   
   	When you're ready, run [`filter_vesicles.py`](filter_vesicles.py):
   
		```
		python filter_vesicles.py parameters/filter_vesicles.ini
 		```
8. Generate particle picks by modifying the [`generate_picks.ini`](parameters/generate_picks.ini) parameter file. Set the workspace into which the vesicle picks will be exported. Set the dilation or erosion radius if desired, and set box size parameter to control the density of picks. We recommend picking with a high density and removing duplicate particles later in CryoSPARC. **Ensure to set the input directory for this script as the output directory of `filter_vesicles.py`.**

   	Run [`filter_vesicles.py`](filter_vesicles.py):
		```
		python generate_picks.py parameters/generate_picks.ini
 		```
### In CryoSPARC: ###

8. 
## Reference ##
