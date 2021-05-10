#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
# @Time    : 2021-04-27 16:45
# @Author  : ethan_hao
# @Email   : jiangwei1.hao@tcl.com
# @File    : baidu_ocr.py
# @Software: PyCharm
# encoding:utf-8

import requests
import base64
import json
import cv2

# client_id 为官网获取的AK， client_secret 为官网获取的SK

# host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=j5YpGX4hSkwRRoYbliGvBfAR&client_secret=8AfRUtEB9ftIUY9VrDkzzMuSUXiyeaNv'
# response = requests.get(host)
# if response:
#     print(response.json())

def OpticalCharacterRecognition(img_path, precision=3):

    if precision==1:
        '''
        通用文字识别（高精度版）
        '''
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"

    elif precision==2:
        '''
        通用文字识别(高精度含位置版)
        '''
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"

    elif precision==3:
        '''
        通用文字识别(通用含位置版)
        '''
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"

    # 二进制方式打开图片文件

    f = open(img_path, 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img,
            'paragraph':'true', 
            'detect_language':'true',
            'recognize_granularity':'small'}
    # access_token = '[调用鉴权接口获取的token]'
    access_token = '24.71ccf2de9c786dfa14b52bbd0b28a141.2592000.1622108930.282335-24078056'

    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    # vertexes_location 是否返回文字外接多边形顶点位置，不支持单字位置。
    response = requests.post(request_url, data=params, headers=headers)

    return response

def draw(response, original_img):
    if response:
        print(response.json())
    dict = json.loads(response.text)
    total = int(dict['words_result_num'])
    for words in dict['words_result']:
        print(words['words'])
        xmin_words = words['location']['left']
        ymin_words = words['location']['top']
        xmax_words = xmin_words + words['location']['width']
        ymax_words = ymin_words + words['location']['height']
        cv2.rectangle(original_img, (xmin_words, ymin_words), (xmax_words, ymax_words), (0, 255, 0), 1)
        for char in words['chars']:
            xmin_char = char['location']['left']
            ymin_char = char['location']['top']
            xmax_char = xmin_words + char['location']['width']
            ymax_char = ymin_words + char['location']['height']
            cv2.rectangle(original_img, (xmin_char, ymin_char), (xmax_char, ymax_char), (0, 255, 255), 1)



if __name__ == '__main__':
    img_path = './1.jpg'
    original_img = cv2.imread(img_path)
    cv2.imshow('OCR',original_img)

    response = OpticalCharacterRecognition(img_path, 3)
    draw(response, original_img)
    cv2.imshow('OCR',original_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
