import cv2
import numpy as np

# 高斯噪声
def gauss_noise(img, mu=0, sigma=20):
    noiseGause = np.random.normal(mu, sigma, img.shape)  # 使用numpy获取指定均值和标准差的随机数
    imgGaussNoise = img + noiseGause  # 将随机数加到图片上
    imgGaussNoise = np.uint8(cv2.normalize(imgGaussNoise, None, 0, 255, cv2.NORM_MINMAX))
    return imgGaussNoise

# 椒盐噪声
def slat_pepper_noise(img, slat=0.05, pepper=0.02):
    mask = np.random.choice((0, 0.5, 1), size=img.shape[:2], p=[pepper, (1 - slat - pepper), slat])  # 使用numpy返回指定概率的随机数
    imgChoiceNoise = img.copy()
    imgChoiceNoise[mask == 1] = 255  # 将mask为1的像素点设置为255
    imgChoiceNoise[mask == 0] = 0  # 将mask为0的像素点设置为0
    return imgChoiceNoise

# 均匀噪声
def uniform_noise(img, mean=10, sigma=100):
    a = 2 * mean - np.sqrt(12 * sigma)  # 均值
    b = 2 * mean + np.sqrt(12 * sigma)  # 标准差
    noiseUniform = np.random.uniform(a, b, img.shape)  # 使用numpy获取指定均值和标准差的均匀随机数
    imgUniformNoise = img + noiseUniform  # 将随机数加到图片上
    imgUniformNoise = np.uint8(cv2.normalize(imgUniformNoise, None, 0, 255, cv2.NORM_MINMAX))
    return imgUniformNoise

# 瑞利噪声
def rayleigh_noise(img, a=30.0):
    noiseRayleigh = np.random.rayleigh(a, size=img.shape)  # 使用numpy获取指定均值和标准差的瑞利随机数
    imgRayleighNoise = img + noiseRayleigh  # 将随机数加到图片上
    imgRayleighNoise = np.uint8(cv2.normalize(imgRayleighNoise, None, 0, 255, cv2.NORM_MINMAX))
    return imgRayleighNoise

# 伽马噪声
def gamma_noise(img, a=10.0, b=2.5):
    noiseGamma = np.random.gamma(shape=b, scale=a, size=img.shape)  # 使用numpy获取指定均值和标准差的伽马随机数
    imgGammaNoise = img + noiseGamma  # 将随机数加到图片上
    imgGammaNoise = np.uint8(cv2.normalize(imgGammaNoise, None, 0, 255, cv2.NORM_MINMAX))
    return imgGammaNoise

# 指数噪声
def exp_noise(img, a=10):
    noiseExp = np.random.exponential(scale=a, size=img.shape)  # 使用numpy获取指定均值和标准差的指数随机数
    imgExpNoise = img + noiseExp  # 将随机数加到图片上
    imgExpNoise = np.uint8(cv2.normalize(imgExpNoise, None, 0, 255, cv2.NORM_MINMAX))
    return imgExpNoise

# 均值滤波
def mean_filter(img, size=3):
    imgMeanFilter = cv2.blur(img, (size, size))
    return imgMeanFilter

# 中值滤波
def median_filter(img, size=3):
    imgMedianFilter = cv2.medianBlur(img, size)
    return imgMedianFilter

# 双边滤波
def bilateral_filter(img, size=15, sigmaColor=35, sigmaSpace=35):
    imgBilateralFilter = cv2.bilateralFilter(img, size, sigmaColor, sigmaSpace)
    return imgBilateralFilter

# 高斯滤波
def gaussian_filter(img, size=3, sigma=0):
    imgGaussianFilter = cv2.GaussianBlur(img, (size, size), sigmaX=sigma, sigmaY=sigma)
    return imgGaussianFilter
