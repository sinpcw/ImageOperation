#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import glob
import hashlib
from absl import app, flags

""" 引数 """
flags.DEFINE_string('input_dir', None, '入力ディレクトリを指定します.', short_name='i')
flags.DEFINE_string('input_fmt', '.png', '入力拡張子を指定します.', short_name='ifmt')
flags.DEFINE_string('output', 'result.txt', '重複を記す出力を指定します.', short_name='o')

FLAGS = flags.FLAGS

""" チェック処理 """
def GetMD5(src):
    md5 = hashlib.md5()
    with open(src, mode='rb') as f:
        while True:
            read = f.read(8096)
            if not read:
                break
            md5.update(read)
        hash = md5.hexdigest()
    return hash

""" 処理 """
def main(argv):
    inputs = glob.glob(os.path.join(FLAGS.input_dir, '**/*' + FLAGS.input_fmt), recursive=True)
    hash = [ GetMD5(x) for x in inputs ]
    nlen = len(hash)
    with open(FLAGS.output, mode='w') as f:
        for i in range(nlen):
            for j in range(i + 1, nlen):
                if hash[i] == hash[j]:
                    f.write('{},{}\n'.format(inputs[i], inputs[j]))

""" エントリポイント """
if __name__ == '__main__':
    app.run(main)