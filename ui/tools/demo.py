#!/usr/bin/env python

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths
import os.path as osp
from model.config import cfg
from model.test import im_detect
from model.nms_wrapper import nms

from utils.timer import Timer
import tensorflow as tf
import numpy as np
import os, cv2
import argparse

from nets.vgg16 import vgg16
from nets.resnet_v1 import resnetv1

CLASSES = ('__background__',
           'mbeer', 'mdorig', 'rsugar', 'zero')

NETS = {'vgg16': ('vgg16_faster_rcnn_iter_10000.ckpt',),'res101': ('res101_faster_rcnn_iter_10000.ckpt',)}
DATASETS= {'pascal_voc': ('voc_2007_trainval',), 'pascal_voch': ('voc_2017h_train',),'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}


cfg.TEST.HAS_RPN = True  # Use RPN for proposals
# model path
demonet = 'vgg16'
dataset = 'pascal_voch'
tfmodel = os.path.join(osp.dirname(__file__), 'output', demonet, DATASETS[dataset][0], 'default',
                          NETS[demonet][0])


if not os.path.isfile(tfmodel + '.meta'):
    raise IOError(('{:s} not found.\nDid you download the proper networks from '
                   'our server and place them properly?').format(tfmodel + '.meta'))

# set config
tfconfig = tf.ConfigProto(allow_soft_placement=True)
tfconfig.gpu_options.allow_growth=True

# init session
sess = tf.Session(config=tfconfig)
# load network
if demonet == 'vgg16':
    net = vgg16()
elif demonet == 'res101':
    net = resnetv1(num_layers=101)
else:
    raise NotImplementedError
net.create_architecture("TEST", 5,
                      tag='default', anchor_scales=[8, 16, 32])
saver = tf.train.Saver()
saver.restore(sess, tfmodel)

print('Loaded network {:s}'.format(tfmodel))

myImage=None

def vis_detections(im, class_name, dets, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    global myImage
    im = im[:, :, (2, 1, 0)]
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        cv2.rectangle(myImage,(bbox[0], bbox[1]),
                          (bbox[0]+(bbox[2] - bbox[0]),bbox[1]+(bbox[3] - bbox[1])),
                          (255,0,0), 3)
        
        cv2.putText(myImage, '{:s} {:.3f}'.format(class_name, score), (int(bbox[0]), int(bbox[1]) - 2), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0,  0, 255), 1, cv2.LINE_AA)



def demo(im):
    """Detect object classes in an image using pre-computed object proposals."""
    global sess
    global net

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

    # Visualize detections for each class
    CONF_THRESH = 0.8
    NMS_THRESH = 0.3
    
    global myImage
    myImage = im
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        vis_detections(im, cls, dets, thresh=CONF_THRESH)
    return myImage

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='vgg16')
    parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc_0712]',
                        choices=DATASETS.keys(), default='pascal_voch')
    args = parser.parse_args()

    return args
