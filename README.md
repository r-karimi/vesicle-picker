![banner](docs/vesicle_picker_banner_withtext.png)

## Installation ##
- Ensure [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.anaconda.com/miniconda/) is installed on your machine.  
- If you wish to run the Segment Anything model on GPU, ensure [CUDA](https://docs.nvidia.com/cuda/) is installed on your machine.  
- Clone this repository:  
	```
	git clone https://github.com/r-karimi/vesicle-picker.git
	```
- Enter this repository:
	```
	cd vesicle_picker
	```
- Create a clean conda virtual environment.
	```
	conda create -n vesicle-picker
 	conda activate vesicle-picker
 	conda install pip
 	```
- Edit the [`pyproject.toml`](pyproject.toml) file in the base directory to install the correction version of PyTorch, PyTorch vision, and PyTorch audio for your machine.
	- Note your version of CUDA and Python by running:
 		```
   		nvcc --version
   		python --version
   		```
	- Browse the [PyTorch wheels](https://download.pytorch.org/whl/torch/) to find the appropriate versions of PyTorch, PyTorch vision, and PyTorch audio for your installed versions of CUDA and Python (e.g. `cu118` for CUDA 11.8 and `cp39` for Python 3.9).
	- Modify `poe install-pytorch` in `pyproject.toml`:
	```
 	# For Python 3.9.X and CUDA 11.8
 	install-pytorch = "pip install torch==2.1.1+cu118 torchvision==0.16.1+cu118 torchaudio==2.1.1+cu118 -f https://download.pytorch.org/whl/torch_stable.html"
 	```
 
- Install `vesicle-picker` and dependencies:
	```
	pip install .
	poe install-pytorch
 	```
- Place Segment Anything model weights in repo base directory. They can be downloaded [here](https://github.com/facebookresearch/segment-anything#model-checkpoints).
- Modify csparc_login.ini to match your active CryoSPARC instance
