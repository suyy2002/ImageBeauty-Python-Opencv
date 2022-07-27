import cv2
import numpy as np


# 亮度和对比度
def brightness_contrast(image, alpha=0, beta=0):
    image_copy = image.copy()
    alpha = alpha * 0.01  # 将alpha转换为浮点型
    return np.uint8(np.clip((alpha * image_copy + beta), 0, 255))  # 使用公式alpha*f(x)+beta对图像进行亮度和对比度调整

# 饱和度
def saturation_image(image, value=0):
    fImg = image.astype(np.float32)  # 将图像转换为浮点型
    fImg = fImg / 255.0  # 将图像转换为[0,1]区间
    hlsImg = cv2.cvtColor(fImg, cv2.COLOR_BGR2HLS)  # 将图像转换到 HLS 色彩空间
    hlsImg[:, :, 2] = (1.0 + value / float(100)) * hlsImg[:, :, 2]  # 对亮度通道进行调整
    hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1  # 防止亮度超过 1
    res = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR)  # 将 HLS 色彩空间转换回 BGR 色彩空间
    res = (res * 255).astype(np.uint8)  # 将图像转换为 uint8 型
    return res

# RGB色彩调整
def rgb_image(image, r=0, g=0, b=0):
    b1, g1, r1 = cv2.split(image)  # 将图像分割为三个通道
    b1 = cv2.add(b1, b)  # 将b通道的值加上b
    g1 = cv2.add(g1, g)  # 将g通道的值加上g
    r1 = cv2.add(r1, r)  # 将r通道的值加上r
    bgr = cv2.merge((b1, g1, r1))  # 将三个通道合并为一个图像
    return bgr

