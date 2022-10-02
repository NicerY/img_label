import sys
import os
import numpy as np
import cv2
import shutil
from PIL import Image
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QScrollArea, QLabel, QWidget, QLineEdit, QListWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QColor

reverse_file_path = os.path.dirname(os.path.abspath(__file__))[::-1]
for i in range(len(reverse_file_path)):
    if reverse_file_path[i]=='\\' or reverse_file_path[i]=='/':
        file_path = os.path.dirname(os.path.abspath(__file__))[:-(i+1)]
        processed_filepath = os.path.join(file_path,'processed')
        break
    else:
        continue

#重定义QLabel
class MyLabel(QLabel):
    def __init__(self,scale,original_width,original_height,original_margin):
        super(QLabel, self).__init__()
        self.scale = scale
        self.press = False
        self.width = 1086
        self.height = 757
        self.original_width = original_width
        self.original_height = original_height
        self.original_size = -1
        self.original_margin = original_margin
        self.width_ratio = self.width/self.original_width
        self.height_ratio = self.height/self.original_height
        self.x = 0
        self.y = 0
        
    labeled = pyqtSignal()

    # 设置区域大小
    def set_box_size(self,size):
        self.press = True
        self.original_size = size
        self.num_width = (self.original_width)//self.original_size
        self.num_height = (self.original_height-2*self.original_margin)//self.original_size
        self.all_num = int(self.num_width*self.num_height)
        self.tmp_filepath = os.path.join(file_path,'original\\label_block\\tmp_{}.txt'.format(self.original_size))

    # 重新初始化
    def reinit(self):
        self.press = False
        self.original_size = -1
        self.tmp_filepath = os.path.join(file_path,'original\\label_block\\tmp_{}.txt'.format(self.original_size))

    # 鼠标点击时选中区域
    def mousePressEvent(self,event):
        if self.press:
            print('press')
            self.y = int(((event.pos().y()-self.original_margin*self.height_ratio)//(self.original_size*self.height_ratio))+1)
            print(self.y)
            self.x = int(((event.pos().x())//(self.original_size*self.width_ratio))+1)
            print(self.x)

            if self.x<1 or self.x>self.num_width or self.y<1 or self.y>self.num_height:
                QtWidgets.QMessageBox.information(
                    self,'提示','所选区域超出范围！',
                    QtWidgets.QMessageBox.Ok
                )
            else:  
                with open(self.tmp_filepath,'r') as f:
                    data = f.read()
                    print(data)
                with open(self.tmp_filepath,'w') as f:
                    index = int((self.y-1)*self.num_width+self.x)
                    if index==1:
                        new_data = '1'+ data[1:]
                    elif index==self.all_num:
                        new_data = data[:-1] + '1'
                    else:
                        new_data = data[:index-1] + '1' + data[index:]
                    print(new_data)
                    f.write(new_data)
                self.update()
        self.labeled.emit()

class MainWindow(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.height = 900
        self.width =  1600
        self.scale = 0.22
        self.setGeometry(150, 100, self.width, self.height)
        self.setFixedSize(self.width, self.height) # 禁止拉伸窗口大小  
        self.setWindowTitle('图片标注')
        self.labeled_imglist_path = os.path.join(file_path, 'pro_original')
        self.check_folder(self.labeled_imglist_path)
        self.original_img_width = 4000
        self.original_img_height = 3000
        self.show_gridlines = False
        self.show_labeled_img = False
        self.show_selected_area_img = False
        self.original_margin = 300
        self.margin = int(300*self.scale)
        self.initUi()
        
    def initUi(self):

        #显示图片名
        self.ImgName = QLineEdit(self)
        self.ImgName.setGeometry(
            int(self.width*0.25) , int(self.height*0.04) ,int(self.width*0.4) , int(self.height*0.05))
        self.ImgName.setFont(QtGui.QFont("Timers", 24)) 
        self.ImgName.setReadOnly(1)   #设为只读

        #列表框
        self.ImgsList = QListWidget(self)
        self.ImgsList.setGeometry(
            int(self.width*0.012) , int(self.height*0.11), int(self.width*0.11) , int(self.height*0.11+660))
        self.ImgsList.doubleClicked.connect(self.ListShow)
        
        #分类按钮
        self.button_W = QPushButton('水(W)', self)
        self.button_W.setGeometry(int(self.width*0.84), int(self.height*0.17), 100, 40)
        self.button_W.setEnabled(False)
        self.button_W.clicked.connect(self.select_W)
        self.button_L = QPushButton('大茨藻(L)', self)
        self.button_L.setGeometry(int(self.width*0.84), int(self.height*0.23), 100, 40)
        self.button_L.setEnabled(False)
        self.button_L.clicked.connect(self.select_L)
        self.button_H = QPushButton('黑藻(H)', self)
        self.button_H.setGeometry(int(self.width*0.84), int(self.height*0.29), 100, 40)
        self.button_H.setEnabled(False)
        self.button_H.clicked.connect(self.select_H)
        self.button_C = QPushButton('金鱼藻(C)', self)
        self.button_C.setGeometry(int(self.width*0.84), int(self.height*0.35), 100, 40)
        self.button_C.setEnabled(False)
        self.button_C.clicked.connect(self.select_C)
        self.button_V = QPushButton('苦草(V)', self)
        self.button_V.setGeometry(int(self.width*0.84), int(self.height*0.41), 100, 40)
        self.button_V.setEnabled(False)
        self.button_V.clicked.connect(self.select_V)
        self.button_M = QPushButton('穗花狐尾藻(M)', self)
        self.button_M.setGeometry(int(self.width*0.84), int(self.height*0.47), 100, 40)
        self.button_M.setEnabled(False)
        self.button_M.clicked.connect(self.select_M)
        self.button_O = QPushButton('其他(O)', self)
        self.button_O.setGeometry(int(self.width*0.84), int(self.height*0.53), 100, 40)
        self.button_O.setEnabled(False)
        self.button_O.clicked.connect(self.select_O)
        self.button_Del = QPushButton('删除(Del)', self)
        self.button_Del.setGeometry(int(self.width*0.84), int(self.height*0.59), 100, 40)
        self.button_Del.setEnabled(False)
        self.button_Del.clicked.connect(self.select_Del)

        #设置区域大小
        self.button_set_area_size = QPushButton('确定', self)
        self.button_set_area_size.setGeometry(int(self.width*0.92), int(self.height*0.11), 100, 40)
        self.button_set_area_size.setToolTip('<b>点击这里确定</b>')
        self.button_set_area_size.setEnabled(False)
        self.button_set_area_size.clicked.connect(self.set_area_size)  
        self.text = QLineEdit('请输入区域大小', self)
        self.text.setGeometry(int(self.width*0.84), int(self.height*0.11), 100, 40)
        self.text.setEnabled(False)

        #读取图片
        self.button_img_select = QPushButton('选择文件夹', self)
        self.button_img_select.setGeometry(int(self.width*0.92), int(self.height*0.17), 100, 40)
        self.button_img_select.setEnabled(True)
        self.button_img_select.clicked.connect(self.select_img)

        #读取上一张图片
        self.button_pre_img = QPushButton('上一张', self)
        self.button_pre_img.setGeometry(int(self.width*0.92), int(self.height*0.23), 100, 40)
        self.button_pre_img.setEnabled(False)
        self.button_pre_img.clicked.connect(self.previous_img_click)

        #读取下一张图片
        self.button_next_img = QPushButton('下一张', self)
        self.button_next_img.setGeometry(int(self.width*0.92), int(self.height*0.29), 100, 40)
        self.button_next_img.setEnabled(False)
        self.button_next_img.clicked.connect(self.next_img_click)

        #显示选中区域
        self.button_show_selected_area = QPushButton('显示选中区域', self)
        self.button_show_selected_area.setGeometry(int(self.width*0.92), int(self.height*0.35), 100, 40)
        self.button_show_selected_area.setEnabled(False)
        self.button_show_selected_area.clicked.connect(self.show_selected_area)

        #显示已标注的图片
        self.button_show_annotated_img = QPushButton('显示已标注区域', self)
        self.button_show_annotated_img.setGeometry(int(self.width*0.92), int(self.height*0.41), 100, 40)
        self.button_show_annotated_img.setEnabled(False)
        self.button_show_annotated_img.clicked.connect(self.show_annotated_img)

        #显示原图
        self.button_original_img = QPushButton('显示原图', self)
        self.button_original_img.setGeometry(int(self.width*0.92), int(self.height*0.47), 100, 40)
        self.button_original_img.setEnabled(False)
        self.button_original_img.clicked.connect(self.show_original_img)

        #重新选择区域
        self.button_reselect_area = QPushButton('重新选择区域', self)
        self.button_reselect_area.setGeometry(int(self.width*0.92), int(self.height*0.53), 100, 40)
        self.button_reselect_area.setEnabled(False)
        self.button_reselect_area.clicked.connect(self.reselect_area)
        
        #图像展示窗口
        self.ImgView = QScrollArea(self)
        self.ImgView.setGeometry(
            int(self.width*0.13) , int(self.height*0.11),  int(self.width*0.13+880),  int(self.height*0.11+660))
        self.ImgView.setWidgetResizable(True)

        # 图像展示控件
        self.ImgShow = MyLabel(
            self.scale,
            self.original_img_width,
            self.original_img_height,
            self.original_margin
        )
        self.ImgShow.labeled.connect(self.update_labeled)


    #设置区域大小
    def set_area_size(self):
        self.input_box_size = int(self.text.text())

        if self.input_box_size>self.original_img_width or self.input_box_size>self.original_img_height:
            QtWidgets.QMessageBox.information(
                    self,'提示','请输入恰当的大小!',
                    QtWidgets.QMessageBox.Ok
                )
            self.text.setFocus()
        else:  
            self.original_box_size = self.input_box_size
            self.size = int(self.original_box_size*self.scale)
            print('开始标注! 区域大小为：',self.original_box_size)
            self.num_width = (self.original_img_width)//self.original_box_size
            self.num_height = (self.original_img_height-2*self.original_margin)//self.original_box_size
            self.generate_label_block_file()
            self.copy_to_tmp()
            print(self.num_width,self.num_height)
            self.show_gridlines = True
            self.show_labeled_img = True
            self.show_selected_area_img = True
            self.button_original_img.setEnabled(True)
            self.button_show_annotated_img.setEnabled(True)
            self.button_show_selected_area.setEnabled(True)
            self.button_reselect_area.setEnabled(True)
            self.button_W.setEnabled(True)
            self.button_L.setEnabled(True)
            self.button_H.setEnabled(True)
            self.button_C.setEnabled(True)
            self.button_V.setEnabled(True)
            self.button_M.setEnabled(True)
            self.button_O.setEnabled(True)
            self.button_Del.setEnabled(True)
            self.ImgShow.set_box_size(self.original_box_size)
            self.Imgshow()

    # 生成当前文件夹中所有图片的标记块
    def generate_label_block_file(self):
        self.init_msg = '0'*(self.num_width*self.num_height)
        print('共有',self.num_width*self.num_height,'块区域')
        self.reversed_dir_path = self.dir_path[::-1]
        for i in range(len(self.dir_path)):
            if self.reversed_dir_path[i]=='\\' or self.reversed_dir_path[i]=='/':
                self.label_block_path = os.path.join(self.dir_path[:-(i+1)], 'label_block')
                break
            else:
                continue
        
        self.label_block_list = os.listdir(self.label_block_path)
        for img in self.file_index_dict.keys():
            img_label_block_filename = img.split('.')[0]+'_'+self.text.text()+'.txt'
            if img_label_block_filename in self.label_block_list:
                print(img_label_block_filename,'已存在')
                continue
            else:
                file = open(os.path.join(self.label_block_path,img_label_block_filename),'w+')
                file.write(self.init_msg)
                print(img_label_block_filename+'创建成功')

        # 生成tmp.txt用于之后进行标记
        with open(os.path.join(self.label_block_path,'tmp_{}.txt'.format(self.text.text())),'w') as f:
            f.write(self.init_msg)
            print('成功创建tmp_{}.txt'.format(self.text.text()))


    # 选择目录按钮
    def select_img(self):
        try:
            self.ImgsList.clear()
            # 得到图片所在文件夹dir_path
            self.dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, '选择文件夹')
            
            # 将图片文件放到列表框中
            img_list = os.listdir(self.dir_path)
            for img in img_list:
                self.ImgsList.addItem(img)
                        
            if len(img_list) > 0:
                self.text.setText('请输入区域大小')
                self.text.setFocus()
                self.show_gridlines = False
                self.show_labeled_img = False
                self.show_selected_area_img = False
                self.button_original_img.setEnabled(False)
                self.button_show_annotated_img.setEnabled(False)
                self.button_show_selected_area.setEnabled(False)
                self.button_reselect_area.setEnabled(False)
                self.button_W.setEnabled(False)
                self.button_L.setEnabled(False)
                self.button_H.setEnabled(False)
                self.button_C.setEnabled(False)
                self.button_V.setEnabled(False)
                self.button_M.setEnabled(False)
                self.button_O.setEnabled(False)
                self.button_Del.setEnabled(False)
                self.ImgShow.reinit()
                self.check_folder(os.path.join(file_path,'original\\label_block'))

                # 图像文件索引字典
                self.totalnum = len(img_list)
                self.img_index_dict = dict()
                self.file_index_dict = dict()
                for i,d in enumerate(img_list):
                    self.img_index_dict[i] = d
                    self.file_index_dict[d] = i
                
                # 查找当前已标记图像并在列表框中显示为红色
                self.check_islabeled()
                
                # 当前的图像索引
                self.current_index = 0 
                self.get_current_img_path()

                # 实例化当前图像
                self.Imgshow()

                # 显示图片名
                self.ImgName.setText(self.img_index_dict[self.current_index])

                # 启用其他按钮
                self.button_pre_img.setEnabled(True)
                self.button_next_img.setEnabled(True)
                self.text.setEnabled(True)
                self.button_set_area_size.setEnabled(True)
                self.text.selectAll()
                self.text.setFocus()
                
            else:
                QtWidgets.QMessageBox.information(
                    self,'提示','文件夹没有发现图片文件！',
                    QtWidgets.QMessageBox.Ok
                )
        except Exception as e:
            print(repr(e))


    # 获得当前图片文件路径
    def get_current_img_path(self):
        self.current_filename = os.path.join(self.dir_path,self.img_index_dict[self.current_index])
        self.sample = cv2.imread(self.current_filename, cv2.IMREAD_COLOR)

    # 将当前的图像标记块索引文件中的内容复制到tmp.txt
    def copy_to_tmp(self):
        self.current_label_block_filename = os.path.join(
            self.label_block_path,self.img_index_dict[self.current_index].split('.')[0]+'_'+self.text.text()+'.txt'
        )
        with open(self.current_label_block_filename,'r') as f:
            data = f.read()
        with open(os.path.join(self.label_block_path,'tmp_{}.txt'.format(self.text.text())),'w') as f:
            f.write(data)

    # 更新当前图像的标记块索引文件
    def update_current_label_block_file(self):
        self.current_label_block_filename = os.path.join(
            self.label_block_path,self.img_index_dict[self.current_index].split('.')[0]+'_'+self.text.text()+'.txt'
        )
        with open(self.current_label_block_filename,'w') as f:
            f.write(self.tmp_data)

    # 上一张图片
    def previous_img_click(self):
        # 当前图像索引减1
        self.current_index -= 1
        if self.current_index in self.img_index_dict.keys():
            if self.show_gridlines:
                self.copy_to_tmp()
            self.get_current_img_path()
            # 实例化一个图像
            self.Imgshow()
            # 显示图片名
            self.ImgName.setText(self.img_index_dict[self.current_index])
        else:
            self.current_index += 1
            QtWidgets.QMessageBox.information(
                self, '提示', '图片列表到顶了！',
                QtWidgets.QMessageBox.Ok
            )

    # 下一张图片
    def next_img_click(self):
        # 当前图像索引加1
        self.current_index += 1
        if self.current_index in self.img_index_dict.keys():
            if self.show_gridlines:
                self.copy_to_tmp()
            self.get_current_img_path()
            # 实例化当前图像
            self.Imgshow()
            # 显示图片名
            self.ImgName.setText(self.img_index_dict[self.current_index])
        else:
            self.current_index -=1
            QtWidgets.QMessageBox.information(
                self,'提示','最后一张图片啦！',
                QtWidgets.QMessageBox.Ok
            )
    
    #图片展示
    def Imgshow(self):
        img_raw = Image.open(self.current_filename)
        width, height = img_raw.size
        imgview_width = int(width*self.ImgShow.scale)
        imgview_height = int(height*self.ImgShow.scale)
        image = img_raw.resize((imgview_width, imgview_height))
        
        #增加网格线  HWC
        if self.show_gridlines:
            image = np.array(image)
            image[self.margin-2:self.margin,:,0] = 255
            image[imgview_height-self.margin:imgview_height-self.margin+2,:,0] = 255
            i = 1
            while i<=self.num_height:
                image[self.margin+i*self.size-1:self.margin+i*self.size+1,:,0] = 255
                i+=1
            i = 1
            while i<=self.num_width:
                image[:,i*self.size-1:i*self.size+1,0] = 255
                i+=1

            # 显示已标记区域
            if self.show_labeled_img:
                self.current_label_block_filename = os.path.join(
                    self.label_block_path,self.img_index_dict[self.current_index].split('.')[0]+'_'+self.text.text()+'.txt'
                )
                with open(os.path.join(self.label_block_path,self.current_label_block_filename),'r') as f:
                    data = f.read()
                    print('当前',data)
                    for i,label in enumerate(data):
                        if label=='1':
                            if i%self.num_width==0:
                                image[self.margin+(int(i//self.num_width))*self.size+1:self.margin+(int(i//self.num_width)+1)*self.size-1,
                                0:self.size-1,
                                2] = 255
                            else:
                                image[self.margin+(int(i//self.num_width))*self.size+1:self.margin+(int(i//self.num_width)+1)*self.size-1,
                                int(i%self.num_width)*self.size+1:(int(i%self.num_width)+1)*self.size-1,
                                2] = 255
                        else:
                            continue

            # 显示选中的区域
            if self.show_selected_area_img:
                with open(os.path.join(self.label_block_path,'tmp_{}.txt'.format(self.text.text())),'r') as f:
                    new_data = f.read()
                    print('当前',data)
                    print('tmp', new_data,'\n')
                    for i,label in enumerate(new_data):
                        if label=='1' and data[i]=='0':
                            if i%self.num_width==0:
                                image[self.margin+(int(i//self.num_width))*self.size+1:self.margin+(int(i//self.num_width)+1)*self.size-1,
                                0:self.size-1,
                                0] = 255
                            else:
                                image[self.margin+(int(i//self.num_width))*self.size+1:self.margin+(int(i//self.num_width)+1)*self.size-1,
                                int(i%self.num_width)*self.size+1:(int(i%self.num_width)+1)*self.size-1,
                                0] = 255
                        else:
                            continue

            image = Image.fromarray(image)

        # 在ImgShow控件中显示图像
        self.Qimg = image.toqimage()
        self.QPixmapImg = QPixmap.fromImage(self.Qimg)
        self.ImgShow.setPixmap(self.QPixmapImg)
        self.ImgShow.setScaledContents(True)
        self.ImgView.setWidget(self.ImgShow)

    #点击列表框展示图片
    def ListShow(self):
        self.current_index = self.ImgsList.currentRow()
        self.get_current_img_path()
        if self.show_gridlines:
            print(1)
            self.copy_to_tmp()
            self.Imgshow()
            print(2)
        else:
            print(3)
            self.show_original_img()
            print(4)
        
    # 展示原始图像
    def show_original_img(self):
        self.show_labeled_img = False
        self.show_selected_area_img = False
        self.Imgshow()
        self.show_labeled_img = True
        self.show_selected_area_img = True

    # 展示已标记的图像
    def show_annotated_img(self):
        self.show_selected_area_img = False
        self.Imgshow()
        self.show_selected_area_img = True

    # 展示当前选中的区域
    def show_selected_area(self):
        self.Imgshow()

    #重新选择区域
    def reselect_area(self):
        self.copy_to_tmp()
        self.Imgshow()

    def update_labeled(self):
        if self.show_gridlines:
            self.Imgshow()

    # 获得数据
    def get_data(self):
        with open(os.path.join(self.label_block_path,'tmp_{}.txt'.format(self.text.text())),'r') as tmp_file:
            self.tmp_data = tmp_file.read()
        with open(os.path.join(self.label_block_path,self.current_label_block_filename),'r') as file:
            self.current_data = file.read()

    # 裁剪并分类图片
    def crop_sample(self,path):
        self.check_folder(path)
        for i,label in enumerate(self.tmp_data):
            if label=='1' and self.current_data[i]=='0':
                if i%self.num_width==0:
                    self.sample_y_min = self.original_margin+(int(i//self.num_width))*self.original_box_size
                    self.sample_y_max = self.original_margin+(int(i//self.num_width)+1)*self.original_box_size
                    self.sample_x_min = 0
                    self.sample_x_max = self.original_box_size
                else:
                    self.sample_y_min = self.original_margin+(int(i//self.num_width))*self.original_box_size
                    self.sample_y_max = self.original_margin+(int(i//self.num_width)+1)*self.original_box_size
                    self.sample_x_min = int(i%self.num_width)*self.original_box_size
                    self.sample_x_max = (int(i%self.num_width)+1)*self.original_box_size

                cropped_img = self.sample[self.sample_y_min:self.sample_y_max,
                                          self.sample_x_min:self.sample_x_max
                                        ]
                cv2.imwrite(os.path.join(path,self.img_index_dict[self.current_index].split('.')[0]+'_{}.jpg'.format(i+1)), cropped_img)
            else:
                continue
        
        if self.img_index_dict[self.current_index] not in self.labeled_list:
            shutil.copy(self.current_filename,self.labeled_imglist_path)
        self.check_islabeled()

    #标记为 水(W)
    def select_W(self):
        self.get_data()
        self.w_path = os.path.join(processed_filepath,'W',self.text.text())
        self.crop_sample(self.w_path)
        self.update_current_label_block_file()
        self.Imgshow()

    #标记为 大茨藻(L)
    def select_L(self):
        self.get_data()
        self.l_path = os.path.join(processed_filepath,'L',self.text.text())
        self.crop_sample(self.l_path)
        self.update_current_label_block_file()
        self.Imgshow()

    #标记为 黑藻(H)
    def select_H(self):
        self.get_data()
        self.h_path = os.path.join(processed_filepath,'H',self.text.text())
        self.crop_sample(self.h_path)
        self.update_current_label_block_file()
        self.Imgshow()

    #标记为 金鱼藻(C)
    def select_C(self):
        self.get_data()
        self.c_path = os.path.join(processed_filepath,'C',self.text.text())
        self.crop_sample(self.c_path)
        self.update_current_label_block_file()
        self.Imgshow()

    #标记为 苦草(V)
    def select_V(self):
        self.get_data()
        self.v_path = os.path.join(processed_filepath,'V',self.text.text())
        self.crop_sample(self.v_path)
        self.update_current_label_block_file()
        self.Imgshow()

    #标记为 穗花狐尾藻(M)
    def select_M(self):
        self.get_data()
        self.m_path = os.path.join(processed_filepath,'M',self.text.text())
        self.crop_sample(self.m_path)
        self.update_current_label_block_file()
        self.Imgshow()

    #标记为 其他(O)
    def select_O(self):
        self.get_data()
        self.o_path = os.path.join(processed_filepath,'O',self.text.text())
        self.crop_sample(self.o_path)
        self.update_current_label_block_file()
        self.Imgshow()

    #标记为 删除(Del)
    def select_Del(self):
        self.get_data()
        self.Del_path = os.path.join(processed_filepath,'Del',self.text.text())
        self.crop_sample(self.Del_path)
        self.update_current_label_block_file()
        self.Imgshow()
        
    #判断文件夹是否存在
    def check_folder(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    # 查找当前已标记图像并在列表框中显示为红色
    def check_islabeled(self):
        self.LabeledImg_index_dict = dict()
        self.labeled_list = os.listdir(self.labeled_imglist_path)
        for img in self.labeled_list:
            if img in self.file_index_dict:
                self.LabeledImg_index_dict[img] = 1
                self.ImgsList.item(self.file_index_dict.get(img)).setForeground(QColor('red'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())