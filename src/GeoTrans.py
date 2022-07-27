import cv2
import numpy as np


# 图像旋转
def rotate_image(image, angle):
    height, width = image.shape[:2]  # 获取图像的高和宽
    heightNew = int(width * np.fabs(np.sin(np.radians(angle))) + height * np.fabs(np.cos(np.radians(angle))))  # 计算新图像的高
    widthNew = int(height * np.fabs(np.sin(np.radians(angle))) + width * np.fabs(np.cos(np.radians(angle))))  # 计算新图像的宽
    matRotation = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)  # 计算旋转矩阵
    matRotation[0, 2] += (widthNew - width) / 2  # 将旋转中心点移至图像中央
    matRotation[1, 2] += (heightNew - height) / 2  # 将旋转中心点移至图像中央
    imgRotation = cv2.warpAffine(image, matRotation, (widthNew, heightNew), borderValue=(255, 255, 255))  # 广义旋转图像
    return imgRotation


# 图像右转90度
def rotate_right(image):
    img = cv2.transpose(image)  # 转置
    return cv2.flip(img, 0)  # 翻转

# 图像左转90度
def rotate_left(image):
    img = cv2.transpose(image)  # 转置
    return cv2.flip(img, 1)  # 翻转

# 图像翻转
def flip_image(image, code):
    return cv2.flip(image, code)  # 翻转

# 图片拼接
def merge_image(img_list, direction='vertical'):
    lens = len(img_list)  # 图片数量
    h = []  # 图片高度列表
    w = []  # 图片宽度列表
    for i in range(lens):  # 获取图片高度和宽度
        h.append(img_list[i].shape[0])
        w.append(img_list[i].shape[1])
    min_w = min(w)  # 最小宽度
    min_h = min(h)  # 最小高度
    if direction == 'vertical':  # 垂直拼接
        for i in range(lens):
            if w[i] != min_w:  # 宽度不等，进行调整
                img_list[i] = cv2.resize(img_list[i], (min_w, (int((min_w * h[i]) / w[i]))), interpolation=cv2.INTER_AREA)  # 调整图片等宽度
        return cv2.vconcat(img_list)
    elif direction == 'horizontal':  # 水平拼接
        for i in range(lens):
            if h[i] != min_h:  # 高度不等，进行调整
                img_list[i] = cv2.resize(img_list[i], (int((min_h * w[i]) / h[i]), min_h), interpolation=cv2.INTER_AREA)  # 调整图片等高度
        return cv2.hconcat(img_list)

# 格栅拼接
def merge_images(imgs_list, col, row):
    row_img = []  # 存放每行图片
    for i in range(row):  # 分割成row行
        col_img = imgs_list[i * col:i * col + col]  # 取出每行图片
        img = merge_image(col_img, 'horizontal')  # 水平拼接
        row_img.append(img)  # 存入每行图片
    return merge_image(row_img, 'vertical')  # 垂直拼接

# 图像加框
def add_frame(image, frame):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)  # 转换颜色通道至BGRA
    frame = cv2.resize(frame, (image.shape[1], image.shape[0]))  # 调整图片大小
    alpha_frame = frame[:, :, 3] / 255.0  # 获取透明度
    alpha_image = 1 - alpha_frame  # 获取透明度
    for c in range(0, 3):  # 对三个通道进行操作
        image[:, :, c] = (  # 计算新图像的像素值
                (alpha_image * image[:, :, c]) + (alpha_frame * frame[:, :, c]))
    return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)  # 转换颜色通道至BGR


# 图像裁剪
global imge
global point1, point2
global cut_img

def on_mouse(event, x, y, flags, param):
    global imge, point1, point2, cut_img  # 声明全局变量
    img2 = imge.copy()  # 复制图像
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        point1 = (x, y)  # 记录点击位置
        cv2.circle(img2, point1, 10, (0, 255, 0), 5)  # 画圆
        cv2.imshow('Cut Image', img2)  # 显示图像
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        cv2.rectangle(img2, point1, (x, y), (255, 0, 0), 0)  # 画矩形
        cv2.imshow('Cut Image', img2)  # 显示图像
    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
        point2 = (x, y)  # 记录点击位置
        cv2.rectangle(img2, point1, point2, (0, 0, 255), 0)  # 画矩形
        cv2.imshow('Cut Image', img2)  # 显示图像
        min_x = min(point1[0], point2[0])  # 获取矩形左上角x坐标
        min_y = min(point1[1], point2[1])  # 获取矩形左上角y坐标
        width = abs(point1[0] - point2[0])   # 获取矩形宽度
        height = abs(point1[1] - point2[1])  # 获取矩形高度
        cut_img = imge[min_y:min_y + height, min_x:min_x + width]  # 裁剪图像

def cut_image(image):
    global imge, cut_img
    imge = image
    cut_img = None
    cv2.namedWindow('Cut Image')
    cv2.setMouseCallback('Cut Image', on_mouse)
    cv2.imshow('Cut Image', imge)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if cut_img is not None:
        return cut_img
