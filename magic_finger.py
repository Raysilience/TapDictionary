#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
# @Time    : 2021-05-10 19:33
# @Author  : rui
# @Email   : rui27.zhang@tcl.com
# @File    : postprocess.py

import cv2
import requests
import base64
import json
import logging

class BBox:
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
    def to_string(self):
        return "BBox:" + "\n\txmin: " + str(self.xmin) + "\t\tymin: " + str(self.ymin) + "\t\txmax: " + str(self.xmax) + "\t\tymax: " + str(self.ymax) + "\n"


class MagicFinger:
    def __init__(self, precision=3, max_len=4, scale=1.2):
        # 最长识别汉字词语长度
        self.MAX_LEN_CHAR_CN = max_len
        # 搜索汉字扩框系数
        self.FACTOR_SCALE = scale
        # OCR精度设置
        self.PRECISION_STATUS = precision
        # OCR响应内容
        self.response = None
        # 查询图片路径
        self.image_path = ''

        # 汉语词语字典路径
        self.PATH_CN_PHRASE = ''
        # 英-汉字典路径
        self.PATH_EN_TO_CN = ''
        # 指尖识别模型路径
        self.PATH_FINGERTIP_MODEL = ''

        self._load_local_dict()
        self._load_model()

    def _load_local_dict(self):
        # ToDo: 
        self.dictionary_cn = {"实现":"shixian"}
        self.dictionary_en_to_cn = None
        return

    def _load_model(self):
        # ToDo: 
        return

    def set_image(self, path):
        """ set data then send it to ocr and fingertip regressor"""
        self.image_path = path
        self._OCR()
        self._fingertip_regress()

    def _fingertip_regress(self):
        if not self.image_path:
            logging.error("no image to parse")
            return

        # ToDo: get x, y from model

        self.x = 241
        self.y = 129

    def _locate_words(self):
        """
        find tentative consecutive words 
        Params:
            self.response: type dict. the output json of the OCR sdk
            x: type double. the horizontal pixel of finger
            y: type double. the vertical pixel of finger

            scale: type double. to control the extension of search
        Returns:
            a dictionary whose key is length of potential words and value is list of words of that length
        """
        ret = {}
        line = self._get_nearest_line()

        # Generate second time searching bbox according to bbox height
        xmin_line = line['location']['left']
        ymin_line = line['location']['top']
        xmax_line = xmin_line + line['location']['width']
        ymax_line = ymin_line + line['location']['height']
        height = abs(ymax_line - ymin_line)
        left = self.x - self.FACTOR_SCALE * height
        right = self.x + self.FACTOR_SCALE * height
        left = left if left > xmin_line else xmin_line
        right = right if right < xmax_line else xmax_line

        # todo: distinguish ch and en
        # get tentative characters 
        chars = []
        anchor_char = ''
        idx = -1
        dist = float('inf')
        for char in line['chars']:
            xmin_char = char['location']['left']
            xmax_char = xmin_char + char['location']['width']
            xmid_char = (xmin_char + xmax_char) / 2
            if left < xmid_char < right:
                chars.append(char['char'])
                cur_dist = abs(self.x - xmid_char)
                if cur_dist < dist:
                    dist = cur_dist
                    anchor_char = char['char']
                    idx += 1
            elif xmid_char > right:
                break
            else:
                continue

        # print("tentative characters: ", chars)
        # print("anchor_char: ", anchor_char)
        # print("idx: ", idx)

        # combination of phrases
        if chars:
            for i in range(idx + 1):
                for j in range(idx + 1, len(chars) + 1):
                    phrase = ''.join(chars[i: j])
                    if len(phrase) not in ret:
                        ret[len(phrase)] = [phrase]
                    else:
                        ret[len(phrase)].append(phrase)

        return ret

    def _get_nearest_line(self):
        if not self.response:
            logging.error("no response to parse, try to set image")
            return

        res = {}
        dist = float('inf')
        for i in range(self.response['words_result_num']):
            words = self.response['words_result'][i]
            xmin_words = words['location']['left']
            ymin_words = words['location']['top']
            xmax_words = xmin_words + words['location']['width']
            ymax_words = ymin_words + words['location']['height']

            # update dist
            cur_dist = self.y - ymax_words if (xmin_words <= self.x <= xmax_words) else float('inf')

            if -0.2*words['location']['height'] < cur_dist <= dist:
                dist = cur_dist
                res = words
                res['idx'] = i
            elif cur_dist == float('inf'):
                continue
            else:
                return res 
        return res

    def get_nearest_paragraph(self):
        line = self._get_nearest_line()
        ret = ''
        if not line:
            return ret

        idx = line['idx']
        for par in self.response['paragraphs_result']:
            if idx in par['words_result_idx']:
                for i in par['words_result_idx']:
                    ret += self.response['words_result'][i]['words'] + '\n'
        return ret

    def _match_dict_cn(self, comb):
        """
        match phrases in Chinese phrase dictionary
        Params:
            comb: type dict. whose key is length of potential words and value is list of words of that length
        """
        keys = list(comb.keys())
        keys.sort(reverse = True)
        max_len = min(self.MAX_LEN_CHAR_CN, keys[0])
        for i in range(max_len, 0, -1):
            for phrase in comb[i]:
                if phrase in self.dictionary_cn:
                    return self.dictionary_cn[phrase]
        return "查无此词"

    def _match_dict_en(self, word):
        if word in self.dictionary_en_to_cn:
            return self.dictionary_en_to_cn[word]
        else:
            return "Not Found"

    def translate(self):
        comb = self._locate_words()
        logging.debug(comb)
        lan = 'cn'
        if (lan == 'cn'):
            return self._match_dict_cn(comb)
        elif (lan == 'en'):
            return self._match_dict_en_to_cn(comb)
        else:
            return 'Unrecognizable language'

    def _OCR(self):
        if not self.image_path:
            logging.error("no image to parse")
            return

        if self.PRECISION_STATUS==1:
            '''通用文字识别（高精度版）'''
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"

        elif self.PRECISION_STATUS==2:
            '''通用文字识别(高精度含位置版)'''
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"

        elif self.PRECISION_STATUS==3:
            '''通用文字识别(通用含位置版)'''
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"

        # 二进制方式打开图片文件
        f = open(self.image_path, 'rb')
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
        res = requests.post(request_url, data=params, headers=headers)
        self.response = json.loads(res.text)
        logging.info(self.response)

        return
        
    def draw(self):
        self.original_img = cv2.imread(self.image_path)
        cv2.namedWindow('Magic Finger')
        for words in self.response['words_result']:
            # print(words['words'])
            xmin_words = words['location']['left']
            ymin_words = words['location']['top']
            xmax_words = xmin_words + words['location']['width']
            ymax_words = ymin_words + words['location']['height']
            cv2.rectangle(self.original_img, (xmin_words, ymin_words), (xmax_words, ymax_words), (0, 255, 0), 2)
            if 'chars' in words:
                for char in words['chars']:
                    xmin_char = char['location']['left']
                    ymin_char = char['location']['top']
                    xmax_char = xmin_char + char['location']['width']
                    ymax_char = ymin_char + char['location']['height']
                    cv2.rectangle(self.original_img, (xmin_char, ymin_char), (xmax_char, ymax_char), (255, 0, 255), 1)

        cv2.circle(self.original_img, (self.x, self.y), 2, (255, 0, 0), 2)
        cv2.setMouseCallback('Magic Finger',  self._OnMouseAction)

        while 1:
            cv2.imshow('Magic Finger', self.original_img)
            if cv2.waitKey(100) == 27:
                break
        cv2.destroyAllWindows()

    def _OnMouseAction(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(x,y)
            cv2.circle(self.original_img, (x, y), 2, (255, 0, 0), 2)
            self.x = x
            self.y = y
            print(self.translate())

if __name__ == "__main__":
    mf = MagicFinger()