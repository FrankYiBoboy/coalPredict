# coding:utf-8
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar, MessageBoxBase, SubtitleLabel, LineEdit, ComboBox
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog

from ..common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, isWin11
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet

from app.common.auth import AuthManager
from app.common.session import SessionManager

class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('Personalization'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        # self.languageCard = ComboBoxSettingCard(
        #     cfg.language,
        #     FIF.LANGUAGE,
        #     self.tr('Language'),
        #     self.tr('Set your preferred language for UI'),
        #     texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
        #     parent=self.personalGroup
        # )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        
        # 新增管理员面板
        self.init_admin_panel()
        
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + " " + VERSION,
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)
        
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        # self.personalGroup.addSettingCard(self.languageCard)

        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # personalization
        cfg.themeChanged.connect(setTheme)
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))
        
    def init_admin_panel(self):
        """视图拦截：动态加载管理员面板"""
        current_user = SessionManager.get_current_user()
        if current_user != "admin":
            return
        self.adminGroup = SettingCardGroup("人员账户分配", self.scrollWidget)

        # 添加用户卡片
        self.addUserCard = PrimaryPushSettingCard(
            "添加用户",
            FIF.ADD,
            "添加新用户",
            "为实验室新成员分配初始账号和密码",
            self.adminGroup
        )
        self.addUserCard.clicked.connect(self.show_add_user_dialog)
        
        # 修改密码卡片
        self.updatePwdCard = PrimaryPushSettingCard(
            "修改密码",
            FIF.EDIT,
            "修改用户密码",
            "当实验人员遗忘密码时，由管理员统一下发新凭证",
            self.adminGroup
        )
        self.updatePwdCard.clicked.connect(self.show_update_pwd_dialog)
        
        # 删除用户卡片
        self.deleteUserCard = PrimaryPushSettingCard(
            "清理记录",
            FIF.DELETE,
            "注销用户账号",
            "移除离职或调岗人员的系统登录权限",
            self.adminGroup
        )
        self.deleteUserCard.clicked.connect(self.show_delete_user_dialog)
        
        # 挂载到分组中
        self.adminGroup.addSettingCard(self.addUserCard)
        self.adminGroup.addSettingCard(self.updatePwdCard)
        self.adminGroup.addSettingCard(self.deleteUserCard)
        # 添加到布局中
        self.expandLayout.addWidget(self.adminGroup)
        
    def show_add_user_dialog(self):
        # 调起自定义输入弹窗
        w = AddUserDialog(self.window())
        if w.exec():
            new_user = w.userLineEdit.text().strip()
            new_pwd = w.pwdLineEdit.text().strip()
            
            if not new_user or not new_pwd:
                self.show_toast("错误", "用户名或密码不能为空", is_error=True)
                return
                
            success, msg = AuthManager.add_user(new_user, new_pwd)
            msg = "用户" + new_user + msg
            self.show_toast("添加结果", msg, is_error=not success)
    
    def show_update_pwd_dialog(self):
        # 调起自定义输入弹窗
        w = UpdatePwdDialog(self.window())
        if w.exec():
            target_user = w.userComboBox.currentText()
            new_pwd = w.newPwdLineEdit.text().strip()
            
            if not target_user or not new_pwd:
                self.show_toast("错误", "新密码不能为空", is_error=True)
                return
            
            current_user = SessionManager.get_current_user()
            success, msg = AuthManager.update_password(current_user, target_user, new_pwd)
            self.show_toast("密码修改", msg, is_error=not success)
         
    def show_delete_user_dialog(self):
        # 调起自定义输入弹窗
        w = DeleteUserDialog(self.window())
        if w.exec():
            target_user = w.userComboBox.currentText()
            if not target_user:
                return
            current_user = SessionManager.get_current_user()
            success, msg = AuthManager.delete_user(current_user, target_user)
            self.show_toast("注销结果", msg, is_error=not success)
    
    def show_toast(self, title, content, is_error=False):
        """封装底部的气泡提示"""
        if is_error:
            InfoBar.error(title, content, duration=3000, parent=self)
        else:
            InfoBar.success(title, content, duration=3000, parent=self)
        
class AddUserDialog(MessageBoxBase):
    """自定义添加用户对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("添加用户",self)
        
        
        # 输入框
        self.userLineEdit = LineEdit(self)
        self.userLineEdit.setPlaceholderText("请输入用户名")
        self.pwdLineEdit = LineEdit(self)
        self.pwdLineEdit.setPlaceholderText("请输入初始密码")
        self.pwdLineEdit.setClearButtonEnabled(True)
        
        # 将组件添加到 MessageBoxBase 布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.userLineEdit)
        self.viewLayout.addWidget(self.pwdLineEdit)
        
        self.widget.setMinimumWidth(350)
        
class DeleteUserDialog(MessageBoxBase):
    """自定义删除用户对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('注销用户账号', self)
        
        self.userComboBox = ComboBox(self)
        self.userComboBox.setPlaceholderText("请选择要注销的用户")
        
        # 动态加载系统内所有用户，并强制过滤掉 admin 本身，防止误删
        all_users = AuthManager.get_all_users()
        normal_users = [u for u in all_users if u != "admin"]
        self.userComboBox.addItems(normal_users)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.userComboBox)
        self.widget.setMinimumWidth(350)

        # 如果没有普通用户，禁用确定按钮
        if not normal_users:
            self.yesButton.setEnabled(False)
            self.userComboBox.setPlaceholderText("当前系统无其他普通用户")
            
class UpdatePwdDialog(MessageBoxBase):
    """自定义更新密码对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('修改用户密码', self)
        
        self.userComboBox = ComboBox(self)
        self.userComboBox.setPlaceholderText("请选择用户")
        
        all_users = AuthManager.get_all_users()
        # 允许管理员修改包括自己在内的所有人密码
        self.userComboBox.addItems(all_users)
        
        self.newPwdLineEdit = LineEdit(self)
        self.newPwdLineEdit.setPlaceholderText('请输入新密码')
        self.newPwdLineEdit.setClearButtonEnabled(True)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.userComboBox)
        self.viewLayout.addWidget(self.newPwdLineEdit)
        self.widget.setMinimumWidth(350)
        