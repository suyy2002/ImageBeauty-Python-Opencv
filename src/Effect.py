import cv2
import numpy as np


# 图像效果类
class ImgEffects:
    def __init__(self, img) -> None:
        self.src = img  # 原图
        self.gray = cv2.cvtColor(self.src, cv2.COLOR_BGR2GRAY)  # 灰度图
        self.h, self.w = self.src.shape[:2]  # 图像高度和宽度

    # 毛玻璃特效
    def glass(self):
        glassImg = np.zeros((self.h, self.w, 3), np.uint8)  # 创建一个空白图像
        for i in range(self.h - 6):  # 循环遍历图像的每一行
            for j in range(self.w - 6):  # 循环遍历图像的每一列
                index = int(np.random.random() * 6)  # 随机选择一个索引
                glassImg[i, j] = self.src[i + index, j + index]  # 将图像的每一个像素点赋值给glassImg
        return glassImg  # 返回毛玻璃图像

    # 流年特效
    def fleet(self):
        fleetImg = np.zeros((self.h, self.w, 3), np.uint8)  # 创建一个空白图像
        for i in range(self.h):  # 循环遍历图像的每一行
            for j in range(0, self.w):  # 循环遍历图像的每一列
                b = np.sqrt(self.src[i, j][0]) * 14  # 计算b的值
                g = self.src[i, j][1]  # 计算g的值
                r = self.src[i, j][2]  # 计算r的值
                if b > 255:  # 如果b的值大于255
                    b = 255  # 就赋值255
                fleetImg[i, j] = np.uint8((b, g, r))  # 将图像的每一个像素点赋值给fleetImg
        return fleetImg  # 返回流年图像

    # 卡通特效
    def cartoon(self):
        num = 7  # 双边滤波数目
        for i in range(num):  # 循环遍历滤波数目
            cv2.bilateralFilter(self.src, d=9, sigmaColor=5, sigmaSpace=3)  # 双边滤波
        median = cv2.medianBlur(self.gray, 7)  # 中值滤波
        edge = cv2.adaptiveThreshold(median, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=5, C=2)  # 自适应阈值
        edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2RGB)  # 转换颜色空间
        return cv2.bitwise_and(self.src, edge)  # 将图像与阈值图像进行位运算


def effect_glass(img):
    process = ImgEffects(img)
    return process.glass()

def effect_fleet(img):
    process = ImgEffects(img)
    return process.fleet()

def effect_cartoon(img):
    process = ImgEffects(img)
    return process.cartoon()
