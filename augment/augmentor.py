"""Provides data augmentation"""
import numpy as np

from .blur import blur_augment
from .box import box_augment
from .circle import circle_augment
from .elastic_warp import elastic_warp_augment
from .flip import flip_augment
from .grey import grey_augment
from .misalign import misalign_augment
from .missing_section import missing_section_augment
from .noise import noise_augment
from .rotate import rotate_augment
from .rotate90 import rotate90_augment
from .rescale import rescale_augment
from .sin import sin_augment

class Augmentor:
  def __init__(self, params):
    self.params = params
    self._init_params()

  def _init_params(self):
    augs = ['blur', 'box', 'circle', 'elastic_warp', 'flip', 'grey',
            'misalign', 'missing_section', 'noise', 'rotate', 'rotate90',
            'rescale', 'sin']
    for aug in augs:
      if aug not in self.params.keys():
        self.params[aug] = False

  def __call__(self, img, labels=[]):
    return self.augment(img, labels)

  def augment(self, img, labels=[]):
    """Augments example.

    Args:
      img: (np array: <z,y,x,ch>) image
      labels: list of (int np array: <z,y,x,ch>), pixelwise labeling of image
      params: dict containing augmentation parameters, see code for details

    Returns:
      augmented img: image after augmentation
      augmented labels: labels after augmentation

    Note:
      augmented img,labels may not be same size as input img,labels
        because of warping
    """
    params = self.params
    img = np.copy(img)
    labels = [np.copy(l) for l in labels]

    # Elastic warp
    if params['elastic_warp']:
      n = params['elastic_n']
      max_sigma = params['elastic_sigma']

      img, labels = elastic_warp_augment(img, labels, n, max_sigma)

    # Flip
    if params['flip']:
      img, labels = flip_augment(img, labels)

    # Rotate
    if params['rotate']:
      img, labels = rotate_augment(img, labels)

    if params['rotate90']:
      img, labels = rotate90_augment(img, labels)

    # Blur
    if params['blur']:
      sigma = params['blur_sigma']
      prob = params['blur_prob']
      img = blur_augment(img, sigma, prob)

    # Misalign
    if params['misalign']:
      p = params['misalign_prob']
      delta = params['misalign_delta']
      type = params['misalign_type']
      shift_labels = params['misalign_label_shift']
      img, labels = misalign_augment(img, labels, p, delta, type, shift_labels)

    # Missing Section
    if params['missing_section']:
      p = params['missing_section_prob']
      img = missing_section_augment(img, p)

    # Rescale
    if params['rescale']:
      min_f = params['rescale_min']
      max_f = params['rescale_max']
      img, labels = rescale_augment(img, labels, min_f, max_f)

    # Circle
    if params['circle']:
      p = params['circle_prob']
      r = params['circle_radius']
      img = circle_augment(img, p, r)

    if params['grey']:
      raise NotImplementedError

    if params['noise']:
      sigma = params['noise_sigma']
      img = noise_augment(img, sigma)

    if params['sin']:
      a = params['sin_a']
      f = params['sin_f']
      img = sin_augment(img, a, f)

    if params['box']:
      n = params['box_n']
      r = params['box_r']
      z = params['box_z']
      fill = params['box_fill']
      img = box_augment(img, n, r, z, fill)

    img = np.copy(img).astype(np.float32)
    labels = [np.copy(l) for l in labels]

    # Return
    if labels == []:
      return img
    else:
      return img, labels