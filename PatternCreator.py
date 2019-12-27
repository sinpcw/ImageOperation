#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from PIL import Image
from absl import app, flags

""" 引数 """
flags.DEFINE_enum('pattern', 'checker', [ 'checker', 'anime-checker-x1', 'anime-checker-y1' ], '入力ディレクトリを指定します.')
flags.DEFINE_string('foreground_color', 'ffffff', '前景色を指定します.', short_name='fcolor')
flags.DEFINE_string('background_color', '000000', '背景色を指定します.', short_name='bcolor')
flags.DEFINE_string('output', 'result.png', '重複を記す出力を指定します.', short_name='o')
flags.DEFINE_integer('width', 1920, '出力サイズ(W)を指定します.', short_name='w')
flags.DEFINE_integer('height', 1080, '出力サイズ(H)を指定します.', short_name='h')
flags.DEFINE_integer('checker_grid_w', 32, '(checker) グリッドサイズ(W)を指定します.', short_name='cgw')
flags.DEFINE_integer('checker_grid_h', 32, '(checker) グリッドサイズ(H)を指定します.', short_name='cgh')
flags.DEFINE_integer('anime_frame', 32, '(anime) 生成するアニメーションフレーム数を指定します.', short_name='frame')
flags.DEFINE_integer('anime_loop', 0, '(anime) アニメーションのループ回数を指定します.', short_name='loop')
flags.DEFINE_integer('anime_duration', 10, '(anime) アニメーションの描画間隔を指定します.', short_name='duration')
flags.DEFINE_integer('anime_checker_vx', 1, '(anime-checker-x1) アニメーション速度(Vx)を指定します.', short_name='vx')
flags.DEFINE_integer('anime_checker_vy', 1, '(anime-checker-y1) アニメーション速度(Vy)を指定します.', short_name='vy')

FLAGS = flags.FLAGS

""" チェック処理 """
def CVToPIL(img):
    buf = img.copy()
    if buf.ndim == 2:
        pass
    elif buf.shape[2] == 3:
        buf = cv2.cvtColor(buf, cv2.COLOR_BGR2RGB)
    elif buf.shape[2] == 4:
        buf = cv2.cvtColor(buf, cv2.COLOR_BGRA2RGBA)
    buf = Image.fromarray(buf)
    return buf

def setLimit(lower, x, upper):
    if x < lower:
        return lower
    if x > upper:
        return upper
    return x

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
    fc = getForegroundColor()
    bc = getBackgroundColor()
    row = fc
    ret = np.zeros([h, w, 3])
    nbh = (h // FLAGS.checker_grid_h) + 1
    nbw = (w // FLAGS.checker_grid_w) + 1
    for j in range(nbh):
        col = row
        y1 = FLAGS.checker_grid_h * (j)
        y2 = FLAGS.checker_grid_h * (j+1)
        for i in range(nbw):
            x1 = FLAGS.checker_grid_w * (i)
            x2 = FLAGS.checker_grid_w * (i+1)
            ret[y1:y2, x1:x2, :] = col[:]
            col = bc if col == fc else fc
        row = bc if row == fc else fc
    return ret

def createAnimeCheckerX(w, h, frame, vx):
    fc = getForegroundColor()
    bc = getBackgroundColor()
    px = 0
    nbh = (h // FLAGS.checker_grid_h) + 1
    nbw = (w // FLAGS.checker_grid_w) + 1
    ret = []
    for _ in range(frame):
        row = fc
        buf = np.zeros([h, w, 3]).astype(np.uint8)
        cx = 0
        for j in range(nbh):
            col = row
            y1 = FLAGS.checker_grid_h * (j)
            y2 = FLAGS.checker_grid_h * (j+1)
            for i in range(-2 * cx, nbw + 2 * cx):
                x1 = FLAGS.checker_grid_w * (i)
                x2 = FLAGS.checker_grid_w * (i+1)
                ax = x1 + cx * px
                bx = x2 + cx * px
                if (0 <= ax and ax < w) or (0 <= bx and bx < w):
                    ax = setLimit(0, ax, w)
                    bx = setLimit(0, bx, w)
                    buf[y1:y2, ax:bx, :] = col[:]
                col = bc if col == fc else fc
            cx = 1 - cx
            row = bc if row == fc else fc
        ret.append(CVToPIL(buf))
        px = (px + vx) % (FLAGS.checker_grid_w * 2)
    return ret

def createAnimeCheckerY(w, h, frame, vy):
    fc = getForegroundColor()
    bc = getBackgroundColor()
    py = 0
    nbh = (h // FLAGS.checker_grid_h) + 1
    nbw = (w // FLAGS.checker_grid_w) + 1
    ret = []
    for _ in range(frame):
        col = fc
        buf = np.zeros([h, w, 3]).astype(np.uint8)
        cy = 0
        for i in range(nbw):
            row = col
            x1 = FLAGS.checker_grid_w * (i)
            x2 = FLAGS.checker_grid_w * (i+1)
            for j in range(-2 * cy, nbh + 2 * cy):
                y1 = FLAGS.checker_grid_h * (j)
                y2 = FLAGS.checker_grid_h * (j+1)
                ay = y1 + cy * py
                by = y2 + cy * py
                if (0 <= ay and ay < h) or (0 <= by and by < h):
                    ay = setLimit(0, ay, h)
                    by = setLimit(0, by, h)
                    buf[ay:by, x1:x2, :] = row[:]
                row = bc if row == fc else fc
            col = bc if col == fc else fc
            cy = 1 - cy
        ret.append(CVToPIL(buf))
        py = (py + vy) % (FLAGS.checker_grid_h * 2)
    return ret

""" 処理 """
def main(argv):
    img = None
    if FLAGS.pattern == 'checker':
        img = createChecker(FLAGS.width, FLAGS.height)
        cv2.imwrite(FLAGS.output, img)
    elif FLAGS.pattern == 'anime-checker-x1':
        img = createAnimeCheckerX(FLAGS.width, FLAGS.height, FLAGS.anime_frame, FLAGS.anime_checker_vx)
        img[0].save(FLAGS.output, save_all=True, append_images=img[1:], duration=FLAGS.anime_duration, loop=FLAGS.anime_loop)
    elif FLAGS.pattern == 'anime-checker-y1':
        img = createAnimeCheckerY(FLAGS.width, FLAGS.height, FLAGS.anime_frame, FLAGS.anime_checker_vy)
        img[0].save(FLAGS.output, save_all=True, append_images=img[1:], duration=FLAGS.anime_duration, loop=FLAGS.anime_loop)

""" エントリポイント """
if __name__ == '__main__':
    app.run(main)