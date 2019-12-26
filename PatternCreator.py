#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from absl import app, flags

""" 引数 """
flags.DEFINE_enum('input_pattern', 'checker', [ 'checker' ], '入力ディレクトリを指定します.')
flags.DEFINE_string('foreground_color', 'ffffff', '前景色を指定します.', short_name='fcolor')
flags.DEFINE_string('background_color', '000000', '背景色を指定します.', short_name='bcolor')
flags.DEFINE_string('output', 'result.png', '重複を記す出力を指定します.', short_name='o')
flags.DEFINE_integer('width', 1920, '出力サイズ(W)を指定します.', short_name='w')
flags.DEFINE_integer('height', 1080, '出力サイズ(H)を指定します.', short_name='h')
flags.DEFINE_integer('checker_grid_w', 32, '(checkerのみ) グリッドサイズ(W)を指定します.', short_name='cgw')
flags.DEFINE_integer('checker_grid_h', 32, '(checkerのみ) グリッドサイズ(H)を指定します.', short_name='cgh')

FLAGS = flags.FLAGS

""" チェック処理 """
def getForegroundColor():
    fcr = int(FLAGS.foreground_color[0:2], 16) if len(FLAGS.foreground_color) >= 2 else 255
    fcg = int(FLAGS.foreground_color[2:4], 16) if len(FLAGS.foreground_color) >= 4 else 255
    fcb = int(FLAGS.foreground_color[4:6], 16) if len(FLAGS.foreground_color) >= 6 else 255
    return fcb, fcg, fcr

def getBackgroundColor():
    bcr = int(FLAGS.background_color[0:2], 16) if len(FLAGS.background_color) >= 2 else 0
    bcg = int(FLAGS.background_color[2:4], 16) if len(FLAGS.background_color) >= 4 else 0
    bcb = int(FLAGS.background_color[4:6], 16) if len(FLAGS.background_color) >= 6 else 0
    return bcb, bcg, bcr

def createChecker(w, h):
    ret = np.zeros([h, w, 3])
    nbh = (h // FLAGS.checker_grid_h) + 1
    nbw = (w // FLAGS.checker_grid_w) + 1
    fc = getForegroundColor()
    bc = getBackgroundColor()
    row = fc
    for j in range(nbh):
        col = row
        for i in range(nbw):
            y1 = FLAGS.checker_grid_h * (j)
            y2 = FLAGS.checker_grid_h * (j+1)
            x1 = FLAGS.checker_grid_w * (i)
            x2 = FLAGS.checker_grid_w * (i+1)
            ret[y1:y2, x1:x2, :] = col[:]
            col = bc if col == fc else fc
        row = bc if row == fc else fc
    return ret

""" 処理 """
def main(argv):
    img = None
    if FLAGS.input_pattern == 'checker':
        img = createChecker(FLAGS.width, FLAGS.height)
    if img is not None:
        cv2.imwrite(FLAGS.output, img)

""" エントリポイント """
if __name__ == '__main__':
    app.run(main)