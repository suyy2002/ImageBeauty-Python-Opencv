import cv2
import numpy as np

drawing = False
mode = False


class GraphCutXupt:  # 寻找轮廓
    def __init__(self, t_img):
        self.img = t_img  # 原图
        self.img_raw = self.img.copy()  # 原图
        self.img_width = self.img.shape[0]  # 原图宽
        self.img_height = self.img.shape[1]  # 原图高
        self.img_show = self.img.copy()  # 显示图
        self.img_gc = self.img.copy()  # 图像分割图
        self.img_gc = cv2.GaussianBlur(self.img_gc, (3, 3), 0)  # 高斯滤波
        self.lb_up = False  # 判断是否点击上方
        self.rb_up = False  # 判断是否点击右上方
        self.lb_down = False  # 判断是否点击下方
        self.rb_down = False   # 判断是否点击右下方
        self.mask = np.full(self.img.shape[:2], 2, dtype=np.uint8)  # 初始化掩膜
        self.firt_choose = True  # 判断是否第一次点击

# 鼠标的回调函数
def mouse_event2(event, x, y, flags, param):
    global drawing, last_point, start_point  # 全局变量
    # 左键按下：开始画图
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键按下
        drawing = True  # 开始画图
        last_point = (x, y)  # 记录点击的位置
        start_point = last_point  # 记录点击的位置
        param.lb_down = True  # 判断是否点击上方
    elif event == cv2.EVENT_RBUTTONDOWN:  # 右键按下
        drawing = True  # 开始画图
        last_point = (x, y)  # 记录点击的位置
        start_point = last_point  # 记录点击的位置
        param.rb_down = True  # 判断是否点击下方
    # 鼠标移动，画图
    elif event == cv2.EVENT_MOUSEMOVE:  # 鼠标移动
        if drawing:  # 如果正在画图
            if param.lb_down:  # 判断是否点击上方
                cv2.line(param.img_show, last_point, (x, y), (0, 0, 255), 2, -1)  # 画线
                cv2.rectangle(param.mask, last_point, (x, y), 1, -1, 4)  # 画矩形
            else:  # 判断是否点击下方
                cv2.line(param.img_show, last_point, (x, y), (255, 0, 0), 2, -1)  # 画线
                cv2.rectangle(param.mask, last_point, (x, y), 0, -1, 4)  # 画矩形
            last_point = (x, y)  # 记录点击的位置
    # 左键释放：结束画图
    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
        drawing = False  # 结束画图
        param.lb_up = True  # 判断是否点击上方
        param.lb_down = False  # 判断是否点击下方
        cv2.line(param.img_show, last_point, (x, y), (0, 0, 255), 2, -1)  # 画线
        if param.firt_choose:  # 判断是否第一次点击
            param.firt_choose = False  # 判断是否第一次点击
        cv2.rectangle(param.mask, last_point, (x, y), 1, -1, 4)  # 画矩形
    elif event == cv2.EVENT_RBUTTONUP:  # 右键释放
        drawing = False  # 结束画图
        param.rb_up = True  # 判断是否点击上方
        param.rb_down = False  # 判断是否点击下方
        cv2.line(param.img_show, last_point, (x, y), (255, 0, 0), 2, -1)  # 画线
        if param.firt_choose:  # 判断是否第一次点击
            param.firt_choose = False  # 判断是否第一次点击
            param.mask = np.full(param.imge.shape[:2], 3, dtype=np.uint8)  # 初始化掩膜
        cv2.rectangle(param.mask, last_point, (x, y), 0, -1, 4)  # 画矩形

# 寻找轮廓
def find_object(img):
    g_img = GraphCutXupt(img)  # 创建图像分割类
    cv2.namedWindow('image')  # 创建窗口
    # 定义鼠标的回调函数
    cv2.setMouseCallback('image', mouse_event2, g_img)  # 设置鼠标回调函数
    while (True):  # 循环
        cv2.imshow('image', g_img.img_show)  # 显示图像
        if g_img.lb_up or g_img.rb_up:  # 判断是否点击上方或下方
            g_img.lb_up = False  # 判断是否点击上方
            g_img.rb_up = False  # 判断是否点击下方
            bgdModel = np.zeros((1, 65), np.float64)  # 初始化背景模型
            fgdModel = np.zeros((1, 65), np.float64)  # 初始化前景模型
            rect = (1, 1, g_img.img.shape[1], g_img.img.shape[0])  # 初始化矩形
            mask = g_img.mask  # 获取掩膜
            g_img.img_gc = g_img.img.copy()  # 复制图像
            cv2.grabCut(g_img.img_gc, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)  # 分割图像
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')  # 0和2做背景
            g_img.img_gc = g_img.img_gc * mask2[:, :, np.newaxis]  # 使用蒙板来获取前景区域
            cv2.imshow('now', g_img.img_gc)  # 显示图像
        if cv2.waitKey(1) == 32:  # 判断是否按下空格键
            cv2.destroyAllWindows()  # 销毁窗口
            break
    return g_img.img_gc  # 返回分割后的图像

# 图像预处理
def find_contours(img):
    # HSV 色彩空间图像分割
    image = find_object(img)  # 寻找轮廓
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # 将图片转换到 HSV 色彩空间
    lowerColor, upperColor = np.array([0, 0, 0]), np.array([1, 1, 1])  # 蓝色阈值
    segment = cv2.inRange(hsv, lowerColor, upperColor)  # 背景色彩图像分割
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # (5, 5) 结构元
    binary = cv2.dilate(cv2.bitwise_not(segment), kernel=kernel, iterations=3)  # 图像膨胀

    # 寻找二值化图中的轮廓
    # binary, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # OpenCV3
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # OpenCV4
    #  绘制全部轮廓，contourIdx=-1 绘制全部轮廓
    for i in range(len(contours)):  # 绘制第 i 个轮廓
        if hierarchy[0][i][3] == -1:  # 最外层轮廓
            rect = cv2.minAreaRect(contours[i])  # 最小外接矩形
            x, y = int(rect[0][0]), int(rect[0][1])  # 最小外接矩形的中心(x,y)
            text = "{}:({},{})".format(i, x, y)  # 显示文字
            img = cv2.drawContours(img, contours, i, (255, 255, 255), -1)  # 绘制第 i 个轮廓, 内部填充
            img = cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255))  # 显示文字
    return img, contours  # 返回图像和轮廓
