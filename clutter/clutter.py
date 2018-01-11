"""
Mask R-CNN
Configurations and data loading code for the synthetic Shapes dataset.
This is a duplicate of the code in the noteobook train_shapes.ipynb for easy
import into other notebooks, such as inspect_model.ipynb.

Copyright (c) 2017 Matterport, Inc.
Licensed under the MIT License (see LICENSE for details)
Written by Waleed Abdulla
"""

import numpy as np, cv2, os
from maskrcnn.config import Config
from tqdm import tqdm
import maskrcnn.utils as utils

# Structure of data from Jeff.
# depth_ims: image_{:06d}.png
# gray_ims: image_{:06d}.png
# occluded_segmasks: image_{:06d}_channel_{:03d}.png
# semantic_segmasks: image_{:06d}
# unoccluded_segmasks: image_{:06d}_channel_{:03d}.png
# splits/fold_{:02d}/{train,test}_indices.npy

class ClutterConfig(Config):
  """Configuration for training on the toy shapes dataset.
  Derives from the base Config class and overrides values specific
  to the toy shapes dataset.
  """
  # Give the configuration a recognizable name
  NAME = "clutter"

  # Train on 1 GPU and 8 images per GPU. We can put multiple images on each
  # GPU because the images are small. Batch size is 8 (GPUs * images/GPU).
  GPU_COUNT = 1
  IMAGES_PER_GPU = 2

  # Number of classes (including background)
  NUM_CLASSES = 1 + 1  # background + 3 shapes

  # Use small images for faster training. Set the limits of the small side
  # the large side, and that determines the image shape.
  IMAGE_MIN_DIM = 512
  IMAGE_MAX_DIM = 512

  # Use smaller anchors because our image and objects are small
  RPN_ANCHOR_SCALES = (8, 16, 32, 64, 128)  # anchor side in pixels

  # Reduce training ROIs per image because the images are small and have
  # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
  TRAIN_ROIS_PER_IMAGE = 32

  # Use a small epoch since the data is simple
  STEPS_PER_EPOCH = 10000/IMAGES_PER_GPU

  # use small validation steps since the epoch is small
  VALIDATION_STEPS = 50
  
  DETECTION_MIN_CONFIDENCE = 0.4
  
  def __init__(self):
    # Overriding things here.
    super().__init__()
    self.IMAGE_SHAPE[2] = 3
    self.MEAN_PIXEL = np.array([128., 128., 128.])

class ClutterDataset(utils.Dataset):
  """Generates the shapes synthetic dataset. The dataset consists of simple
  shapes (triangles, squares, circles) placed randomly on a blank surface.
  The images are generated on the fly. No file access required.
  """
  def load(self, imset, typ='depth', fold=0):
    # Load the indices for imset.
    self.base_path = os.path.join('../clutter_segmentation_11_07_17/')
    split_file = os.path.join(self.base_path, 'splits',
      'fold_{:02d}'.format(fold), '{:s}_indices.npy'.format(imset))
    self.image_id = np.load(split_file)
    self.add_class('clutter', 1, 'fg')

    for i in self.image_id:
      p = os.path.join(self.base_path, '{:s}_ims'.format(typ), 
        'image_{:06d}.png'.format(i))
      self.add_image('clutter', image_id=i, path=p, width=256, height=256)

  def load_image(self, image_id):
    """Generate an image from the specs of the given image ID.
    Typically this function loads the image from a file, but
    in this case it generates the image on the fly from the
    specs in image_info.
    """
    info = self.image_info[image_id]
    image = cv2.imread(info['path'], cv2.IMREAD_UNCHANGED)
    assert(image is not None)
    assert(image.ndim == 2)
    image = np.tile(image[:,:,np.newaxis], [1,1,3])
    return image

  def image_reference(self, image_id):
    """Return the shapes data of the image."""
    info = self.image_info[image_id]
    if info["source"] == "clutter":
      return info["path"]
    else:
      super(self.__class__).image_reference(self, image_id)

  def load_mask(self, image_id):
    """Generate instance masks for shapes of the given image ID.
    """
    info = self.image_info[image_id]
    _image_id = info['id']
    Is = []
    file_name = os.path.join(self.base_path, 'occluded_segmasks_project', 
      'image_{:06d}.png'.format(_image_id))
    all_masks = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)
    
    for i in range(25):
      # file_name = os.path.join(self.base_path, 'occluded_segmasks', 
      #   'image_{:06d}_channel_{:03d}.png'.format(_image_id, i))
      # I = cv2.imread(file_name, cv2.IMREAD_UNCHANGED) > 0
      I = all_masks == i+1
      if np.any(I):
        I = I[:,:,np.newaxis]
        Is.append(I)
    if len(Is) > 0: mask = np.concatenate(Is, 2)
    else: mask = np.zeros([info['height'], info['width'], 0], dtype=np.bool)
    # Making sure masks are always contiguous.
    # block = np.any(np.any(mask,0),0)
    # assert((not np.any(block)) or (not np.any(block[np.where(block)[0][-1]+1:])))
    # print(block)
    # import pdb; pdb.set_trace()
    class_ids = np.array([1 for _ in range(mask.shape[2])])
    return mask, class_ids.astype(np.int32)

def test_clutter_dataset():
  clutter_dataset = ClutterDataset()
  clutter_dataset.load('train', 'gray')
  clutter_dataset.prepare()
  image_ids = clutter_dataset.image_ids
  for i in tqdm(image_ids):
    clutter_dataset.load_image(i)
    clutter_dataset.load_mask(i)

def concat_segmasks():
  base_dir = '../clutter_segmentation_11_07_17/'
  bads = []
  for i in tqdm(range(10000)):
    Is = []
    masks = np.zeros((256, 256), dtype=np.uint8)
    for j in range(25):
      file_name = os.path.join(base_dir, 'occluded_segmasks', 
        'image_{:06d}_channel_{:03d}.png'.format(i, j))
      I = cv2.imread(file_name, cv2.IMREAD_UNCHANGED) > 0
      masks[I] = j+1
      I = I[:,:,np.newaxis]; Is.append(I)
    Is = np.concatenate(Is, 2)
    Is = Is*1
    file_name = os.path.join(base_dir, 'occluded_segmasks_project', 
      'image_{:06d}.png'.format(i))
    cv2.imwrite(file_name, masks)
    bads.append(len(np.where(np.sum(Is,2) > 1)[0]))
  print(bads)

if __name__ == '__main__':
  test_clutter_dataset()
  # concat_segmasks()
