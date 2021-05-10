#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
# @Time    : 2021-05-10 19:33
# @Author  : Rui Zhang
# @Email   : rui27.zhang@tcl.com
# @File    : postprocess.py

import cv2

class BBox:
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
    def to_string(self):
        return "BBox:" + "\n\txmin: " + str(self.xmin) + "\t\tymin: " + str(self.ymin) + "\t\txmax: " + str(self.xmax) + "\t\tymax: " + str(self.ymax) + "\n"


def gen_search_bbox(original_bbox, x, y, scale=1.2):
    """
    Generate second time searching bbox
    Params:
        original_bbox: type BBox. the first-time output bounding box of the OCR sdk
        x: type double. the horizontal pixel of finger
        y: type double. the vertical pixel of finger

        scale: type double. to control the extension of search
    """
    height = abs(original_bbox.ymax - original_bbox.ymin)
    left = finger_pos - scale * height
    right = finger_pos + scale * height
    left = left if left > original_bbox.xmin else original_bbox.xmin
    right = right if right < original_bbox.xmax else original_bbox.xmax
    return BBox(left, original_bbox.ymin, right, original_bbox.ymax)

def get_nearest_line(response, x, y):
    res = {}
    dist = float('inf')
    for i in range(response['words_result_num']):
        words = response['words_result'][i]
        xmin_words = words['location']['left']
        ymin_words = words['location']['top']
        xmax_words = xmin_words + words['location']['width']
        ymax_words = ymin_words + words['location']['height']

        # update dist
        cur_dist = y - ymax_words if (xmin_words <= x <= xmax_words) else float('inf')

        if -0.2*words['location']['height'] < cur_dist <= dist:
            dist = cur_dist
            res = words
            res['idx'] = i
        else:
            return res 
    return res

def get_nearest_paragraph(response, x, y):
    line = get_nearest_line(response, x, y)
    idx = line['idx']
    ret = ''
    for par in response['paragraphs_result']:
        if idx in par['words_result_idx']:
            for i in par['words_result_idx']:
                ret += response['words_result'][i]['words'] + '\n'
    return ret

def match_dict(characters, language):
    if (language == 'cn'):
        match_dict_cn(characters, dictionary_cn)
    if (language == 'en'):
        match_dict_en(characters, dictionary_en)

def match_dict_cn(characters, dictionary_cn, max_len=2):
    """
    match phrases in chinese dictionary
    Params:
        character: type str. the characters to be translate
        dictionary_cn: type dict. the Chinese dictionary
        max_len: type int. the maximum length of phrase
    """
    max_len = min(max_len, len(characters))
    for i in range(max_len, 0, -1):
        # search from the longest phrases
        for j in range(len(characters) - i + 1):
            print(j, " : ", j+i)
            phrase = characters[j: j+i]
            print(phrase)
            if phrase in dictionary_cn:
                return dictionary_cn[phrase]
    return ""

def match_dict_en(characters, dictionary_en):
    idx = len(characters)/2
    return dictionary_en[characters[idx]]

def draw(response, original_img):

    for words in response['words_result']:
        # print(words['words'])
        xmin_words = words['location']['left']
        ymin_words = words['location']['top']
        xmax_words = xmin_words + words['location']['width']
        ymax_words = ymin_words + words['location']['height']
        cv2.rectangle(original_img, (xmin_words, ymin_words), (xmax_words, ymax_words), (0, 255, 0), 2)
        if 'chars' in words:
            for char in words['chars']:
                xmin_char = char['location']['left']
                ymin_char = char['location']['top']
                xmax_char = xmin_char + char['location']['width']
                ymax_char = ymin_char + char['location']['height']
                cv2.rectangle(original_img, (xmin_char, ymin_char), (xmax_char, ymax_char), (255, 0, 255), 1)



if __name__ == "__main__":
    dictionary_cn = {"最先":"1", "从头":"2", "开始":"3"}
    res = match_dict_cn("想要开始", dictionary_cn)
    a = "0123"
    print(a[0:1])