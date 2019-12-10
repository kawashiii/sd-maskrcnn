
FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget nano vim gcc make libopencv-dev \
    python3 python3-dev python3-pip python3-tk && \
    pip3 install --upgrade pip setuptools

RUN mkdir /root/src && cd /root/src && \
    git clone -b sd_maskrcnn https://github.com/damien-petit/Mask_RCNN &&\
    cd Mask_RCNN && \
    python3 -m pip install -r requirements_gpu.txt && \
    python3 -m pip install pycocotools && \
    python3 setup.py install && \
    wget -q https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5

RUN jupyter notebook --generate-config && \
    echo 'c.NotebookApp.ip = "*"\nc.NotebookApp.open_browser = False\nc.NotebookApp.token = ""\nc.NotebookApp.allow_root = True' > /root/.jupyter/jupyter_notebook_config.py

