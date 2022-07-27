import cv2
import numpy as np


# 绘制重心
def centroid(img, cnt):
    image = img.copy()  # 复制图像
    M = cv2.moments(cnt)  # 返回字典，几何矩 mpq, 中心矩 mupq 和归一化矩 nupq
    cx = round(M['m10'] / M['m00'])  # 中心点 x 坐标
    cy = round(M['m01'] / M['m00'])  # 中心点 y 坐标
    cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)  # 在轮廓的质心上绘制圆点
    res = {'img': image, 'cx': cx, 'cy': cy}  # 返回结果
    return res

# 垂直矩形边界框
def vertical_rect(img, cnt):
    image = img.copy()  # 复制图像
    x, y, w, h = cv2.boundingRect(cnt)  # 返回轮廓的坐标和宽高(矩形左上顶点的坐标 x, y, 矩形宽度 w, 高度 h)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # 绘制垂直矩形边界框
    res = {'img': image, 'x': x, 'y': y, 'w': w, 'h': h}  # 返回结果
    return res

# 最小矩形边界框
def minimum_rect(img, cnt):
    image = img.copy()  # 复制图像
    area = cv2.contourArea(cnt)  # 返回轮廓面积
    rect = cv2.minAreaRect(cnt)  # 中心点 (x,y), 矩形宽度高度 (w,h), 旋转角度 ang
    (x, y), (w, h), ang = np.int32(rect[0]), np.int32(rect[1]), round(rect[2], 1)  # 将结果转换为整数
    box = np.int32(cv2.boxPoints(rect))  # 计算旋转矩形的顶点, (4, 2)
    cv2.drawContours(image, [box], 0, (0, 0, 255), 2)  # # 将旋转矩形视为一个轮廓进行绘制
    res = {'img': image, 'x': x, 'y': y, 'w': w, 'h': h, 'ang': ang, 'rect':  area / (w * h)}  # 返回结果
    return res

# 轮廓的最小外接圆
def minimum_circle(img, cnt):
    image = img.copy()  # 复制图像
    area = cv2.contourArea(cnt)  # 返回轮廓面积
    circumference = cv2.arcLength(cnt, True)  # 返回轮廓周长
    (x, y), radius = cv2.minEnclosingCircle(cnt)  # 返回圆心坐标和半径
    center = (int(x), int(y))  # 将结果转换为整数
    radius = int(radius)  # 将结果转换为整数
    cv2.circle(image, center, radius, (0, 255, 0), 2)  # 绘制最小外接圆
    res = {'img': image, 'x': x, 'y': y, 'r': radius,
           'circle': (4 * np.pi * area) / (circumference**2),
           'sphere': np.sqrt(area / (3.14 * radius ** 2))}  # 返回结果
    return res

# 轮廓的最小外接三角形
def minimum_triangle(img, cnt):
    image = img.copy()  # 复制图像
    area, triangle = cv2.minEnclosingTriangle(cnt)  # area 三角形面积, triangle 三角形顶点 (3,1,2)
    intTri = np.int32(triangle)  # 将结果转换为整数
    cv2.polylines(image, [intTri], True, (255, 0, 0), 2)  # 绘制最小外接三角形
    res = {'img': image, 'area': area}  # 返回结果
    return res
