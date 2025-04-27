# Installation for CV tools

1. create and activate the MainRender env

```bash
yes | conda create -n MainRender python=3.8
conda activate MainRender
conda install pytorch==2.1.2 pytorch-cuda=12.1 -c pytorch -c nvidia
```

2. install PaddleDetection

```bash
cd cv_tools/PaddleDetection
python -m pip install -e segment_anything
python -m pip install -r lama/requirements.txt
```

3. install Inpainting Anything, i.e., manipulating images using neural networks

```bash
cd cv_tools/Inpaint_Anything
python -m pip install -e segment_anything
python -m pip install -r lama/requirements.txt
```

4. install SAM and MiVOLO
```shell
pip -e git+https://github.com/facebookresearch/segment-anything.git
pip -e git+https://github.com/WildChlamydia/MiVOLO.git
```