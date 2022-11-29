from typing import List, Optional, Dict
from dataclasses import dataclass
import enum
import cv2


CvColorConversionCode = int


class ColorType(enum.Enum):
    BGR = enum.auto()
    RGB = enum.auto()
    HSV = enum.auto()
    HLS = enum.auto()
    Lab = enum.auto()
    Luv = enum.auto()
    XYZ = enum.auto()

    def channels_names(self) -> List[str]:
        return list(self.name)

    def channel_name(self, i: int) -> str:
        names = self.channels_names()
        assert 0 <= i < len(names)
        return names[i]


@dataclass
class ColorConversion:
    name: str
    src_color: ColorType
    dst_color: ColorType
    conversion_code: CvColorConversionCode


@dataclass
class ColorConversionPair:
    """Two inverse color conversions"""

    name: str
    conversion: ColorConversion
    inv_conversion: ColorConversion


def cv_color_conversion_code_between(type1: ColorType, type2: ColorType) -> Optional[CvColorConversionCode]:
    def handle_bgr() -> Optional[CvColorConversionCode]:
        if type1 == ColorType.BGR:
            conversions: Dict[ColorType, CvColorConversionCode] = {
                ColorType.RGB: cv2.COLOR_BGR2RGB,
                ColorType.HSV: cv2.COLOR_BGR2HSV_FULL,
                ColorType.HLS: cv2.COLOR_BGR2HLS_FULL,
                ColorType.Lab: cv2.COLOR_BGR2Lab,
                ColorType.Luv: cv2.COLOR_BGR2Luv,
                ColorType.XYZ: cv2.COLOR_BGR2XYZ,
            }
            if type2 in conversions.keys():
                return conversions[type2]

        if type2 == ColorType.BGR:
            conversions_inv: Dict[ColorType, CvColorConversionCode] = {
                ColorType.RGB: cv2.COLOR_RGB2BGR,
                ColorType.HSV: cv2.COLOR_HSV2BGR_FULL,
                ColorType.HLS: cv2.COLOR_HLS2BGR_FULL,
                ColorType.Lab: cv2.COLOR_Lab2BGR,
                ColorType.Luv: cv2.COLOR_Luv2BGR,
                ColorType.XYZ: cv2.COLOR_XYZ2BGR,
            }
            if type1 in conversions_inv.keys():
                return conversions_inv[type1]
        return None

    def handle_rgb() -> Optional[CvColorConversionCode]:
        if type1 == ColorType.RGB:
            conversions: Dict[ColorType, CvColorConversionCode] = {
                ColorType.BGR: cv2.COLOR_RGB2BGR,
                ColorType.HSV: cv2.COLOR_RGB2HSV_FULL,
                ColorType.HLS: cv2.COLOR_RGB2HLS_FULL,
                ColorType.Lab: cv2.COLOR_RGB2Lab,
                ColorType.Luv: cv2.COLOR_RGB2Luv,
                ColorType.XYZ: cv2.COLOR_RGB2XYZ,
            }
            if type2 in conversions.keys():
                return conversions[type2]

        if type2 == ColorType.RGB:
            conversions_inv: Dict[ColorType, CvColorConversionCode] = {
                ColorType.BGR: cv2.COLOR_BGR2RGB,
                ColorType.HSV: cv2.COLOR_HSV2RGB_FULL,
                ColorType.HLS: cv2.COLOR_HLS2RGB_FULL,
                ColorType.Lab: cv2.COLOR_Lab2RGB,
                ColorType.Luv: cv2.COLOR_Luv2RGB,
                ColorType.XYZ: cv2.COLOR_XYZ2RGB,
            }
            if type1 in conversions_inv.keys():
                return conversions_inv[type1]

        return None

    with_bgr = handle_bgr()
    if with_bgr is not None:
        return with_bgr

    with_rgb = handle_rgb()
    if with_rgb is not None:
        return with_rgb

    return None


def compute_possible_conversion_pairs(color_type: ColorType) -> List[ColorConversionPair]:
    r: List[ColorConversionPair] = []
    for other_color_type in ColorType:
        conversion_code = cv_color_conversion_code_between(color_type, other_color_type)
        conversion_code_inv = cv_color_conversion_code_between(other_color_type, color_type)
        if conversion_code is not None and conversion_code_inv is not None:
            conversion_direct = ColorConversion(
                f"{color_type.name}=>{other_color_type.name}", color_type, other_color_type, conversion_code
            )
            conversion_inv = ColorConversion(
                f"{other_color_type.name}=>{color_type.name}", other_color_type, color_type, conversion_code_inv
            )
            conversion_pair = ColorConversionPair(
                f"{color_type.name}=>{other_color_type.name}=>{color_type.name}", conversion_direct, conversion_inv
            )
            r.append(conversion_pair)
    return r
