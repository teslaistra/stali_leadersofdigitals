import cv2

import numpy as np
import torch
import torchvision
from torchvision import transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

from PIL import Image
from matplotlib import pyplot as plt

global model
model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True, progress=False)
model.eval()


def get_predictions(im):
    print(2)
    photo = transforms.ToTensor()(im).unsqueeze_(0)
    print(3)
    result = model(photo)[0]
    print(4)
    boxes = result['boxes']
    pret = []
    avg = 0
    for i in range(len(boxes)):
        if result['labels'][i] == 3 and result['scores'][i] > 0:
            x1, y1, x2, y2 = int(boxes[i][0]), int(boxes[i][1]), int(boxes[i][2]), int(boxes[i][3])
            pret.append((x1, y1, x2, y2))
            avg += abs((x2 - x1) * (y2 - y1))
    avg /= len(boxes)

    boxed = im
    taken = []
    for i in range(len(pret)):
        x1, y1, x2, y2 = pret[i]
        space = abs((x2 - x1) * (y2 - y1))
        if space < avg * 1.5 and space > avg / 1.5:
            boxed = cv2.rectangle(np.asarray(boxed), (x1, y1), (x2, y2), (0, 255, 0), 2)
            taken.append((x1, y1, x2, y2))
    return boxed, taken


def get_busy(img, coors):
    print(1)
    boxed, taken = (get_predictions(img))
    print(2)
    busy = []
    for t in taken:
        c = ((t[0] + t[2]) / 2, (t[1] + t[3]) / 2)
        dist = min([abs(c[0] - t[0]), abs(c[1] - t[1]), abs(c[0] - t[2]), abs(c[1] - t[3])]) * 8
        for key in coors.keys():
            x, y = coors[key]
            if (x - c[0]) ** 2 + (y - c[1]) ** 2 < dist:
                busy.append(key)
    return list(set(busy))


def detect_parking(image_path, inputs):

    print("done model")

    im = Image.open(image_path)
    print("image opened")

    return get_busy(im, inputs)
