import os.path as op
import re
from typing import Union, List, AnyStr

# import cv2 as cv
import numpy as np
# import pytesseract as tes
#
# tes.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract"
# TEMPLATE_TOP_PATH = op.join(op.dirname(__file__), "template/top.png")
# TEMPLATE_BOTTOM_PATH = op.join(op.dirname(__file__), "template/bottom.png")


def _match_template(img, template_path: str):
    img_internal = img.copy()
    template = cv.imread(template_path, 0)
    w, h = template.shape[::-1]
    res = cv.matchTemplate(img_internal, template, cv.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    top_left = min_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return top_left[0], bottom_right[0], top_left[1], bottom_right[1]


def crop_item_window_coords(img_path: str):
    img = cv.imread(img_path, cv.IMREAD_COLOR)
    img_gray = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
    img_cp = img.copy()
    coord_top = _match_template(img_gray, TEMPLATE_TOP_PATH)
    coords_bottom = _match_template(img_gray, TEMPLATE_BOTTOM_PATH)
    img_cp = img_cp[coord_top[2]:coords_bottom[3], coord_top[0]:coords_bottom[1]]
    return img_cp


def enhance_image_readability(img):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    ret, img = cv.threshold(img, 50, 255, cv.THRESH_BINARY_INV)
    im = cv.filter2D(img, -1, kernel)
    return im


class Item(object):
    def __init__(self, name, level, mythic_boost, img):
        self.name = name.rstrip()
        self.level = level
        self.mythic_boost = mythic_boost
        self.img = img

    def __repr__(self):
        return f"name: {self.name},\nmythic: {self.mythic_boost}"


def _validator(match: re.match, group: int, on_fail=None):
    return match.group(group) if match is not None else on_fail


def analyze(pic: Union[List, AnyStr]):
    def analyze_internal(pic):
        window_img = crop_item_window_coords(pic)
        # window_img = enhance_image_readability(window_img)
        item_str = tes.image_to_string(window_img)
        if item_str is not None:
            item_str = item_str.strip()

        name = _validator(re.match(".*\n", item_str), 0, "")
        level = _validator(re.search(".*Level:\s+(\d+).*", item_str), 1, 0)
        mythic = _validator(re.search(".*Mythic.*\+(\d+)", item_str), 1, 0)
        return Item(name=name, level=level, mythic_boost=mythic, img=window_img)

    if isinstance(pic, str):
        return analyze_internal(pic=pic)

    for p in pic:
        yield analyze_internal(p)

# if __name__ == '__main__':
# window_img = crop_item_window_coords("test_pics/test_mythic.png")
# window_img = enhance_image_readability(window_img)
# # item_str = tes.image_to_string(window_img).rstrip().strip()
# name = _validator(re.match(".*\n", item_str), 0)
# level = _validator(re.search(".*Level:\s+(\d+).*", item_str), 1)
# mythic = _validator(re.search(".*Mythic.*\+(\d+)", item_str), 1)
# it = Item(name=name, level=level, mythic_boost=mythic, img=window_img)
