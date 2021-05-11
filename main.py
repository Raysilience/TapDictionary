#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
# @Time    : 2021-04-27 16:45
# @Author  : ethan_hao  ruizhang
# @Email   : jiangwei1.hao@tcl.com  rui27.zhang@tcl.com
# @File    : baidu_ocr.py
# @Software: PyCharm
# encoding:utf-8

import logging

from magic_finger import MagicFinger

logging.basicConfig(level=logging.INFO)
img_path = './1.jpg'

mf = MagicFinger(precision=2)
mf.set_image(img_path)
# result = mf.translate()
# print(result)
mf.draw()