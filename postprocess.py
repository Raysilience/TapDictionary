
class BBox:
    def __init__(self, xmin=0, ymin=0, xmax=0, ymax=0):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
    def to_string(self):
        return "BBox:" + "\n\txmin: " + str(self.xmin) + "\t\tymin: " + str(self.ymin) + "\t\txmax: " + str(self.xmax) + "\t\tymax: " + str(self.ymax) + "\n"


def gen_search_bbox(original_bbox, finger_pos, scale=1.0):
    """
    Generate second time searching bbox
    Params:
        original_bbox: type BBox. the first-time output bounding box of the OCR sdk
        finger_pos: type double. the output finger positon of the finger tips recognition model
        scale: type double. to control the extension of search
    """
    height = abs(original_bbox.ymax - original_bbox.ymin)
    left = finger_pos - scale * height
    right = finger_pos + scale * height
    left = left if left > original_bbox.xmin else original_bbox.xmin
    right = right if right < original_bbox.xmax else original_bbox.xmax
    return BBox(left, original_bbox.ymin, right, original_bbox.ymax)


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

if __name__ == "__main__":
    dictionary_cn = {"最先":"1", "从头":"2", "开始":"3"}
    res = match_dict_cn("想要开始", dictionary_cn)
    a = "0123"
    print(a[0:1])