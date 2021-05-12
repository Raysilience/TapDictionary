#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
# @Author  : ethan_hao  Rui
# @Email   : jiangwei1.hao@tcl.com  rui27.zhang@tcl.com
# @File    : main.py
# encoding:utf-8

import logging
from magic_finger import MagicFinger

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

img_path = './2.jpg'

mf = MagicFinger(precision=3, max_len_cn=1)
mf.set_image(img_path)

mf.draw(mode=mf.DRAWLINE|mf.INTERACTIVE)

# result = mf.translate()
# print(result)