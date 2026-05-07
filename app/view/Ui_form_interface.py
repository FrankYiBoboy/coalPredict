from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import (CardWidget, IconWidget, StrongBodyLabel, BodyLabel, 
                            TransparentToolButton, LineEdit, CheckBox, PushButton, 
                            PrimaryPushButton, FluentIcon,SubtitleLabel,ScrollArea,Pivot)
from PyQt5.QtCore import Qt

class Ui_form(object):
    def setupUi(self, FormInterface):
        # ==========================================================
        #  数据输入卡片 (Data Input Card)
        # ==========================================================
        FormInterface.setObjectName("FormInterface")
        
        # self.horizontalLayout = QtWidgets.QVBoxLayout(FormInterface)
        # self.horizontalLayout.setObjectName("horizontalLayout")
        
        # self.gridLayout = QtWidgets.QGridLayout()
        # self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        # self.gridLayout.setContentsMargins(20, 40, 20, 20)
        # self.gridLayout.setSpacing(12)
        # self.gridLayout.setObjectName("gridLayout")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(FormInterface)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(20, 30, 20, 20)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout") 
        
        self.dataInputCard = CardWidget(FormInterface)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataInputCard.sizePolicy().hasHeightForWidth())
        self.dataInputCard.setSizePolicy(sizePolicy)
        self.dataInputCard.setStyleSheet("")
        self.dataInputCard.setObjectName("dataInputCard")
        
        # 布局：主垂直布局
        self.vLayoutInput = QtWidgets.QVBoxLayout(self.dataInputCard)
        self.vLayoutInput.setSpacing(10)
        self.vLayoutInput.setContentsMargins(20, 20, 20, 20)

        # --- 1. 卡片标题栏 ---
        self.headerLayout = QtWidgets.QHBoxLayout()
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        
        # 图标
        self.inputIcon = IconWidget(self.dataInputCard)
        self.inputIcon.setFixedSize(20, 20)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(':/gallery/images/input.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.inputIcon.setIcon(icon1)
        self.inputIcon.setObjectName("inputIcon")
        
        
        self.inputTitleLabel = StrongBodyLabel("数据输入", self.dataInputCard)
        
        self.headerLayout.addWidget(self.inputIcon)
        self.headerLayout.addWidget(self.inputTitleLabel)
        self.headerLayout.addStretch(1) # 弹簧，把标题顶在左边
        self.vLayoutInput.addLayout(self.headerLayout)

        # 分割线或间距
        self.vLayoutInput.addSpacing(8)

        # --- 2. 中间文本：采矿参数 ---
        self.paramLabel = SubtitleLabel("采矿参数", self.dataInputCard)
        self.paramLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.vLayoutInput.addWidget(self.paramLabel)

        # --- 3. 第一行：工作面名称 (1个输入框) ---
        self.row1Layout = QtWidgets.QHBoxLayout()
        self.row1Layout.setSpacing(15)
        
        # 封装一个简易函数来创建带标签的输入框结构 (垂直排列：标签在上，输入框在下)
        def create_input_field(parent, label_text, placeholder=""):
            container = QtWidgets.QVBoxLayout()
            container.setSpacing(5)
            label = BodyLabel(label_text, parent)
            line_edit = LineEdit(parent)
            line_edit.setPlaceholderText(placeholder)
            line_edit.setClearButtonEnabled(True)
            container.addWidget(label)
            container.addWidget(line_edit)
            return container, line_edit
        
        # 创建工作面名称
        self.faceNameLayout, self.faceNameEdit = create_input_field(self.dataInputCard, "工作面名称", "例如: Face 1")
        self.row1Layout.addLayout(self.faceNameLayout)
        self.vLayoutInput.addLayout(self.row1Layout)

        # --- 4. 第二行：走向 X1, X2 (2个输入框) ---
        self.row2Layout = QtWidgets.QHBoxLayout()
        self.row2Layout.setSpacing(15)
        
        self.x1Layout, self.x1Edit = create_input_field(self.dataInputCard, "走向起点 X1 (m)","工作面走向起点")
        self.x2Layout, self.x2Edit = create_input_field(self.dataInputCard, "走向终点 X2 (m)","工作面走向终点")
        
        self.row2Layout.addLayout(self.x1Layout)
        self.row2Layout.addLayout(self.x2Layout)
        self.vLayoutInput.addLayout(self.row2Layout)

        # --- 5. 第三行：倾向 Y1, Y2 (2个输入框) ---
        self.row3Layout = QtWidgets.QHBoxLayout()
        self.row3Layout.setSpacing(15)
        
        self.y1Layout, self.y1Edit = create_input_field(self.dataInputCard, "倾向起点 Y1 (m)","工作面倾向起点") 
        self.y2Layout, self.y2Edit = create_input_field(self.dataInputCard, "倾向终点 Y2 (m)","工作面倾向终点")
        
        self.row3Layout.addLayout(self.y1Layout)
        self.row3Layout.addLayout(self.y2Layout)
        self.vLayoutInput.addLayout(self.row3Layout)

        # --- 6. 第四行：采深 H, 采厚 m, 倾角 α 松散度厚度(4个输入框) ---
        self.row4Layout = QtWidgets.QHBoxLayout()
        self.row4Layout.setSpacing(15)
        
        self.hLayout, self.hEdit = create_input_field(self.dataInputCard, "采深 H (m)")
        self.mLayout, self.mEdit = create_input_field(self.dataInputCard, "采厚 M (m)")
        self.alphaLayout, self.alphaEdit = create_input_field(self.dataInputCard, "煤层倾角 α (度)")
        self.songSanLayout, self.songSanEdit = create_input_field(self.dataInputCard, "松散层厚度 (m)")
        
        self.row4Layout.addLayout(self.hLayout)
        self.row4Layout.addLayout(self.mLayout)
        self.row4Layout.addLayout(self.alphaLayout)
        self.row4Layout.addLayout(self.songSanLayout)
        self.vLayoutInput.addLayout(self.row4Layout)
        
        # --- 6.5. 第四点五行：基岩厚度、基岩抗压强度、松散层内摩擦角、关键层位置(4个输入框) (输入框只显示不做后续运算处理) ---
        self.row4_1Layout = QtWidgets.QHBoxLayout()
        self.row4_1Layout.setSpacing(15)
        self.baseThicknessLayout, self.baseThicknessEdit = create_input_field(self.dataInputCard, "基岩厚度 (m)")
        self.baseYieldStrengthLayout, self.baseYieldStrengthEdit = create_input_field(self.dataInputCard, "基岩抗压强度 (MPa)")
        self.frictionAngleLayout, self.frictionAngleEdit = create_input_field(self.dataInputCard, "基岩层内摩擦角 (度)")
        self.keyLayerPositionLayout, self.keyLayerPositionEdit = create_input_field(self.dataInputCard, "关键层位置 (m)")
        
        self.row4_1Layout.addLayout(self.baseThicknessLayout)
        self.row4_1Layout.addLayout(self.baseYieldStrengthLayout)
        self.row4_1Layout.addLayout(self.frictionAngleLayout)
        self.row4_1Layout.addLayout(self.keyLayerPositionLayout)
        self.vLayoutInput.addLayout(self.row4_1Layout)
        

        # --- 7. 第五行：下沉系数 q, tanβ, 水平移动系数 (3个输入框) ---
        self.row5Layout = QtWidgets.QHBoxLayout()
        self.row5Layout.setSpacing(15)
        
        self.qLayout, self.qEdit = create_input_field(self.dataInputCard, "下沉系数 q (0-1)")
        self.tanBetaLayout, self.tanBetaEdit = create_input_field(self.dataInputCard, "主要影响角正切 tanβ")
        self.horizontalMovementLayout, self.horizontalMovementEdit = create_input_field(self.dataInputCard, "水平移动系数(b) (0-1)")
        
        
        self.row5Layout.addLayout(self.qLayout)
        self.row5Layout.addLayout(self.tanBetaLayout)
        self.row5Layout.addLayout(self.horizontalMovementLayout)
        self.row5Layout.addSpacing(10)
        self.row5Layout.addStretch()
        self.vLayoutInput.addLayout(self.row5Layout)

        self.vLayoutInput.addSpacing(10)

        # --- 8. 双态复选框：添加多个工作面 ---
        self.multiFaceCheckBox = CheckBox("添加多个工作面", self.dataInputCard)
        self.vLayoutInput.addWidget(self.multiFaceCheckBox)

        # --- 9. 条件按钮：添加下一个工作面 ---
        self.addNextFaceButton = PushButton("点击添加下一个工作面", self.dataInputCard)
        self.addNextFaceButton.setIcon(FluentIcon.ADD)
        self.addNextFaceButton.setMinimumWidth(200)
        self.addNextFaceButton.setVisible(False)  # 默认隐藏
        self.vLayoutInput.addWidget(self.addNextFaceButton, 0, QtCore.Qt.AlignLeft)
        self.vLayoutInput.addSpacing(10)

        # 9.2 添加观测线起点坐标
        self.rowObsPointXLayout = QtWidgets.QHBoxLayout()
        self.rowObsPointXLayout.setSpacing(15)
        self.x1PointLayout, self.x1PointEdit = create_input_field(self.dataInputCard, "观测线起点坐标 X")
        self.x1PointEdit.setFixedWidth(200)
        self.y1PointLayout, self.y1PointEdit = create_input_field(self.dataInputCard, "观测线起点坐标 Y")
        self.y1PointEdit.setFixedWidth(200)
        self.rowObsPointXLayout.addLayout(self.x1PointLayout)
        self.rowObsPointXLayout.addLayout(self.y1PointLayout)
        self.rowObsPointXLayout.addStretch()
        self.vLayoutInput.addLayout(self.rowObsPointXLayout)
        self.vLayoutInput.addSpacing(10)
        
        # 9.3 添加观测线终点坐标
        self.rowObsPointYLayout = QtWidgets.QHBoxLayout()
        self.rowObsPointYLayout.setSpacing(15)
        self.x2PointLayout, self.x2PointEdit = create_input_field(self.dataInputCard, "观测线终点坐标 X")
        self.x2PointEdit.setFixedWidth(200)
        self.y2PointLayout, self.y2PointEdit = create_input_field(self.dataInputCard, "观测线终点坐标 Y")
        self.y2PointEdit.setFixedWidth(200)
        self.rowObsPointYLayout.addLayout(self.x2PointLayout)
        self.rowObsPointYLayout.addLayout(self.y2PointLayout)
        self.rowObsPointYLayout.addStretch()
        self.vLayoutInput.addLayout(self.rowObsPointYLayout)
        self.vLayoutInput.addSpacing(10)
        
        # 9.4 添加观测时间序列
        self.rowObsTimeLayout = QtWidgets.QHBoxLayout()
        self.rowObsTimeLayout.setSpacing(15)
        self.obsTimeLayout, self.obsTimeEdit = create_input_field(self.dataInputCard, "观测时间序列(月)   默认序列为[3 6 12 24 36]   (数据之间空格分隔)")
        self.obsTimeEdit.setFixedWidth(500)
        self.rowObsTimeLayout.addLayout(self.obsTimeLayout)
        self.rowObsTimeLayout.addStretch()
        self.vLayoutInput.addLayout(self.rowObsTimeLayout) 
        self.vLayoutInput.addSpacing(10)
        
        
        
        # --- 10. 运行按钮 ---
        self.rowRunButtonLayout = QtWidgets.QHBoxLayout()
        self.runButton = PrimaryPushButton("运行", self.dataInputCard)
        self.runButton.setIcon(FluentIcon.SEND)
        self.runButton.setMinimumWidth(150)
        self.rowRunButtonLayout.addStretch()
        self.rowRunButtonLayout.addWidget(self.runButton)
        self.rowRunButtonLayout.addStretch()
        self.vLayoutInput.addLayout(self.rowRunButtonLayout)
        

        # --- 将卡片添加到 Grid Layout ---
        # 关键点：rowSpan=1, colSpan=2 (或更多)
        # 参数依次为: widget, row, column, rowSpan, colSpan
        # self.gridLayout.addWidget(self.dataInputCard, 0, 1)
        
        #TODO 采用垂直布局 暂时不用栅格布局
        self.verticalLayout.addWidget(self.dataInputCard)
        self.verticalLayout.addStretch()
        # spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.verticalLayout.addItem(spacerItem)
        
        # 显示预测图
        
        self.viewAreaCard = CardWidget(FormInterface)
        self.viewAreaCard.setSizePolicy(sizePolicy)
        self.viewAreaCard.setObjectName("viewAreaCard")
        
        self.vLayoutView = QtWidgets.QVBoxLayout(self.viewAreaCard)
        self.vLayoutView.setContentsMargins(20, 20, 20, 20)
        self.vLayoutView.setSpacing(10)
        
        # 1. 创建标签栏 (Pivot)
        self.pivot = Pivot(self.viewAreaCard)
        self.pivot.addItem(routeKey="contourPage", text="下沉等值线图")
        self.pivot.addItem(routeKey="sinkPage", text="三维下沉图")
        self.pivot.setObjectName("pivot")
        
        # 将 Pivot 添加到布局，并居中或居左显示
        self.vLayoutView.addWidget(self.pivot, 0, QtCore.Qt.AlignCenter)
        
        # 2. 创建堆叠窗口 (StackedWidget) 用于存放不同的图表
        self.stackedWidget = QtWidgets.QStackedWidget(self.viewAreaCard)
        self.stackedWidget.setObjectName("stackedWidget")
        
        # --- 页面 1：等值线图容器 ---
        self.pageContour = QtWidgets.QWidget()
        self.pageContour.setObjectName("pageContour")
        self.contourLayout = QtWidgets.QVBoxLayout(self.pageContour)
        self.contourLayout.setContentsMargins(0, 10, 0, 0)
        # 这里你可以添加一个临时的 Label 占位，或者留空等待 Matplotlib 填入
        self.labelPlaceholder1 = BodyLabel("请点击运行以生成等值线图", self.pageContour)
        self.labelPlaceholder1.setAlignment(Qt.AlignCenter)
        self.contourLayout.addWidget(self.labelPlaceholder1)
        self.stackedWidget.addWidget(self.pageContour)
        
        # --- 页面 2：3D图容器 ---
        self.pageSink = QtWidgets.QWidget()
        self.pageSink.setObjectName("pageSink")
        self.sinkLayout = QtWidgets.QVBoxLayout(self.pageSink)
        self.sinkLayout.setContentsMargins(0, 10, 0, 0)
        self.labelPlaceholder2 = BodyLabel("请点击运行以生成下沉图", self.pageSink)
        self.labelPlaceholder2.setAlignment(Qt.AlignCenter)
        self.sinkLayout.addWidget(self.labelPlaceholder2)
        self.stackedWidget.addWidget(self.pageSink)
        
        # 将堆叠窗口添加到结果卡片布局中
        self.vLayoutView.addWidget(self.stackedWidget)
        
        # 关联 Pivot 和 StackedWidget (通过信号槽，在 UI 文件里可以简单关联索引)
        # 注意：在逻辑代码中通常需要: self.pivot.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentIndex(0 if k == "contourPage" else 1))
        # 此时默认显示第一页
        self.stackedWidget.setCurrentIndex(0)
        self.pivot.setCurrentItem("contourPage")
        
        self.verticalLayout.addWidget(self.viewAreaCard)
        
        