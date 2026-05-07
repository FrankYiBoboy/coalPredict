# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt,QThread, pyqtSignal
from PyQt5.QtWidgets import QAction  # 需要导入 QAction
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog # 导入打印支持
from PyQt5.QtGui import QPainter # 导入绘图笔

from qfluentwidgets import (StateToolTip,InfoBar,InfoBarPosition,FluentIcon)
from ..common.translator import Translator

from .Ui_form_interface import Ui_form
from .algorithm import WorkingFace,PIMSolver,SubsidenceVisualizer
from .gallery_interface import GalleryInterface

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
from scipy import integrate

import os
import json
import datetime
import shutil

# ==========================================================
# 1. 定义工作线程类
# ==========================================================
class CalculationWorker(QThread):
    # 定义信号：计算完成后发送数据
    # finished(Z矩阵, 时间曲线数据元组, 工作面列表, 范围信息)
    calculation_finished = pyqtSignal(object, object, list, tuple)
    error_occurred = pyqtSignal(str)

    def __init__(self, faces_data, start_pos,end_pos,time_list, range_data):
        super().__init__()
        self.faces_data = faces_data # 传递纯数据而非对象，避免线程冲突
        self.start_pos = start_pos # 观测线起点终点
        self.end_pos = end_pos
        self.time_list = time_list # 观测时间序列
        self.range_data = range_data # (x_min, x_max, y_min, y_max)

    def run(self):
        try:
            # --- 1. 在线程中重建 Solver ---
            solver = PIMSolver()
            faces_objects = []
            face_results = []
            global_max_w = 0.0
            
            for f_data in self.faces_data:
                # 解包数据重建 WorkingFace 对象
                # f_data: (name, (x1,x2), (y1,y2), H, m, alpha, q, tan_beta)
                face = WorkingFace(*f_data)
                solver.add_face(face)
                faces_objects.append(face)

            # --- 2. 执行耗时的等值线计算 (网格) ---
            x_min, x_max, y_min, y_max = self.range_data
            
            plot_x_min, plot_x_max = x_min - 100, x_max + 100
            plot_y_min, plot_y_max = y_min - 50, y_max + 50
            
            # --- 3. 计算测线数据 ---
            distances, w_finals = solver.calculate_line_subsidence(self.start_pos, self.end_pos)
            
            # 打包成 tuple 发送
            line_data = (distances, w_finals)
            
            # 局部积分数据
            for idx,face in enumerate(faces_objects):
                xs = np.linspace(face.x_start, face.x_end, 50)
                ys = np.linspace(face.y_start, face.y_end, 50)
                X,Y = np.meshgrid(xs, ys)
                Z_local = np.zeros_like(X)
                
                for i in range(len(ys)):
                    for j in range(len(xs)):
                        val,_ = integrate.dblquad(
                            func=solver._integrand,
                            a=face.x_start, b=face.x_end,
                            gfun=lambda x: face.y_start,
                            hfun=lambda x: face.y_end,
                            args=(xs[j], ys[i], face.r0)
                        )
                        Z_local[i,j] = face.W_max * val
            
                # 统计数据
                local_max = np.max(Z_local)
                if local_max > global_max_w: global_max_w = local_max
                face_results.append((X, Y, Z_local, face, local_max))

            # 4. 发送结果
            # 注意：把实际用于绘图的 range 也传回去
            real_plot_range = (plot_x_min, plot_x_max, plot_y_min, plot_y_max)
            
            self.calculation_finished.emit(face_results, line_data, faces_objects, real_plot_range)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(str(e))
            
# 过滤 toolitems，只保留配置名为 'Save' 的项
class SaveAndPrintToolbar(NavigationToolbar):
    # 1. 过滤默认工具，只保留 'Save'
    toolitems = [t for t in NavigationToolbar.toolitems if t[0] == 'Save']

    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)
        # 3. 手动添加“打印”动作
        self.print_action = QAction(self)
        # 添加图标
        self.print_action.setIcon(FluentIcon.PRINT.icon())
        self.print_action.triggered.connect(self.print_graph)
        self.addAction(self.print_action)

    def print_graph(self):
        """处理打印逻辑"""
        printer = QPrinter(QPrinter.HighResolution)
        # 弹出打印设置对话框
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            # 创建绘图对象，目标是打印机
            painter = QPainter(printer)
            
            # 获取当前 Canvas 的图像 (截图)
            rect = printer.pageRect()
            pixmap = self.canvas.grab() # 抓取画布内容
            
            # --- 计算缩放比例，保持纵横比适应纸张 ---
            size = pixmap.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            
            # 设置视口并绘制
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            
            painter.drawPixmap(0, 0, pixmap)
            painter.end()   

