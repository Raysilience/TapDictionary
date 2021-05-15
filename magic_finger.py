import cv2
import requests
import base64
import json
import logging
import webbrowser
from mdict_query import IndexBuilder

class BBox:
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
    def to_string(self):
        return "BBox:" + "\n\txmin: " + str(self.xmin) + "\t\tymin: " + str(self.ymin) + "\t\txmax: " + str(self.xmax) + "\t\tymax: " + str(self.ymax) + "\n"


class MagicFinger:
    def __init__(self, **kwargs):
        # 最长识别汉字词语长度
        self.MAX_LEN_CHAR_CN = 4 if 'max_len_cn' not in kwargs else kwargs['max_len_cn']
        # 搜索汉字扩框系数
        self.FACTOR_SCALE = 1.2 if 'scale' not in kwargs else kwargs['scale']
        # OCR精度设置
        self.PRECISION_STATUS = 3 if 'precision' not in kwargs else kwargs['precision']
        # OCR响应内容
        self.response = None
        # 查询图片路径
        self.image_path = ''
        # 默认查询语言
        self.lan = 'cn'

        # 汉语成语词典路径
        self.PATH_CN_PHRASE = './data/CHENGYUCIDIAN.mdx'
        # 汉语新华字典路径
        self.PATH_CN_XINHUA = './data/XINHUAZIDIAN.mdx'
        # 英-汉字典路径
        self.PATH_EN_TO_CN = './data/OALD7.mdx'
        # 指尖识别模型路径
        self.PATH_FINGERTIP_MODEL = ''
        # html显示路径
        self.PATH_HTML = 'temp.html'

        # 显示模式
        self.DRAWLINE = 1
        self.DRAWBOX = 2
        self.INTERACTIVE = 4

        self._load_local_dict()
        self._load_model()
        self._init_OCR()

    def _load_local_dict(self):
        self.dictionary_cn_XinHua = IndexBuilder(self.PATH_CN_XINHUA)
        self.dictionary_cn_phrase = IndexBuilder(self.PATH_CN_PHRASE)
        self.dictionary_en_to_cn = IndexBuilder(self.PATH_EN_TO_CN)

    def _load_model(self):
        # ToDo: 
        return

    def translate(self):
        words = self._locate_words()
        logging.debug(words)
        if not words:
            logging.error("no word detected")
            return 'NAN'

        if (self.lan == 'cn'):
            return self._match_dict_cn(words)
        elif (self.lan == 'en'):
            return self._match_dict_en(words)
        else:
            return 'Unrecognizable language'

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
        line = self._get_nearest_line()
        if not line:
            logging.error('out of bounds. retap the word')
            return ''
        xmin = line['chars'][0]['location']['left']
        xmax = line['chars'][-1]['location']['left'] + line['chars'][-1]['location']['width']
        if self.x < xmin or self.x > xmax:
            logging.error('out of bounds. retap the word')
            return ''

        # distinguish language of the interest word
        anchor_char = ''
        dist = float('inf')
        for char in line['chars']:
            xmin_char = char['location']['left']
            xmax_char = xmin_char + char['location']['width']
            xmid_char = (xmin_char + xmax_char) / 2

            cur_dist = abs(self.x - xmid_char)
            if cur_dist < dist:
                dist = cur_dist
                anchor_char = char['char']
            else:
                break
        if anchor_char >= u'\u4e00' and anchor_char<=u'\u9fa5':
            self.lan = 'cn'
        else:
            self.lan = 'en'
        
        if self.lan == 'cn':
            return self._locate_words_cn(line)
        elif self.lan == 'en':
            return self._locate_words_en(line)
        else:
            raise ValueError("not support language")

    def _locate_words_cn(self, line):
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

        ret = {}
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

    def _locate_words_en(self, line):
        words = line['words'].split()
        idx = 0
        for word in words:
            xmin = line['chars'][idx]['location']['left']
            xmax = line['chars'][idx+len(word)-1]['location']['left'] + line['chars'][idx+len(word)-1]['location']['width']
            if xmin <= self.x <= xmax:
                i = 0
                j = len(word) - 1
                for p in range(len(word)):
                    if (word[p] >= u'\u0041' and word[p]<=u'\u005a') or (word[p] >= u'\u0061' and word[p]<=u'\u007a'):
                        break
                    else:
                        i += 1
                for q in range(len(word)-1, i, -1):
                    if (word[q] >= u'\u0041' and word[q]<=u'\u005a') or (word[q] >= u'\u0061' and word[q]<=u'\u007a'):
                        break
                    else:
                        j -= 1
                return word[i: j+1]
            idx += len(word)

        return ''

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
        ret = ''
        for i in range(max_len, 0, -1):
            for phrase in comb[i]:
                ret = self.dictionary_cn_XinHua.mdx_lookup(phrase)
                if ret:
                    return ret[0]
        return "<html><head></head><body><p>{}</p></body></html>".format("查无此词")

    def _match_dict_en(self, word):
        res = self.dictionary_en_to_cn.mdx_lookup(word, True)
        if not res:
            return "Not Found"
        else:
            return res[0]



    def _init_OCR(self):
        if self.PRECISION_STATUS==1:
            '''通用文字识别（高精度版）'''
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"

        elif self.PRECISION_STATUS==2:
            '''通用文字识别(高精度含位置版)'''
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"

        elif self.PRECISION_STATUS==3:
            '''通用文字识别(通用含位置版)'''
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"

        self.params = {
                'paragraph':'true', 
                'language_type': "CHN_ENG",
                'recognize_granularity':'small'}
        # access_token = '[调用鉴权接口获取的token]'
        access_token = '24.71ccf2de9c786dfa14b52bbd0b28a141.2592000.1622108930.282335-24078056'

        self.request_url = request_url + "?access_token=" + access_token
        self.headers = {'content-type': 'application/x-www-form-urlencoded'}

    def _OCR(self):
        if not self.image_path:
            logging.error("no image to parse")
            return

        f = open(self.image_path, 'rb')
        img = base64.b64encode(f.read())
        self.params['image'] = img

        res = requests.post(self.request_url, data=self.params, headers=self.headers)
        self.response = json.loads(res.text)
        logging.debug(self.response)

        return
        
    def draw(self, mode):
        self.original_img = cv2.imread(self.image_path)
        cv2.namedWindow('Magic Finger')
        if mode & 1:
            for words in self.response['words_result']:
                xmin_words = words['location']['left']
                ymin_words = words['location']['top']
                xmax_words = xmin_words + words['location']['width']
                ymax_words = ymin_words + words['location']['height']
                cv2.rectangle(self.original_img, (xmin_words, ymin_words), (xmax_words, ymax_words), (0, 255, 0), 2)
                if (mode & 2) and ('chars' in words):
                    for char in words['chars']:
                        xmin_char = char['location']['left']
                        ymin_char = char['location']['top']
                        xmax_char = xmin_char + char['location']['width']
                        ymax_char = ymin_char + char['location']['height']
                        cv2.rectangle(self.original_img, (xmin_char, ymin_char), (xmax_char, ymax_char), (255, 0, 255), 1)
            cv2.imshow('Magic Finger', self.original_img)
            
        if mode & 4:
            cv2.setMouseCallback('Magic Finger',  self._OnMouseAction)
            while 1:
                cv2.imshow('Magic Finger', self.original_img)
                if cv2.waitKey(100) == 27:
                    break
        cv2.destroyAllWindows()

    def _display_html(self, content):
        if not content:
            return
        with open(self.PATH_HTML, 'w', encoding='utf-8') as f:
            f.write(content)
        webbrowser.open(self.PATH_HTML)

    def _OnMouseAction(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            logging.debug("x: {}\ty: {}".format(x, y))
            cv2.circle(self.original_img, (x, y), 2, (255, 0, 0), 2)
            self.x = x
            self.y = y
            res = self.translate()
            self._display_html(res)
            logging.info(res)

if __name__ == "__main__":
    mf = MagicFinger()