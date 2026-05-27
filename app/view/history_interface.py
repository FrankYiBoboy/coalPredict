# coding:utf-8
import os
import json
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap, QColor, QCursor,QDesktopServices
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                             QFrame, QScrollArea, QDialog, QGraphicsOpacityEffect)
from qfluentwidgets import (CardWidget, StrongBodyLabel, BodyLabel, 
                            CaptionLabel, SubtitleLabel, FluentIcon)

from .gallery_interface import GalleryInterface
from app.common.session import SessionManager

# ==========================================
# 可点击的图片标签
# ==========================================
class ClickableImageLabel(QWidget):
    """ 封装一个可点击的图片显示控件 """
    clicked = pyqtSignal(str) # 发送图片路径

    def __init__(self, img_path, title, parent=None):
        super().__init__(parent)
        self.img_path = img_path
        self.initUI(title)
        self.setCursor(QCursor(Qt.PointingHandCursor)) # 鼠标变手型

    def initUI(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        # 图片区域
        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("""
            QLabel {
                border: 1px solid #e0e0e0; 
                border-radius: 6px; 
                background: white;
                padding: 4px;
            }
            QLabel:hover {
                border: 1px solid #009faa; /* 悬停变色 */
            }
        """)
        
        if os.path.exists(self.img_path):
            pixmap = QPixmap(self.img_path)
            # 缩略图高度固定
            self.lbl.setPixmap(pixmap.scaledToHeight(140, Qt.SmoothTransformation))
        else:
            self.lbl.setText("图片丢失")
            
        caption = CaptionLabel(title)
        caption.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.lbl)
        layout.addWidget(caption)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.img_path)
        super().mousePressEvent(event)