class ModelInterface(Ui_form,GalleryInterface):
    """ Text interface """
    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            parent=parent
        )
        self.setObjectName('modelInterface')
        
        self.setupUi(self.view)
        self.setWidget(self.view)
        self.view.setObjectName('view')
        
        self.faces = []
        self.stateTooltip = None
        # 初始化范围
        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0
        
        self.multiFaceCheckBox.stateChanged.connect(self.onCheckBoxStateChanged)
        self.runButton.clicked.connect(self.onRunButtonClicked)
        self.addNextFaceButton.clicked.connect(self.onAddNextFaceButtonClicked)
        # 标签切换
        self.pivot.currentItemChanged.connect(self.onPivotChanged)
    # 多工作面切换   
    def onCheckBoxStateChanged(self):
        if(self.multiFaceCheckBox.isChecked()):
            self.addNextFaceButton.setVisible(True)
        else:
            self.addNextFaceButton.setVisible(False)
            # 清空工作面数据
            self.faces = []
    
    def onAddNextFaceButtonClicked(self):
        """点击添加下一个工作面时，保存当前数据并清空输入框"""
        isValid, missingField = self.validateInputs(True)
        if isValid:
            if self.saveCurrentFaceData():
                self.createTopAddFaceInfoBar()
                # 清空部分输入框以便输入下一个
                self.faceNameEdit.clear()
                self.x1Edit.clear()
                self.x2Edit.clear()
                self.y1Edit.clear()
                self.y2Edit.clear()
                # 根据需求决定是否清空其他参数
        else:
            self.createTopParamInfoBar(missingField)
    
    # 运行按钮点击事件  
    def onRunButtonClicked(self):
        # 验证当前输入框数据
        isValid, missingField = self.validateInputs()
        if not isValid:
            self.createTopParamInfoBar(missingField)
            return
        
        # 将当前输入框数据加入缓冲区
        if not self.saveCurrentFaceData():
            return
          
        # 准备启动线程数据
        try:
            x1Point = int(self.x1PointEdit.text())
            y1Point = int(self.y1PointEdit.text())
            x2Point = int(self.x2PointEdit.text())
            y2Point = int(self.y2PointEdit.text())
            
            isValid, time_list = self.parse_times_list(self.obsTimeEdit.text())
            
            if not isValid: raise Exception
            
        except:
            self.createTopTypeInfoBar()
            return
        
        start_pos = (x1Point,y1Point)
        end_pos  = (x2Point,y2Point)
        range_data = (self.x_min,self.x_max,self.y_min,self.y_max)
        
        # 显示加载提示
        self.stateTooltip = StateToolTip("正在处理中","请稍候，正在进行复杂的积分运算...",self.window())
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()
        # 禁用运行按钮
        self.runButton.setEnabled(False)
        
        # 启动线程
        self.worker = CalculationWorker(self.faces,start_pos,end_pos,time_list, range_data)
        self.worker.calculation_finished.connect(self.onCalculationFinished)
        self.worker.error_occurred.connect(self.onCalculationError)
        self.worker.start()
    
    # 线程计算完成后的回调
    def onCalculationFinished(self, face_results, line_data, faces_objects, range_data):
        """ 线程计算完成后的回调 """
        
        #  关闭加载提示
        if self.stateTooltip:
            self.stateTooltip.setContent('计算完成！')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        self.runButton.setEnabled(True)

        # 准备 Solver 和 Visualizer 用于绘图
        # 采用 Visualizer 来绘图
        solver = PIMSolver()
        for face in faces_objects:
            solver.add_face(face)
        visualizer = SubsidenceVisualizer(solver)

        # 1. 绘制曲线图 (使用预计算数据)
        x1 = float(self.x1PointEdit.text())
        y1 = float(self.y1PointEdit.text())
        x2 = float(self.x2PointEdit.text())
        y2 = float(self.y2PointEdit.text())
        _, time_list = self.parse_times_list(self.obsTimeEdit.text())
        
        # 调用我们修改后的 plot_time_curves，传入 data
        figCurves = visualizer.plot_profile_time_evolution(
            (x1, y1), (x2, y2), 
            time_list, 
            pre_calculated_data=line_data # 传入线程算好的数据
        )
        curvesCanvas = FigureCanvas(figCurves)
        
        # 添加保存按钮
        curvesToolbar = SaveAndPrintToolbar(curvesCanvas, self.pageContour)
        
        self.clear_layout(self.contourLayout)
        self.contourLayout.addWidget(curvesToolbar)
        self.contourLayout.addWidget(curvesCanvas)

        # 绘制等值线图 
        plot_x_min, plot_x_max, plot_y_min, plot_y_max = range_data
        # 调用plot_2d_contour_and_gob方法
        figGob = visualizer.plot_2d_contour_and_gob(
            (plot_x_min, plot_x_max), 
            (plot_y_min, plot_y_max), 
            pre_calculated_data=face_results
        )
        gobCanvas = FigureCanvas(figGob)
        
        # 实例化自定义工具栏
        gobToolbar = SaveAndPrintToolbar(gobCanvas, self.pageSink)
        
        
        self.clear_layout(self.sinkLayout)
        self.sinkLayout.addWidget(gobToolbar)
        self.sinkLayout.addWidget(gobCanvas)

        # 保存历史记录
        self.save_history_record(figCurves, figGob,faces_objects)
        
        # 清理数据，准备下一次
        self.faces = []
        # if not self.multiFaceCheckBox.isChecked():
        #     self.faces = [] # 如果不是多工作面模式，用完即清
    
    # 计算错误提示
    def onCalculationError(self, error_msg):
        if self.stateTooltip:
            self.stateTooltip.setContent('处理出错')
            self.stateTooltip.setState(False) # 显示红色错误
            self.stateTooltip = None
        self.runButton.setEnabled(True)
        InfoBar.error("计算错误", str(error_msg), parent=self)
    
    # 验证页面输入框是否为空   
    def validateInputs(self,addFace=False):
        """ 验证输入框是否为空 """
        # 获取所有输入框
        if addFace:
            inputs = [
                ("工作面名称", self.faceNameEdit),
                ("走向起点 X1", self.x1Edit),
                ("走向终点 X2", self.x2Edit),
                ("倾向起点 Y1", self.y1Edit),
                ("倾向起点 Y2", self.y2Edit),
                ("采深 H", self.hEdit),
                ("采厚 m", self.mEdit),
                ("煤层倾角 α", self.alphaEdit),
                ("下沉系数 q", self.qEdit),
                ("主要影响角正切 tanβ", self.tanBetaEdit),
            ]
        else:
            inputs = [
                ("工作面名称", self.faceNameEdit),
                ("走向起点 X1", self.x1Edit),
                ("走向终点 X2", self.x2Edit),
                ("倾向起点 Y1", self.y1Edit),
                ("倾向起点 Y2", self.y2Edit),
                ("采深 H", self.hEdit),
                ("采厚 m", self.mEdit),
                ("煤层倾角 α", self.alphaEdit),
                ("下沉系数 q", self.qEdit),
                ("主要影响角正切 tanβ", self.tanBetaEdit),
                ("观测线起点坐标 X",self.x1PointEdit),
                ("观测点起点坐标 Y",self.y1PointEdit),
                ("观测点终点坐标 X",self.x2PointEdit),
                ("观测点终点坐标 Y",self.y2PointEdit)
            ]
        # 检查空值
        for label, value in inputs:
            if not value.text().strip():  # 去除空格后检查
                return False, label  # 返回缺失的字段
        return True, None
    
    # 创建顶部参数错误框
    def createTopParamInfoBar(self,missingField):
        InfoBar.error(
            title="错误",
            content=f"参数不完整,请填写缺失的参数: {missingField} ！",
            orient=Qt.Horizontal,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    # 数据格式错误弹框   
    def createTopTypeInfoBar(self):
        InfoBar.error(
            title="错误",
            content="输入格式错误，请输入正确的数值！",
            orient=Qt.Horizontal,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    # 顶部新增工作面成功
    def createTopAddFaceInfoBar(self):
        InfoBar.success(
            title="成功",
            content="工作面数据已添加！请继续输入。",
            orient=Qt.Horizontal,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        ) 
    
    # 验证观测时间序列正确处理
    def parse_times_list(self,time_list):
        default_list = [3, 6, 12, 24, 36]
        # 1. 空输入处理: 使用默认值
        stripped = time_list.strip()
        if not stripped:
            return True, sorted(set(default_list))
        
        # 2. 分割与基础验证
        parts = stripped.split()
        if not parts:
            return True, sorted(set(default_list))
        
        # 3. 类型转换与数值验证
        valid_numbers = []
        for i, part in enumerate(parts, 1):
            # 检查是否为纯数字（拒绝小数、负数、科学计数法等）
            if not part.isdigit():
                return False, default_list
            
            num = int(part)
            if num <= 0:
                return False, default_list
            
            valid_numbers.append(num)
    
        # 4. 去重 + 升序排序
        result = sorted(set(valid_numbers))
        
        # 5. 空结果保护（理论上不会触发）
        if not result:
            return True, sorted(set(default_list))
        
        return True, result
    
    
    def saveCurrentFaceData(self):
        """ 读取界面输入并存入 self.faces """
        try:
            name = self.faceNameEdit.text()
            x_start = float(self.x1Edit.text())
            x_end = float(self.x2Edit.text())
            y_start = float(self.y1Edit.text())
            y_end = float(self.y2Edit.text())
            H = float(self.hEdit.text())
            m = float(self.mEdit.text())
            alpha = float(self.alphaEdit.text())
            q = float(self.qEdit.text())
            tan_beta = float(self.tanBetaEdit.text())
            
            
            # 添加其他参数
            songSan = self.songSanEdit.text().strip() or 0 
            
            baseThickness = self.baseThicknessEdit.text().strip() or 0 
            baseYieldStrength = self.baseYieldStrengthEdit.text().strip() or 0 
            frictionAngle = self.frictionAngleEdit.text().strip() or 0 
            keyLayerPosition = self.keyLayerPositionEdit.text().strip() or 0 
            
            horizontalMovement = self.horizontalMovementEdit.text().strip() or 0
            
            otherParameters = (songSan, baseThickness, baseYieldStrength, frictionAngle, keyLayerPosition, horizontalMovement)
            # 更新全局范围
            if not self.faces:
                self.x_min, self.x_max = min(x_start, x_end), max(x_start, x_end)
                self.y_min, self.y_max = min(y_start, y_end), max(y_start, y_end)
            else:
                self.x_min = min(self.x_min, x_start, x_end)
                self.x_max = max(self.x_max, x_start, x_end)
                self.y_min = min(self.y_min, y_start, y_end)
                self.y_max = max(self.y_max, y_start, y_end)

            # 保存元组数据 (以便传入线程)
            face_tuple = (name, (x_start, x_end), (y_start, y_end), H, m, alpha, q, tan_beta ,otherParameters)
            self.faces.append(face_tuple)
            return True
        except ValueError:
            self.createTopTypeInfoBar()
            return False
        
    # 标签切换
    def onPivotChanged(self, routeKey):
        if routeKey == "contourPage":
            self.stackedWidget.setCurrentIndex(0)
        elif routeKey == "sinkPage":
            self.stackedWidget.setCurrentIndex(1)
         
    # 清空布局
    def clear_layout(self, layout):
        """
        清理布局中的所有控件
        用于在重新绘图前移除旧的 Canvas 或占位 Label
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
    
    # 保存历史记录
    def save_history_record(self, fig_curve, fig_gob, faces_objects):
        """ 
        保存当前记录到本地 
        :param faces_objects: 参与计算的工作面对象列表
        """
        try:
            # 1. 创建基础目录
            base_dir = "saved_history"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            
            # 2. 创建当前记录的子目录
            current_time = datetime.datetime.now()
            timestamp = current_time.strftime("%Y%m%d_%H%M%S")
            record_dir = os.path.join(base_dir, f"Record_{timestamp}")
            os.makedirs(record_dir)
            
            # 3. 收集参数 (支持多工作面)
            # 这里的 face 对象属性名取决于你的 WorkingFace 类定义
            # 假设 WorkingFace 类中有对应的属性存储了初始化参数
            faces_data = []
            for face in faces_objects:
                face_info = {
                    "name": getattr(face, 'id', '未命名'), # 假设属性名为 name
                    # 如果你的对象属性名不同，请根据 algorithm.py 实际情况修改
                    "x_range": [face.x_start, face.x_end],
                    "y_range": [face.y_start, face.y_end],
                    "params": {
                        "H": getattr(face, 'H', 0),
                        "m": getattr(face, 'm', 0),
                        "alpha": getattr(face, 'alpha_degree', 0),
                        "q": getattr(face, 'q', 0),
                        "tan_beta": getattr(face, 'tan_beta', 0),
                        "songSan": getattr(face, 'songSan', 0),
                        "baseThickness": getattr(face, 'baseThickness', 0),
                        "baseYieldStrength": getattr(face, 'baseYieldStrength', 0),
                        "frictionAngle": getattr(face, 'frictionAngle', 0),
                        "keyLayerPosition": getattr(face, 'keyLayerPosition', 0),
                        "horizontalMovement": getattr(face, 'horizontalMovement', 0)
                    }
                }
                faces_data.append(face_info)

            params = {
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "face_count": len(faces_objects),
                "faces": faces_data, # 保存列表
                "obs_line": {
                    "start": f"({self.x1PointEdit.text()}, {self.y1PointEdit.text()})",
                    "end": f"({self.x2PointEdit.text()}, {self.y2PointEdit.text()})"
                }
            }
            
            # 4. 保存 JSON
            json_path = os.path.join(record_dir, "info.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(params, f, ensure_ascii=False, indent=4)
                
            # 5. 保存图片
            fig_curve.savefig(os.path.join(record_dir, "curve.png"), dpi=100, bbox_inches='tight')
            fig_gob.savefig(os.path.join(record_dir, "contour.png"), dpi=100, bbox_inches='tight')
            
        except Exception as e:
            print(f"Error saving history: {e}")
            import traceback
            traceback.print_exc()        
            
        
        
