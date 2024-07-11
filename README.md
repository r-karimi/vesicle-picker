![banner](docs/vesicle_picker_banner_withtext.png)

# Installation Instructions
- Clone this repository: `git clone https://github.com/r-karimi/vesicle-picker.git`
- Enter this repository: `cd vesicle_picker`
- Create a clean python virtual environment with venv or conda, tested with Python version 3.9 but likely compatible with Python 3.X.
	- With venv: `python3 -m venv .` and `source venv/bin/activate`.
	- With conda: `conda create -n vesicle-picker`, `conda activate vesicle-picker`, `conda install python=3.9`, and `conda install pip`.	
- Edit the `pyproject.toml` file to install the correction version of PyTorch, PyTorch vision, and PyTorch audio for your hardware, matching both your version of CUDA (e.g. `cu118` for CUDA 11.8) and Python version (e.g. `cp39` for Python 3.9). Available PyTorch wheels are listed [here](https://download.pytorch.org/whl/torch/). GPU acceleration is highly recommended when possible.
- Install `vesicle-picker` package and dependencies with:
	- `pip install .`
	- `poe install-pytorch`
- Place segment-anything model weights in repo base directory. They can be downloaded [here](https://github.com/facebookresearch/segment-anything#model-checkpoints).
- Modify csparc_login.ini to match your active CryoSPARC instance
