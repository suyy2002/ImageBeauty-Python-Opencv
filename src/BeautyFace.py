import dlib
import cv2
import numpy as np
import math

predictor_path = 'shape_predictor_68_face_landmarks.dat'
# 使用dlib自带的frontal_face_detector作为特征提取器
detector = dlib.get_frontal_face_detector()  # 创建人脸检测器
predictor = dlib.shape_predictor(predictor_path)  # 获取人脸检测器

def landmark_dec_dlib_fun(img_src):
    img_gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)  # 灰度化
    land_marks = []  # 存放特征点
    rects = detector(img_gray, 0)  # 检测人脸
    for i in range(len(rects)):  # 遍历每一张人脸
        land_marks_node = np.matrix([[p.x, p.y] for p in predictor(img_gray, rects[i]).parts()])  # 获取人脸关键点
        land_marks.append(land_marks_node)  # 存入列表
    return land_marks

def localTranslationWarp(srcImg, startX, startY, endX, endY, radius):
    ddradius = float(radius * radius)  # 半径的平方
    copyImg = np.zeros(srcImg.shape, np.uint8)  # 创建一个空的图像
    copyImg = srcImg.copy()  # 复制原图像
    # 计算公式中的|m-c|^2
    ddmc = (endX - startX) * (endX - startX) + (endY - startY) * (endY - startY)
    H, W, C = srcImg.shape  # 获取图像的宽高和通道数
    for i in range(W):  # 遍历图像的每一行
        for j in range(H):  # 遍历图像的每一列
            # 计算该点是否在形变圆的范围之内
            # 优化，第一步，直接判断是会在（startX,startY)的矩阵框中
            if math.fabs(i - startX) > radius and math.fabs(j - startY) > radius:
                continue
            distance = (i - startX) * (i - startX) + (j - startY) * (j - startY)  # 计算距离
            if distance < ddradius:
                # 计算出（i,j）坐标的原坐标
                # 计算公式中右边平方号里的部分
                ratio = (ddradius - distance) / (ddradius - distance + ddmc)  # 计算比例
                ratio = ratio * ratio  # 比例的平方
                # 映射原位置
                UX = i - ratio * (endX - startX)  # 映射到新的X坐标
                UY = j - ratio * (endY - startY)  # 映射到新的Y坐标
                # 根据双线性插值法得到UX，UY的值
                value = BilinearInsert(srcImg, UX, UY)  # 双线性插值法
                # 改变当前 i ，j的值
                copyImg[j, i] = value  # 改变当前坐标的值
    return copyImg  # 返回形变后的图像

# 双线性插值法
def BilinearInsert(src, ux, uy):
    w, h, c = src.shape  # 获取图像的宽高和通道数
    if c == 3:
        x1 = int(ux)  # 取整
        x2 = x1 + 1  # 取整
        y1 = int(uy)  # 取整
        y2 = y1 + 1  # 取整
        part1 = src[y1, x1].astype(np.float) * (float(x2) - ux) * (float(y2) - uy)  # 取下面的像素点
        part2 = src[y1, x2].astype(np.float) * (ux - float(x1)) * (float(y2) - uy)  # 取右边的像素点
        part3 = src[y2, x1].astype(np.float) * (float(x2) - ux) * (uy - float(y1))  # 取上面的像素点
        part4 = src[y2, x2].astype(np.float) * (ux - float(x1)) * (uy - float(y1))  # 取右边的像素点
        insertValue = part1 + part2 + part3 + part4  # 加起来
        return insertValue.astype(np.uint8)  # 返回像素点

# 瘦脸
def face_thin(src, radius=0):
    landmarks = landmark_dec_dlib_fun(src)  # 获取特征点
    # 如果未检测到人脸关键点，就不进行瘦脸
    if len(landmarks) == 0:
        return src
    for landmarks_node in landmarks:  # 遍历每一张人脸
        left_landmark = landmarks_node[3]
        left_landmark_down = landmarks_node[5]
        right_landmark = landmarks_node[13]
        right_landmark_down = landmarks_node[15]
        endPt = landmarks_node[30]
        if radius == 0:  # 如果没有设置半径，就使用默认的半径
            # 计算第4个点到第6个点的距离作为瘦脸距离
            r_left = math.sqrt(
                (left_landmark[0, 0] - left_landmark_down[0, 0]) * (left_landmark[0, 0] - left_landmark_down[0, 0]) +
                (left_landmark[0, 1] - left_landmark_down[0, 1]) * (left_landmark[0, 1] - left_landmark_down[0, 1]))
            # 计算第14个点到第16个点的距离作为瘦脸距离
            r_right = math.sqrt(
                (right_landmark[0, 0] - right_landmark_down[0, 0]) * (
                        right_landmark[0, 0] - right_landmark_down[0, 0]) +
                (right_landmark[0, 1] - right_landmark_down[0, 1]) * (right_landmark[0, 1] - right_landmark_down[0, 1]))
        else:
            r_left = radius  # 如果设置了半径，就使用设置的半径
            r_right = radius  # 如果设置了半径，就使用设置的半径
        # 瘦左边脸
        thin_image = localTranslationWarp(src, left_landmark[0, 0], left_landmark[0, 1], endPt[0, 0], endPt[0, 1],
                                          r_left)
        # 瘦右边脸
        thin_image = localTranslationWarp(thin_image, right_landmark[0, 0], right_landmark[0, 1], endPt[0, 0],
                                          endPt[0, 1], r_right)
    return thin_image

# 红唇
def red_lip(img, points, color):
    for point in points:  # 遍历每一个点
        hull = cv2.convexHull(point)  # 计算凸包
        temp = cv2.drawContours(img.copy(), [hull], -1, (0, 0, color), -1)  # 绘制凸包
        image = cv2.addWeighted(temp, 0.2, img.copy(), 0.9, 0)  # 将凸包绘制到原图上
    return image

def face_red_lip(src, radius=0):
    img1 = src.copy()  # 复制原图
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)  # 转换为灰度图
    rects = detector(gray, 0)  # 检测人脸
    if len(rects) == 0:  # 如果没有检测到人脸
        return src
    # 遍历每一个检测到的人脸
    p = []
    for rect in rects:
        # 获取坐标
        result = predictor(gray, rect)  # 获取人脸关键点
        result = result.parts()  # 获取人脸关键点
        points = [[p.x, p.y] for p in result]  # 获取人脸关键点坐标
        points = np.array(points)  # 这里需将上面的points转化为数组
        for (x, y) in points[:]:  # 遍历每一个点
            cv2.circle(img1, (x, y), 3, (0, 255, 0), -1)  # 还是原谅色
        p.append(points[48:68])  # 嘴唇点集分布
    return red_lip(src, p, radius)  # 绘制嘴唇点集