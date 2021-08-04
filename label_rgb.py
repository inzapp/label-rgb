import os
import sys
from glob import glob

import cv2
import numpy as np

g_max_num_circles = 2
g_win_size = (768, 768)
g_win_name = 'Label RGB v2.0 by Inzapp'


def get_next_circle_index():
    global g_max_num_circles, g_circle_index
    g_circle_index += 1
    if g_circle_index == g_max_num_circles:
        g_circle_index = 0
    return g_circle_index


def is_cursor_in_image(x):
    global g_win_size
    return x < g_win_size[0]


def is_cursor_in_circle(cur_x, cur_y):
    global g_side_pan_circle_positions
    for x1, y1, x2, y2 in g_side_pan_circle_positions:
        if x1 <= cur_x <= x2 and y1 <= cur_y <= y2:
            return True
    return False


def show_cursor_color(cur_x, cur_y):
    global g_win_size
    radius = int(min(g_win_size[0], g_win_size[1]) * 0.125)
    raw_height, raw_width = g_view.shape[0], g_view.shape[1]
    bgr = g_view[cur_y][cur_x]
    x = cur_x + radius
    y = cur_y - radius
    if cur_x > raw_width - radius:
        x = cur_x - radius
    if cur_y < radius:
        y = cur_y + radius
    g_view_copy = g_view.copy()
    g_view_copy = cv2.circle(g_view_copy, (x, y), radius, (int(bgr[0]), int(bgr[1]), int(bgr[2])), thickness=-1)
    cv2.imshow(g_win_name, g_view_copy)


def set_circle_to_side_pan_and_save_label(cur_x, cur_y):
    global g_view
    bgr = g_view[cur_y][cur_x] / 255.0
    rgb = [bgr[2], bgr[1], bgr[0]]
    circle_index = get_next_circle_index()
    g_view = set_circle_to_side_pan(g_view, rgb, circle_index)
    save_label(g_label_path, rgb, circle_index)
    cv2.imshow(g_win_name, g_view)


def get_circle_index_at_cursor(cur_x, cur_y):
    global g_side_pan_circle_positions
    for circle_index, p in enumerate(g_side_pan_circle_positions):
        x1, y1, x2, y2 = p
        if x1 <= cur_x <= x2 and y1 <= cur_y <= y2:
            return circle_index
    return -1


