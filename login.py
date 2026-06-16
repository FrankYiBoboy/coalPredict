import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTranslator, pyqtSignal, QSettings
from qframelesswindow import FramelessWindow, StandardTitleBar
from qfluentwidgets import setThemeColor, FluentTranslator, InfoBar, InfoBarIcon, InfoBarPosition, FluentIcon, MessageBox
from PyQt5.QtGui import QIcon, QPainter, QPixmap

from app.common.config import cfg
from app.common.session import SessionManager
from app.view.main_window import MainWindow
from app.view.Ui_LoginWindow import Ui_Login
from app.common.auth import AuthManager

import app.common.resource


class loginWindow(FramelessWindow, Ui_Login):
    # 定义信号
    login_success_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 更改主题色
        setThemeColor("#28afe9")

        # 设置标题栏
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()

        # 设置窗口图标
        self.setWindowIcon(QIcon(":/gallery/images/Logo.png"))
        self.setWindowTitle("煤矿开采覆岩运移预测软件")
        # self.resize(1000, 650)

        # 窗口居中
        rect = QApplication.desktop().availableGeometry()
        w, h = rect.width(), rect.height()
        self.move(w//2-self.width()//2, h//2-self.height()//2)
        self.setStyleSheet("LoginWindow{background: rgba(242, 242, 242, 0.8)}")

        # 调整样式
        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 14px 'Segoe UI';
                padding: 0 5px;
                color: white
            }
        """)
        # 登录界面
        self.fondButton.clicked.connect(self.createFondInfoBar)
        self.regButton.clicked.connect(self.createRegistInfoBar)
        self.loginButton.clicked.connect(self.loginClicked)

        # 读取配置并预填充页面
        self.settings = QSettings("CoalPredict_Org", "CoalPredictApp")
        saved_user = self.settings.value("remember_user")
        saved_token = self.settings.value("remember_token")
        
        if saved_user and saved_token:
            # 如果存在本地保存的记录，填充用户名
            self.userEdit.setText(saved_user)
            # 填充 8 个星号作为视觉伪装，无需填写真实密码
            self.passwordEdit.setText("********")
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)
            
            
    # 设置找回密码弹窗
    def createFondInfoBar(self):
        content = "密码丢失请联系管理员,暂不支持在线修改。"
        fond = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title='警告',
            content=content,
            orient=Qt.Vertical,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        fond.show()

    # 注册账号弹窗
    def createRegistInfoBar(self):
        content = "本软件为局域网软件,如需添加账户,请联系管理员更新用户数据库。"
        regist = InfoBar.new(
            icon=FluentIcon.MESSAGE,
            title='温馨提示',
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=2000,
            parent=self
        )
        regist.setCustomBackgroundColor('white', '#202020')
    
    # 用户名或密码错误弹窗
    def creatErrorBar(self):
        content = "如果您的密码丢失或遗忘,请联系管理员处理。"
        error = InfoBar(
            icon=InfoBarIcon.ERROR,
            title='您输入的用户名或密码不正确',
            content=content,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        error.show()

    # 登录按钮slot
    def loginClicked(self):
        user = self.userEdit.text()
        password = self.passwordEdit.text()

        # 校验输入是否为空
        if not user or not password:
            self.creatErrorBar() # 或者你可以专门写一个提示“请输入完整”的 InfoBar
            return
        
        # 调用脚本验证用户名密码
        # is_valid = AuthManager.verify_login(user, password)
        # 分支验证
        is_valid = False
        if password == "********":
            # 用户没有修改密码框，使用的是“记住密码”的 Token 凭证
            saved_token = self.settings.value("remember_token")
            # 调用 AuthManager 的 Token 校验方法
            is_valid = AuthManager.verify_auto_login_token(user, saved_token)
        else:
            # 密码不是占位符，说明用户手动输入了新密码
            # 走正常的密码 Hash 校验流程
            is_valid = AuthManager.verify_login(user, password)
         
        # 用户名密码正确关闭登录界面切换到主页
        if is_valid:
            # 拦截写入全局状态
            SessionManager.set_current_user(user)
            # 处理记住密码逻辑
            if self.checkBox.isChecked():
                # 只有在手动输入真实密码时，才需要重新生成 Token 并保存
                if password != "********":
                    raw_token = AuthManager.create_auto_login_token(user)
                    self.settings.setValue("remember_user", user)
                    self.settings.setValue("remember_token", raw_token)
                pass
            else:
                # 如果用户没有勾选，则清除之前可能存在的本地配置
                self.settings.remove("remember_user")
                self.settings.remove("remember_token")
            
            # 发送登录成功信号
            self.login_success_signal.emit()
            self.close()
        else:
            self.creatErrorBar()

if __name__ == '__main__':
    
    # 启动自检用户
    AuthManager.init_system()
    
    if cfg.get(cfg.dpiScale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    # 添加翻译 面向国际化
    locale = cfg.get(cfg.language).value
    translator = FluentTranslator(locale)
    galleryTranslator = QTranslator()
    galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")

    app.installTranslator(translator)
    app.installTranslator(galleryTranslator)
    # 显示界面
    main_window = None
    # 定义登录成功槽函数
    def on_login_success():
        global main_window
        main_window = MainWindow()
        main_window.show()
    # 实例化并显示登录窗口
    w = loginWindow()
    w.login_success_signal.connect(on_login_success)
    w.show()
    app.exec_()