# ==========================================
# 3. 更新：HistoryCard 支持多数据和弹窗
# ==========================================
class HistoryCard(CardWidget):
    def __init__(self, record_path, parent=None):
        super().__init__(parent)
        self.record_path = record_path
        self.initUI()

    def initUI(self):
        # 读取 JSON
        json_path = os.path.join(self.record_path, "info.json")
        data = {}
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

        self.vLayout = QVBoxLayout(self)
        self.vLayout.setSpacing(12)
        self.vLayout.setContentsMargins(24, 24, 24, 24)

        # --- 1. 头部信息 ---
        headerLayout = QHBoxLayout()
        time_str = data.get("timestamp", "Unknown Time")
        face_count = data.get("face_count", 0)
        faces_list = data.get("faces", [])
        obs_line = data.get("obs_line", {})
        
        # 构建标题文本
        if faces_list:
            face_names = [f["name"] for f in faces_list]
            if face_count > 3:
                name_str = f"工作面: {', '.join(face_names[:3])} 等{len(face_names)}个"
            else:
                name_str = f"工作面: {', '.join(face_names)}"
        else:
            # 兼容旧格式 TODO 最后删除
            name_str = f"工作面: {data.get('face_name', '未命名')}"

        timeLabel = StrongBodyLabel(f"{time_str}", self)
        nameLabel = BodyLabel(name_str, self)
        
        headerLayout.addWidget(timeLabel)
        headerLayout.addStretch(1)
        headerLayout.addWidget(nameLabel)
        self.vLayout.addLayout(headerLayout)

        # --- 2. 参数详情 ---
        paramWidget = QWidget()
        paramLayout = QVBoxLayout(paramWidget)
        paramLayout.setContentsMargins(0,0,0,0)
        paramLayout.setSpacing(4)
        
        if faces_list:
            for i, face in enumerate(faces_list[:2]):
                p = face.get("params", {})
                info_text = (f"[{face['name']}] 采深H:{p.get('H')}m | 采厚M:{p.get('m')}m | "
                             f"倾角α:{p.get('alpha')}° | 松散层厚度:{p.get('songSan')}m | "
                             f"基岩厚度:{p.get('baseThickness')}m | 基岩抗压强度:{p.get('baseYieldStrength')}MPa | "
                             f"基岩层内摩擦角:{p.get('frictionAngle')}° | 关键层位置:{p.get('keyLayerPosition')}m | "
                             f"下沉系数q:{p.get('q')} | 影响角正切tanβ:{p.get('tan_beta')} | "
                             f"水平移动系数:{p.get('horizontalMovement')}"
                            )
                lbl = CaptionLabel(info_text, self)
                lbl.setTextColor(QColor(100, 100, 100), QColor(150, 150, 150))
                paramLayout.addWidget(lbl)
            
            if face_count > 2:
                more_lbl = CaptionLabel(f"...以及其他 {face_count-2} 个工作面", self)
                more_lbl.setTextColor(QColor(150, 150, 150), QColor(180, 180, 180))
                paramLayout.addWidget(more_lbl)
            # 观测线信息
            if obs_line:
                obs_text = (f"观测线: 观测线起点: {obs_line.get('start')} | 观测线终点: {obs_line.get('end')}")
                line_lbl = CaptionLabel(obs_text, self)
                line_lbl.setTextColor(QColor(110, 110, 110), QColor(120, 120, 120))
                paramLayout.addWidget(line_lbl)
                
        else:
            inputs = data.get("inputs", {})
            param_text = (f"采深(H): {inputs.get('H')}m | 采厚(m): {inputs.get('m')}m | "
                          f"倾角: {inputs.get('alpha')}°")
            lbl = CaptionLabel(param_text, self)
            lbl.setTextColor(QColor(100, 100, 100), QColor(150, 150, 150))
            paramLayout.addWidget(lbl)
            
        self.vLayout.addWidget(paramWidget)

        # --- 3. 分割线 ---
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0;")
        line.setFixedHeight(1)
        self.vLayout.addWidget(line)

        # --- 4. 图片区域 ---
        imgLayout = QHBoxLayout()
        curve_path = os.path.join(self.record_path, "curve.png")
        contour_path = os.path.join(self.record_path, "contour.png")
        
        # 提示文字改为“点击打开”
        self.img1 = ClickableImageLabel(curve_path, "下沉等值线图 (点击打开)", self)
        self.img2 = ClickableImageLabel(contour_path, "沉陷图 (点击打开)", self)
        
        # 绑定点击事件到新的处理函数
        self.img1.clicked.connect(self.openImageInSystem)
        self.img2.clicked.connect(self.openImageInSystem)
        
        imgLayout.addWidget(self.img1)
        imgLayout.addWidget(self.img2)
        self.vLayout.addLayout(imgLayout)

    def openImageInSystem(self, img_path):
        """ 使用系统默认程序打开图片 """
        if os.path.exists(img_path):
            # 获取绝对路径，确保系统能找到文件
            abs_path = os.path.abspath(img_path)
            # 使用 QUrl.fromLocalFile 转换路径
            url = QUrl.fromLocalFile(abs_path)
            # 调用系统服务打开 URL
            QDesktopServices.openUrl(url)


class HistoryInterface(GalleryInterface):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('historyInterface')
        
        self.mainViewLayout = QVBoxLayout(self.view)
        self.mainViewLayout.setSpacing(30)
        
        self.mainViewLayout.addSpacing(30)
        #  添加标题标签
        self.titleLabel = SubtitleLabel("历史记录", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.mainViewLayout.addWidget(self.titleLabel)
        
        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollLayout.setSpacing(20)
        self.scrollLayout.setContentsMargins(10, 0, 0, 0)

        self.mainViewLayout.addLayout(self.scrollLayout)
        self.mainViewLayout.addStretch(1)
        self.setWidget(self.view)
        self.loadHistory()

    def showEvent(self, event):
        self.loadHistory()
        super().showEvent(event)

    def loadHistory(self):
        self.clearLayout(self.scrollLayout)
        
        # base_dir = "saved_history"
        # 获取当前用户目录
        base_dir = SessionManager.get_user_history_path()
        if not os.path.exists(base_dir):
            self.showEmptyState()
            return

        dirs = [d for d in os.listdir(base_dir) if d.startswith("Record_")]
        dirs.sort(reverse=True)

        if not dirs:
            self.showEmptyState()
            return

        for d in dirs:
            full_path = os.path.join(base_dir, d)
            card = HistoryCard(full_path, self.view)
            self.scrollLayout.addWidget(card)

    def showEmptyState(self):
        lbl = BodyLabel("暂无历史记录", self)
        lbl.setAlignment(Qt.AlignCenter)
        self.scrollLayout.addWidget(lbl)

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()