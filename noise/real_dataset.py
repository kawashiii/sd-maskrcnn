import os
import sys
import logging
from tqdm import tqdm

import cv2
import skimage.io
import numpy as np
import tensorflow as tf

from clutter import ClutterConfig
from augmentation import augment_img
from eval_coco import *

from train_clutter import mkdir_if_missing
import model as modellib, visualize, utils

"""
RealImageDataset creates a Matterport dataset object for a directory of real
images in order to ensure compatibility with functions from Saurabh's code and
MaskRCNN code, e.g. old benchmarking tools and image resizing for networks.

Directory structure must be as follows:

$base_path/
    test_indices.npy
    depth_ims/ (Depth images here)
        image_000000.png
        image_000001.png
        ...
    modal_segmasks/ (GT segmasks here, one channel)
        image_000000.png
        image_000001.png
        ...

"""

class RealImageDataset(utils.Dataset):
    def __init__(self, base_path=""):
        assert base_path != "", "You must provide the path to a dataset!"

        self.base_path = base_path
        super().__init__()

    def load(self, imset):
        split_file = os.path.join(self.base_path, '{:s}_indices.npy'.format(imset))
        self.image_id = np.load(split_file)
        self.add_class('clutter', 1, 'fg')

        # IMAGE PATH FORMAT HERE

        for i in self.image_id:
            p = os.path.join(self.base_path, 'depth_ims',
                             'image_{:06d}.png'.format(i))
            self.add_image('clutter', image_id=i, path=p, width=256, height=256)

    def load_image(self, image_id):
        info = self.image_info[image_id]
        image = cv2.imread(info['path'])
        assert(image is not None)
        if image.ndim == 2: image = np.tile(image[:,:,np.newaxis], [1,1,3])
        return image


    def load_mask(self, image_id):
        info = self.image_info[image_id]
        _image_id = info['id']
        Is = []
        file_name = os.path.join(self.base_path, 'modal_segmasks',
          'image_{:06d}.png'.format(_image_id))

        all_masks = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)

        for i in range(25):
          # file_name = os.path.join(self.base_path, 'occluded_segmasks',
          #   'image_{:06d}_channel_{:03d}.png'.format(_image_id, i))
          # I = cv2.imread(file_name, cv2.IMREAD_UNCHANGED) > 0
          I = all_masks == i+1 # We ignore the background, so the first instance is 0-indexed.
          if np.any(I):
            I = I[:,:,np.newaxis]
            Is.append(I)
        if len(Is) > 0:
            mask = np.concatenate(Is, 2)
        else:
            mask = np.zeros([info['height'], info['width'], 0], dtype=np.bool)
        # Making sure masks are always contiguous.
        # block = np.any(np.any(mask,0),0)
        # assert((not np.any(block)) or (not np.any(block[np.where(block)[0][-1]+1:])))
        # print(block)
        class_ids = np.array([1 for _ in range(mask.shape[2])])
        return mask, class_ids.astype(np.int32)


def prepare_real_image_test(model_path, dataset_path, indices_name, config_path=''):
    """Loads model with the appropriate config and prepares dataset.
    Set indices_name to name of appropriate indices file (<name>_indices.npy).
    Returns network inference config, loaded model, and dataset."""

    # TODO: inference configuration needs to match what the model was trained with

    # Configure and load specified model
    class InferenceConfig(ClutterConfig):
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1

    inference_config = InferenceConfig(mean=128)

    model_dir, model_name = os.path.split(model_path)
    model = modellib.MaskRCNN(mode='inference', config=inference_config,
                              model_dir=model_dir)

    # Load trained weights

    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)

    dataset_real = RealImageDataset(dataset_path)
    dataset_real.load(indices_name)
    dataset_real.prepare()

    return inference_config, model, dataset_real
