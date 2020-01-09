
FROM nvidia/cuda:10.0-cudnn7-runtime-ubuntu16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget nano vim gcc make libopencv-dev unrar \
    python3 python3-dev python3-pip python3-tk python3-rtree && \
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

RUN cd /root/src && \
    git clone -b lab_config https://github.com/kawashiii/sd-maskrcnn && \
    cd sd-maskrcnn && bash install.sh && \
    wget -q https://berkeley.box.com/shared/static/7aurloy043f1py5nukxo9vop3yn7d7l3.rar && \
    unrar x 7aurloy043f1py5nukxo9vop3yn7d7l3.rar datasets/wisdom/ && \
    rm 7aurloy043f1py5nukxo9vop3yn7d7l3.rar