def hover(circle_index):
    global g_side_pan_circle_positions
    x1, y1, x2, y2 = g_side_pan_circle_positions[circle_index]
    g_view_copy = g_view.copy()
    cv2.rectangle(g_view_copy, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
    cv2.imshow(g_win_name, g_view_copy)


def cover(view, default_image, position):
    x1, y1, x2, y2 = position
    for y in range(y1, y2):
        for x in range(x1, x2):
            view[y][x] = default_image[y - y1][x - x1]
    return view


def remove_circle_if_exist(circle_index):
    global g_side_pan_circle_positions, g_raw, g_view, g_circle_index, g_win_name
    circle_position = g_side_pan_circle_positions[circle_index]
    x1, y1, x2, y2 = circle_position
    default_image = g_raw[y1:y2, x1:x2]
    g_view = cover(g_view, default_image, circle_position)
    g_circle_index = circle_index - 1
    cv2.imshow(g_win_name, g_view)


def mouse_callback(event, cur_x, cur_y, flag, _):
    global g_view

    # no click mouse moving
    if event == 0 and flag == 0:
        if is_cursor_in_image(cur_x):
            show_cursor_color(cur_x, cur_y)
        elif is_cursor_in_circle(cur_x, cur_y):
            circle_index_at_cursor = get_circle_index_at_cursor(cur_x, cur_y)
            hover(circle_index_at_cursor)
        else:
            cv2.imshow(g_win_name, g_view)

    # end left click
    elif event == 4 and flag == 0:
        if is_cursor_in_image(cur_x):
            set_circle_to_side_pan_and_save_label(cur_x, cur_y)

    # right click
    elif event == 5 and flag == 0:
        if is_cursor_in_circle(cur_x, cur_y):
            circle_index_at_cursor = get_circle_index_at_cursor(cur_x, cur_y)
            remove_circle_if_exist(circle_index_at_cursor)


def side_pan():
    pan = [[84, 168],
           [168, 84]]

    pan = np.concatenate((pan, pan), axis=1)
    pan = np.concatenate((pan, pan), axis=1)

    pan = np.concatenate((pan, pan), axis=0)
    pan = np.concatenate((pan, pan), axis=0)
    pan = np.concatenate((pan, pan), axis=0)
    pan = np.concatenate((pan, pan), axis=0)

    pan = np.asarray(pan).astype('uint8')
    pan = cv2.resize(pan, (int(g_win_size[0] / 5), g_win_size[1]), interpolation=cv2.INTER_NEAREST)
    pan = cv2.cvtColor(pan, cv2.COLOR_GRAY2BGR)
    return pan


def save_label(label_path, rgb, circle_index):
    # confidence, r, g, b = rgb
    r, g, b = rgb
    label_str = f'{r:.6f} {g:.6f} {b:.6f}\n'
    if not (os.path.exists(label_path) and os.path.isfile(label_path)):
        with open(label_path, 'wt') as f:
            f.writelines(label_str)
        return

    with open(label_path, 'rt') as f:
        lines = f.readlines()

    if circle_index < len(lines):
        lines[circle_index] = label_str
    else:
        lines.append(label_str)

    with open(label_path, 'wt') as f:
        f.writelines(lines)


def set_circle_to_side_pan(img, rgb, circle_index):
    global g_label_path
    r, g, b = rgb
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    if circle_index == 0:
        circle_cy = int(g_win_size[1] * 0.2)
        img = cv2.circle(img, (g_side_pan_circle_cx, circle_cy), g_side_pan_circle_radius, (b, g, r), thickness=-1)

    if circle_index == 1:
        circle_cy = int(g_win_size[1] * 0.8)
        img = cv2.circle(img, (g_side_pan_circle_cx, circle_cy), g_side_pan_circle_radius, (b, g, r), thickness=-1)
    return img


def load_saved_rgbs_if_exist(label_path):
    rgbs = list()
    if os.path.exists(label_path) and os.path.isfile(label_path):
        with open(label_path, 'rt') as f:
            lines = f.readlines()
        for line in lines:
            r, g, b = list(map(float, line.replace('\n', '').split()))
            rgbs.append([r, g, b])
        return rgbs
    else:
        return None


def get_g_side_pan_circle_positions():
    global g_max_num_circles, g_side_pan_circle_radius
    cys = []
    if g_max_num_circles == 1:
        cys = [0.5]
    elif g_max_num_circles == 2:
        cys = [0.2, 0.8]
    else:
        print('not implemented : g_max_num_circles > 2')
        exit(0)
    cys = np.asarray(cys) * g_win_size[1]

    cx = g_side_pan_circle_cx
    cys = cys.astype('int32')

    positions = []
    for cy in cys:
        x1 = int(cx - g_side_pan_circle_radius)
        y1 = int(cy - g_side_pan_circle_radius)
        x2 = int(cx + g_side_pan_circle_radius)
        y2 = int(cy + g_side_pan_circle_radius)
        positions.append([x1, y1, x2, y2])
    return positions


path = ''
if len(sys.argv) > 1:
    path = sys.argv[1].replace('\\', '/') + '/'

jpg_file_paths = glob(f'{path}*.jpg')
png_file_paths = glob(f'{path}*.png')
img_paths = jpg_file_paths + png_file_paths
if len(img_paths) == 0:
    print('No image files in path. run label.py with path argument')
    exit(0)

g_side_pan = side_pan()
g_side_pan_width = g_side_pan.shape[1]
g_side_pan_height = g_side_pan.shape[0]
g_side_pan_circle_radius = int(g_side_pan_width / 2)
g_side_pan_circle_cx = g_win_size[0] + int((g_win_size[0] / 5) / 2)
g_side_pan_circle_positions = get_g_side_pan_circle_positions()

index = 0
while True:
    g_circle_index = -1
    file_path = img_paths[index]
    g_label_path = f'{file_path[:-4]}.txt'
    g_raw = cv2.imread(file_path, cv2.IMREAD_COLOR)
    g_raw = cv2.resize(g_raw, g_win_size)
    g_raw = np.concatenate((g_raw, g_side_pan), axis=1)
    g_view = g_raw.copy()
    g_rgbs = load_saved_rgbs_if_exist(g_label_path)
    if g_rgbs is not None:
        for i in range(len(g_rgbs)):
            g_view = set_circle_to_side_pan(g_view, g_rgbs[i], i)
    cv2.namedWindow(g_win_name)
    cv2.imshow(g_win_name, g_view)
    cv2.setMouseCallback(g_win_name, mouse_callback)

    while True:
        res = cv2.waitKey(0)

        # go to next if input key was 'd'
        if res == ord('d'):
            if index == len(img_paths) - 1:
                print('Current image is last image')
            else:
                index += 1
                break

        # go to previous image if input key was 'a'
        elif res == ord('a'):
            if index == 0:
                print('Current image is first image')
            else:
                index -= 1
                break

        # exit if input key was ESC
        elif res == 27:
            exit(0)
