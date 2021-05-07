import os
import sys
from glob import glob

import cv2
import numpy as np

win_name = 'Label RGB v1.0 by Inzapp'


def mouse_callback(event, cur_x, cur_y, flag, _):
    # no click mouse moving
    if event == 0 and flag == 0:
        radius = 100
        raw_copy = raw.copy()
        raw_height, raw_width = raw.shape[0], raw.shape[1]
        bgr = raw[cur_y][cur_x]
        x = cur_x + radius
        y = cur_y - radius
        if cur_x > raw_width - radius:
            x = cur_x - radius
        if cur_y < radius:
            y = cur_y + radius
        raw_copy = cv2.circle(raw_copy, (x, y), radius, (int(bgr[0]), int(bgr[1]), int(bgr[2])), thickness=-1)
        cv2.imshow(win_name, raw_copy)

    # end click
    elif event == 4 and flag == 0:
        bgr = raw[cur_y][cur_x] / 255.0
        with open(label_path, 'wt') as label_file:
            label_file.writelines(f'{bgr[2]:6f} {bgr[1]:6f} {bgr[0]:6f}\n')


path = ''
if len(sys.argv) > 1:
    path = sys.argv[1].replace('\\', '/') + '/'

jpg_file_paths = glob(f'{path}*.jpg')
png_file_paths = glob(f'{path}*.png')
img_paths = jpg_file_paths + png_file_paths
if len(img_paths) == 0:
    print('No image files in path. run label.py with path argument')
    sys.exit(0)

index = 0
while True:
    file_path = img_paths[index]
    label_path = f'{file_path[:-4]}.txt'
    if os.path.exists(label_path) and os.path.isfile(label_path):
        with open(label_path, 'rt') as f:
            line = f.readline()
        r, g, b = list(map(float, line.split(' ')))

        # get rgb image
        print('loaded')
        print(r, g, b)
        print()

    raw = cv2.imread(file_path, cv2.IMREAD_COLOR)
    raw = cv2.resize(raw, (768, 768))
    cv2.namedWindow(win_name)
    cv2.setMouseCallback(win_name, mouse_callback)
    cv2.imshow(win_name, raw.copy())
    res = cv2.waitKey(0)

    # go to next if input key was 'd'
    if res == ord('d'):
        if index == len(img_paths) - 1:
            print('Current image is last image')
        else:
            index += 1

    # go to previous image if input key was 'a'
    elif res == ord('a'):
        if index == 0:
            print('Current image is first image')
        else:
            index -= 1

    # exit if input key was ESC
    elif res == 27:
        sys.exit()
