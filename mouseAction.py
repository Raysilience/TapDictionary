#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
# @Time    : 2021-04-27 16:45
# @Author  : ethan_hao 、Rui Zhang
# @Email   : jiangwei1.hao@tcl.com rui27.zhang@tcl.com
# @File    : baidu_ocr.py
# @Software: PyCharm
# encoding:utf-8
import numpy as np
import cv2 #freetype

global a, b
#创建回调函数
def OnMouseAction(event,x,y,flags,param):

    img = img1

    if event == cv2.EVENT_LBUTTONDOWN:
        print("左键点击")
        print(x,y)
        a,b= x,y
        cv2.circle(img,(x,y),2,(255,255,0),2)
        return a,b



img_path = '/Users/jiangweihao/Desktop/a/902.jpg'
img1 = cv2.imread(img_path)
cv2.namedWindow('image1')

cv2.setMouseCallback('image1',OnMouseAction)
while(1):
    cv2.imshow('image1',img1)
    k=cv2.waitKey(1)
cv2.destroyAllWindows()


