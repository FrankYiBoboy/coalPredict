# coding: utf-8
from PyQt5.QtCore import QObject


class Translator(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.text = self.tr('Text')
        self.model = "应用"
        self.history = "历史记录"