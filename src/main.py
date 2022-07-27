import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem

from Effect import *
from Enhancement import *
from GeoTrans import *
from ImageFeature import *
from ImageStack import *
from MyQtUI1 import Ui_MainWindow
from MyView import GraphicsView
from NoiseFilter import *
from BeautyFace import face_thin, face_red_lip


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.pix = None  # 图像
        self.ShowGraphics = GraphicsView(self.centralwidget)  # 显示图像的组件
        self.verticalLayout.addWidget(self.ShowGraphics)  # 添加显示图像的组件到布局中
        self.scene = QGraphicsScene()  # 创建画布
        self.ShowGraphics.setScene(self.scene)  # 把画布添加到窗口
        self.ShowGraphics.show()  # 显示窗口

        self.undo_stack = ImageStack()  # 撤销栈
        self.redo_stack = ImageStack()  # 重做栈
        self.buffer_img = None  # 缓冲图像，用于可动态调整的功能
        self.contours = None  # 轮廓数组
        self.cnt_img = None  # 轮廓图像
        self.OpenAction.triggered.connect(self.OpenImage)
        self.SaveAction.triggered.connect(self.SaveImage)
        self.UndoAction.triggered.connect(self.Undo)
        self.RedoAction.triggered.connect(self.Redo)
        self.actionCamera.triggered.connect(self.Camera)
        self.OkButton.clicked.connect(self.ImageOk)
        self.CancelButton.clicked.connect(self.ImageCancel)

        self.SaltSlider.valueChanged.connect(self.SPNoise)
        self.PepperSlider.valueChanged.connect(self.SPNoise)
        self.GSsigmaSlider.valueChanged.connect(self.GSNoise)
        self.UniSigmaSlider.valueChanged.connect(self.UniNoise)
        self.ReilSlider.valueChanged.connect(self.ReilNoise)
        self.GammaSlider.valueChanged.connect(self.GammaNoise)
        self.ExpSlider.valueChanged.connect(self.ExpNoise)

        self.MeanspinBox.valueChanged.connect(self.MeanFilter)
        self.MedianspinBox.valueChanged.connect(self.MedianFilter)
        self.BilaspinBox.valueChanged.connect(self.BilaFilter)
        self.BilaCspinBox.valueChanged.connect(self.BilaFilter)
        self.BilaSspinBox.valueChanged.connect(self.BilaFilter)
        self.GausspinBox.valueChanged.connect(self.GaussFilter)
        self.GaussigmaSlider.valueChanged.connect(self.GaussFilter)

        self.Rotatedial.valueChanged.connect(self.Rotate)
        self.pushButtonLeft.clicked.connect(self.RotateLeft)
        self.pushButtonRight.clicked.connect(self.RotateRight)
        self.pushButtonCut.clicked.connect(self.CutImage)
        self.pushButtonUpDown.clicked.connect(self.FlipUpDown)
        self.pushButtonLeftRight.clicked.connect(self.FlipLeftRight)

        self.pushButtonHmerge.clicked.connect(self.HMerge)
        self.pushButtonVmerge.clicked.connect(self.VMerge)
        self.pushButton4Merge.clicked.connect(self.Merges)
        self.pushButtonFrame.clicked.connect(self.AddFrame)
        self.pushButtonFleet.clicked.connect(self.Fleet)
        self.pushButtonGlass.clicked.connect(self.Glass)
        self.pushButtonCartoon.clicked.connect(self.Cartoon)

        self.BrightnessSlider.valueChanged.connect(self.Enhance)
        self.ContrastSlider.valueChanged.connect(self.Enhance)
        self.SaturationSlider.valueChanged.connect(self.Enhance)
        self.RcolorSlider.valueChanged.connect(self.Enhance)
        self.GcolorSlider.valueChanged.connect(self.Enhance)
        self.BcolorSlider.valueChanged.connect(self.Enhance)
        self.pushButtonSmooth.clicked.connect(self.Smooth)
        self.pushButtonThin.clicked.connect(self.Thin)
        self.pushButtonWhite.clicked.connect(self.White)
        self.RedLipSlider.valueChanged.connect(self.RedLip)

        self.pushButtonFind.clicked.connect(self.FindContour)
        self.CntspinBox.valueChanged.connect(self.CntCenter)
        self.pushButtonCenter.clicked.connect(self.CntCenter)
        self.pushButtonRect.clicked.connect(self.CntRect)
        self.pushButtonMiniRect.clicked.connect(self.CntMiniRect)
        self.pushButtonCircle.clicked.connect(self.CntCircle)
        self.pushButtonTri.clicked.connect(self.CntTriangle)

    def OpenImage(self):
        """打开图像"""
        fileName, tmp = QFileDialog.getOpenFileName(self, '打开图像', 'Image', '*.png *.jpg *.bmp *.jpeg *.tif *.tiff *.webp')  # 获取文件路径
        if not fileName:  # 如果没有选择文件，则退出
            return
        root_dir, file_name = os.path.split(fileName)  # 按照路径将文件名和路径分割开
        pwd = os.getcwd()  # 返回当前工作目录
        if root_dir:
            os.chdir(root_dir)  # 解决opencv中文乱码问题，改变当前工作目录到指定的路径
        self.redo_stack.clear()  # 清空重做栈
        self.undo_stack.push(cv2.imread(file_name))  # 将图像加入撤销栈
        os.chdir(pwd)  # 改变当前工作目录回到原来的目录
        self.ShowImage(self.undo_stack.top())  # 将撤销栈顶图像显示在窗口中
        pass

    def SaveImage(self):
        """保存图像"""
        if self.undo_stack.isEmpty():
            return  # 如果撤销栈为空，则不执行任何操作
        name, tmp = QFileDialog.getSaveFileName(self, '保存图片', '', '*.png ;; *.jpg ;; *.bmp ;; *.jpeg')  # 获取文件路径
        if name != '':  # 如果路径不为空
            root_dir, name = os.path.split(name)  # 按照路径将文件名和路径分割开
            pwd = os.getcwd()  # 返回当前工作目录
            if root_dir:
                os.chdir(root_dir)  # 改变当前工作目录到指定的路径
            cv2.imencode(tmp[1:], self.undo_stack.top())[1].tofile(name)  # 将图像保存到指定的路径
            os.chdir(pwd)  # 改变当前工作目录回到原来的目录
        pass

    def ShowImage(self, img):
        """显示图像"""
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 把opencv 默认BGR转为通用的RGB
        x = img.shape[1]  # 获取图像的宽度
        y = img.shape[0]  # 获取图像的高度
        frame = QImage(rgb_img.data, x, y, x * 3, QImage.Format_RGB888)  # 将图像转换为QImage格式
        self.scene.clear()  # 清除scene残留
        self.pix = QPixmap.fromImage(frame)  # 将图像转换为QPixmap格式
        item = QGraphicsPixmapItem(QPixmap(frame))  # 将图像转换为QGraphicsPixmapItem格式
        item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)  # 设置图像可选可移动
        self.scene.addItem(item)  # 将图像添加到scene中
        item.setTransformationMode(Qt.SmoothTransformation)  # 设置图像缩放模式为平滑缩放
        self.ShowGraphics.fitInView(item, Qt.KeepAspectRatio)  # 将图像显示在窗口中

    def Undo(self):
        """撤销"""
        if self.undo_stack.size() == 1:  # 如果撤销栈只有一个元素，则不执行任何操作
            return
        self.redo_stack.push(self.undo_stack.pop())  # 将撤销栈顶冒出并加入重做栈
        self.ShowImage(self.undo_stack.top())  # 将撤销栈顶图像显示在窗口中
        pass

    def Redo(self):
        """重做"""
        if self.redo_stack.isEmpty():  # 如果重做栈为空，则不执行任何操作
            return
        self.undo_stack.push(self.redo_stack.pop())  # 将重做栈图像加入撤销栈
        self.ShowImage(self.undo_stack.top())  # 将撤销栈顶图像显示在窗口中
        pass

    def Camera(self):
        """拍照"""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 创建一个VideoCapture对象
        while True:  # 循环显示摄像头中的图像
            ret, frame = cap.read()  # 读取摄像头中的图像
            k = cv2.waitKey(1)  # 每隔1ms读取一次摄像头中的图像
            if k == 27:  # 如果按下ESC键，则退出循环
                break
            elif k == ord(' '):  # 如果按下空格键，则获取当前图像
                self.redo_stack.clear()  # 清空重做栈
                self.undo_stack.push(frame)  # 将图像加入撤销栈
                self.ShowImage(self.undo_stack.top())  # 将图像显示在窗口中
                break
            cv2.imshow("Press 'Space' to take a photo, Press 'Esc' to cancel", frame)  # 显示摄像头窗口
        cap.release()  # 释放摄像头
        cv2.destroyAllWindows()  # 关闭所有cv2窗口
        pass

    def ImageOk(self):
        """图像确认"""
        self.redo_stack.clear()  # 清空重做栈
        if self.buffer_img is None:  # 如果缓冲区中没有图像，则不执行任何操作
            return
        self.undo_stack.push(self.buffer_img)  # 将缓冲图像加入撤销栈
        self.ShowImage(self.undo_stack.top())  # 将栈顶图像显示在窗口中
        pass

    def ImageCancel(self):
        """图像取消"""
        self.buffer_img = None  # 清空缓冲图像
        if self.undo_stack.isEmpty():  # 如果撤销栈为空，则不执行任何操作
            return
        self.ShowImage(self.undo_stack.top())
        self.SaltSlider.setSliderPosition(0)
        self.PepperSlider.setSliderPosition(0)
        self.GSsigmaSlider.setSliderPosition(0)
        self.UniSigmaSlider.setSliderPosition(0)
        self.ReilSlider.setSliderPosition(0)
        self.GammaSlider.setSliderPosition(0)
        self.ExpSlider.setSliderPosition(0)
        self.MeanspinBox.setValue(1)
        self.MedianspinBox.setValue(1)
        self.BilaspinBox.setValue(1)
        self.BilaCspinBox.setValue(1)
        self.BilaSspinBox.setValue(1)
        self.GausspinBox.setValue(1)
        self.GaussigmaSlider.setSliderPosition(0)
        self.Rotatedial.setSliderPosition(0)
        self.BrightnessSlider.setSliderPosition(100)
        self.ContrastSlider.setSliderPosition(0)
        self.SaturationSlider.setSliderPosition(0)
        self.RcolorSlider.setSliderPosition(0)
        self.GcolorSlider.setSliderPosition(0)
        self.BcolorSlider.setSliderPosition(0)
        self.RedLipSlider.setSliderPosition(0)
        self.CntspinBox.setValue(1)
        pass

    def SPNoise(self):
        """椒盐噪声"""
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):  # 如果缓冲区中没有图像，且撤销栈为空，则不执行任何操作
            return
        self.buffer_img = slat_pepper_noise(self.undo_stack.top(),  # 对撤销栈顶的图像进行操作
                                            self.SaltSlider.value() / 500,  # 对椒盐噪声的程度进行设置
                                            self.PepperSlider.value() / 500)
        self.ShowImage(self.buffer_img)  # 将缓冲图像显示在窗口中

    def GSNoise(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = gauss_noise(self.undo_stack.top(),
                                      sigma=self.GSsigmaSlider.value())
        self.ShowImage(self.buffer_img)

    def UniNoise(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = uniform_noise(self.undo_stack.top(),
                                        sigma=self.UniSigmaSlider.value())
        self.ShowImage(self.buffer_img)

    def ReilNoise(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = rayleigh_noise(self.undo_stack.top(),
                                         self.ReilSlider.value())
        self.ShowImage(self.buffer_img)

    def GammaNoise(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = gamma_noise(self.undo_stack.top(),
                                      self.GammaSlider.value())
        self.ShowImage(self.buffer_img)

    def ExpNoise(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = exp_noise(self.undo_stack.top(),
                                    self.ExpSlider.value())
        self.ShowImage(self.buffer_img)

    def MeanFilter(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = mean_filter(self.undo_stack.top(),
                                      self.MeanspinBox.value())
        self.ShowImage(self.buffer_img)

    def MedianFilter(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = median_filter(self.undo_stack.top(),
                                        self.MedianspinBox.value())
        self.ShowImage(self.buffer_img)

    def BilaFilter(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = bilateral_filter(self.undo_stack.top(),
                                           self.BilaspinBox.value(),
                                           self.BilaCspinBox.value(),
                                           self.BilaSspinBox.value())
        self.ShowImage(self.buffer_img)

    def GaussFilter(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = gaussian_filter(self.undo_stack.top(),
                                          self.GausspinBox.value(),
                                          self.GaussigmaSlider.value())
        self.ShowImage(self.buffer_img)

    def Rotate(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = rotate_image(self.undo_stack.top(),
                                       self.Rotatedial.value())
        self.anglelabe.setText("{}°".format(self.Rotatedial.value()))
        self.ShowImage(self.buffer_img)

    def RotateLeft(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(rotate_left(self.undo_stack.top()))
        self.ShowImage(self.undo_stack.top())

    def RotateRight(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(rotate_right(self.undo_stack.top()))
        self.ShowImage(self.undo_stack.top())

    def CutImage(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(cut_image(self.undo_stack.top()))
        self.ShowImage(self.undo_stack.top())

    def FlipUpDown(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(flip_image(self.undo_stack.top(), 0))
        self.ShowImage(self.undo_stack.top())

    def FlipLeftRight(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(flip_image(self.undo_stack.top(), 1))
        self.ShowImage(self.undo_stack.top())

    def HMerge(self):
        self.redo_stack.clear()
        # 打开多个图片
        fileNames, tmp = QFileDialog.getOpenFileNames(self, '打开图像', 'Image', '*.png *.jpg *.bmp *.jpeg *.gif *.tiff *.tga *webp')
        if not fileNames:
            return
        pwd = os.getcwd()  # 返回当前工作目录
        img_list = []
        for fileName in fileNames:
            root_dir, file_name = os.path.split(fileName)  # 按照路径将文件名和路径分割开
            if root_dir:
                os.chdir(root_dir)  # 改变当前工作目录到指定的路径。
            img_list.append(cv2.imread(file_name))
        os.chdir(pwd)
        self.undo_stack.push(merge_image(img_list, direction='horizontal'))
        self.ShowImage(self.undo_stack.top())
        pass

    def VMerge(self):
        self.redo_stack.clear()
        # 打开多个图片
        fileNames, tmp = QFileDialog.getOpenFileNames(self, '打开图像', 'Image', '*.png *.jpg *.bmp *.jpeg *.gif *.tiff *.tga *webp')
        if not fileNames:
            return
        pwd = os.getcwd()  # 返回当前工作目录
        img_list = []
        for fileName in fileNames:
            root_dir, file_name = os.path.split(fileName)
            if root_dir:
                os.chdir(root_dir)
            img_list.append(cv2.imread(file_name))
        os.chdir(pwd)
        self.undo_stack.push(merge_image(img_list, direction='vertical'))
        self.ShowImage(self.undo_stack.top())
        pass

    def Merges(self):
        image_num = self.colspinBox.value()*self.rowspinBox.value()
        if image_num == 0:
            return
        self.redo_stack.clear()
        img_list = []
        pwd = os.getcwd()
        while image_num > len(img_list):
            fileNames, tmp = QFileDialog.getOpenFileNames(self, '打开图像', 'Image',
                                                          '*.png *.jpg *.bmp *.jpeg *.gif *.tiff *.tga *webp')
            if not fileNames:
                return
            for fileName in fileNames:
                root_dir, file_name = os.path.split(fileName)
                if root_dir:
                    os.chdir(root_dir)
                img_list.append(cv2.imread(file_name))
        os.chdir(pwd)
        self.undo_stack.push(merge_images(img_list, self.colspinBox.value(), self.rowspinBox.value()))
        self.ShowImage(self.undo_stack.top())
        pass

    def AddFrame(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        fileName, tmp = QFileDialog.getOpenFileName(self, '选择相框', 'Frame', '*.png')
        if not fileName:
            return
        root_dir, file_name = os.path.split(fileName)  # 按照路径将文件名和路径分割开
        pwd = os.getcwd()  # 返回当前工作目录
        if root_dir:
            os.chdir(root_dir)  # 改变当前工作目录到指定的路径。
        self.redo_stack.clear()
        self.undo_stack.push(add_frame(self.undo_stack.top(), cv2.imread(file_name, -1)))
        os.chdir(pwd)
        self.ShowImage(self.undo_stack.top())

    def Fleet(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(effect_fleet(self.undo_stack.top()))
        self.ShowImage(self.undo_stack.top())
        pass

    def Glass(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(effect_glass(self.undo_stack.top()))
        self.ShowImage(self.undo_stack.top())
        pass

    def Cartoon(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.redo_stack.clear()
        self.undo_stack.push(effect_cartoon(self.undo_stack.top()))
        self.ShowImage(self.undo_stack.top())
        pass

    def Enhance(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = brightness_contrast(self.undo_stack.top(),
                                              self.BrightnessSlider.value(),
                                              self.ContrastSlider.value())
        self.buffer_img = saturation_image(self.buffer_img,
                                           self.SaturationSlider.value())
        self.buffer_img = rgb_image(self.buffer_img,
                                    self.RcolorSlider.value(),
                                    self.GcolorSlider.value(),
                                    self.BcolorSlider.value())
        self.ShowImage(self.buffer_img)
        pass

    def Smooth(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.undo_stack.push(bilateral_filter(self.undo_stack.top()))
        self.redo_stack.clear()
        self.ShowImage(self.undo_stack.top())
        pass

    def Thin(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.undo_stack.push(face_thin(self.undo_stack.top()))
        self.redo_stack.clear()
        self.ShowImage(self.undo_stack.top())
        pass

    def White(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.undo_stack.push(brightness_contrast(self.undo_stack.top(), 130, 20))
        self.redo_stack.clear()
        self.ShowImage(self.undo_stack.top())
        pass

    def RedLip(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.buffer_img = face_red_lip(self.undo_stack.top(), self.RedLipSlider.value())
        self.ShowImage(self.buffer_img)
        pass

    def FindContour(self):
        if (self.buffer_img is None) & (self.undo_stack.isEmpty()):
            return
        self.cnt_img, self.contours = find_contours(self.undo_stack.top())
        self.ShowImage(self.cnt_img)
        pass

    def CntCenter(self):
        if self.contours is None:
            self.textBrowser.append("请先执行“寻找轮廓”\n")
            return
        if self.CntspinBox.value() > len(self.contours):
            self.textBrowser.append("轮廓序号超出范围\n")
            return
        now_cnt = self.contours[self.CntspinBox.value()]
        self.textBrowser.append("{}号轮廓的周长为: {}, : 面积为:{}\n".format(self.CntspinBox.value(),
                                                                   cv2.arcLength(now_cnt, True),
                                                                   cv2.contourArea(now_cnt)))
        center = centroid(self.cnt_img, self.contours[self.CntspinBox.value()])
        self.textBrowser.append("{}号轮廓的中心坐标为: {}\n".format(self.CntspinBox.value(),
                                                           (center['cx'], center['cy'])))
        self.buffer_img = center['img']
        self.ShowImage(self.buffer_img)
        pass

    def CntRect(self):
        if self.contours is None:
            self.textBrowser.append("请先执行“寻找轮廓”\n")
            return
        if self.CntspinBox.value() > len(self.contours):
            self.textBrowser.append("轮廓序号超出范围\n")
            return
        vrect = vertical_rect(self.cnt_img, self.contours[self.CntspinBox.value()])
        self.textBrowser.append("{}号轮廓垂直外接矩形左上顶点坐标: {}, 宽高: {}\n".format(self.CntspinBox.value(),
                                                                         (vrect['x'], vrect['y']),
                                                                         (vrect['w'], vrect['h'])))
        self.buffer_img = vrect['img']
        self.ShowImage(self.buffer_img)
        pass

    def CntMiniRect(self):
        if self.contours is None:
            self.textBrowser.append("请先执行“寻找轮廓”\n")
            return
        if self.CntspinBox.value() > len(self.contours):
            self.textBrowser.append("轮廓序号超出范围\n")
            return
        minirect = minimum_rect(self.cnt_img, self.contours[self.CntspinBox.value()])
        self.textBrowser.append(
            "{}号轮廓最小外接矩形的中心点坐标: {}, 宽高: {}, 旋转角度: {}, 面积: {}, 周长: {}\n".format(self.CntspinBox.value(),
                                                                               (minirect['x'], minirect['y']),
                                                                               (minirect['w'], minirect['h']),
                                                                               minirect['ang'],
                                                                               minirect['w'] * minirect['h'],
                                                                               (minirect['w'] + minirect['h']) * 2))
        self.textBrowser.append("矩形性: {:.2%}\n".format(minirect['rect']))
        self.buffer_img = minirect['img']
        self.ShowImage(self.buffer_img)
        pass

    def CntCircle(self):
        if self.contours is None:
            self.textBrowser.append("请先执行“寻找轮廓”\n")
            return
        if self.CntspinBox.value() > len(self.contours):
            self.textBrowser.append("轮廓序号超出范围\n")
            return
        minicircle = minimum_circle(self.cnt_img, self.contours[self.CntspinBox.value()])
        self.textBrowser.append(
            "{}号轮廓外接圆的圆心坐标: {}, 半径: {}, 面积: {:.2f}, 周长: {:.2f}\n".format(self.CntspinBox.value(),
                                                                         (minicircle['x'], minicircle['y']),
                                                                         minicircle['r'],
                                                                         minicircle['r'] ** 2 * 3.14,
                                                                         minicircle['r'] * 2 * 3.14))
        self.textBrowser.append("圆形性: {:.2%}, 球状度:{:.2%}\n".format(minicircle['circle'], minicircle['sphere']))
        self.buffer_img = minicircle['img']
        self.ShowImage(self.buffer_img)
        pass

    def CntTriangle(self):
        if self.contours is None:
            self.textBrowser.append("请先执行“寻找轮廓”\n")
            return
        if self.CntspinBox.value() > len(self.contours):
            self.textBrowser.append("轮廓序号超出范围\n")
            return
        minitriangle = minimum_triangle(self.cnt_img, self.contours[self.CntspinBox.value()])
        self.textBrowser.append(
            "{}号轮廓外接三角形的面积: {:.2f}\n".format(self.CntspinBox.value(),
                                             minitriangle['area']))
        self.buffer_img = minitriangle['img']
        self.ShowImage(self.buffer_img)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)  # 在 QApplication 方法中使用，创建应用程序对象
    myWin = MyMainWindow()  # 实例化 MyMainWindow 类，创建主窗口
    myWin.show()  # 在桌面显示控件 myWin
    sys.exit(app.exec_())  # 结束进程，退出程序
