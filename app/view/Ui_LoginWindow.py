from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import CheckBox, LineEdit, PrimaryPushButton, HyperlinkButton, TitleLabel,Action, FluentIcon

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(1160, 780)
        Login.setMinimumSize(QtCore.QSize(700, 500))
        self.horizontalLayout = QtWidgets.QHBoxLayout(Login)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Login)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/gallery/images/login_background.jpg"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        
        # 右侧表单容器
        self.widget = QtWidgets.QWidget(Login)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(360, 0))
        self.widget.setMaximumSize(QtCore.QSize(360, 16777215))
        self.widget.setObjectName("widget")
        
        self.widget.setStyleSheet("""
            QWidget#widget {
                background-color: rgba(255, 255, 255, 160); 
                border-left: 1.5px solid rgba(255, 255, 255, 220); 
                border-top-left-radius: 20px; 
                border-bottom-left-radius: 20px;
            }
        """)
        
        # 右侧垂直布局
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(35, 20, 35, 20)
        self.verticalLayout_2.setSpacing(15)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        # 顶部弹簧
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        
        # logo
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(90, 90))
        self.label_2.setMaximumSize(QtCore.QSize(90, 90))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/gallery/images/Logo.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2, 0, QtCore.Qt.AlignHCenter)
        
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        
        # 欢迎标题
        self.welcomeLabel = TitleLabel(self.widget)
        self.welcomeLabel.setObjectName("welcomeLabel")
        self.verticalLayout_2.addWidget(self.welcomeLabel, 0, QtCore.Qt.AlignHCenter)
        
        spacerItem2 = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem2)
        
        # 用户名输入框
        self.userEdit = LineEdit(self.widget)
        self.userEdit.setClearButtonEnabled(True)
        # 添加图标
        self.userEdit.addAction(Action(FluentIcon.PEOPLE, 'User'), QtWidgets.QLineEdit.LeadingPosition)
        self.userEdit.setObjectName("userEdit")
        self.verticalLayout_2.addWidget(self.userEdit)
        
        # 密码输入框
        self.passwordEdit = LineEdit(self.widget)
        self.passwordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordEdit.setClearButtonEnabled(True)
        # 添加图标
        self.passwordEdit.addAction(Action(FluentIcon.FINGERPRINT, 'Password'), QtWidgets.QLineEdit.LeadingPosition)
        self.passwordEdit.setObjectName("passwordEdit")
        self.verticalLayout_2.addWidget(self.passwordEdit)
        
        # 记住密码复选框
        self.checkBox = CheckBox(self.widget)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_2.addWidget(self.checkBox)
        
        spacerItem3 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem3)
        
        # 登录按钮
        self.loginButton = PrimaryPushButton(self.widget)
        self.loginButton.setMinimumHeight(35) 
        self.loginButton.setObjectName("loginButton")
        self.verticalLayout_2.addWidget(self.loginButton)
        
        spacerItem4 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem4)
        
        # 水平布局放置“注册”与“找回密码”
        self.horizontalLayout_actions = QtWidgets.QHBoxLayout()
        self.horizontalLayout_actions.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_actions.setObjectName("horizontalLayout_actions")
        
        # 注册按钮
        self.regButton = HyperlinkButton(self.widget)
        self.regButton.setObjectName("regButton")
        self.horizontalLayout_actions.addWidget(self.regButton)
        
        # 中间弹簧推开两侧
        spacerItem_actions = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_actions.addItem(spacerItem_actions)
        
        # 找回密码按钮
        self.fondButton = HyperlinkButton(self.widget)
        self.fondButton.setObjectName("fondButton")
        self.horizontalLayout_actions.addWidget(self.fondButton)
        
        self.verticalLayout_2.addLayout(self.horizontalLayout_actions)
        
        # 底部弹簧
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem6)
        
        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(Login)
        QtCore.QMetaObject.connectSlotsByName(Login)

    def retranslateUi(self, Login):
        _translate = QtCore.QCoreApplication.translate
        Login.setWindowTitle(_translate("Login", "系统登录 - 矿业沉陷预测"))
        self.welcomeLabel.setText(_translate("Login", "欢迎使用"))
        self.userEdit.setPlaceholderText(_translate("Login", "请输入用户名 / 邮箱"))
        self.passwordEdit.setPlaceholderText(_translate("Login", "请输入密码"))
        self.checkBox.setText(_translate("Login", "记住密码"))
        self.loginButton.setToolTip(_translate("Login", "点击登录系统"))
        self.loginButton.setText(_translate("Login", "登 录"))
        self.regButton.setText(_translate("Login", "注册账号"))
        self.fondButton.setText(_translate("Login", "忘记密码？"))