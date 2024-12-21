from PyQt5.QtCore import QEasingCurve, pyqtProperty
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QPoint, Qt, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QMainWindow, QApplication, QFrame, QCheckBox, QVBoxLayout


class ToggleButton(QCheckBox):  # Наследуемся от QCheckBox
    """Это переключатель toggle switch, т.к его нет в инструментарии Qt Designer, мы прописываем класс самостоятельно"""
    def __init__(
        self,
        parent=None,
        width=70,
        bgColor="#777",
        circleColor="#DDD",
        activeColor="#00BCff",
        animationCurve=QEasingCurve.OutBounce,
    ):
        super().__init__(parent)  # Используем super() для вызова конструктора родителя

        self.setFixedSize(width, 40)
        self.setCursor(Qt.PointingHandCursor)

        self._bg_color = bgColor
        self._circle_color = circleColor
        self._active_color = activeColor
        self._circle_position = 3
        self.animation = QPropertyAnimation(self, b"circle_position")

        self.animation.setEasingCurve(animationCurve)
        self.animation.setDuration(500)
        self.stateChanged.connect(self.start_transition)

    @pyqtProperty(int)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    def start_transition(self, value):
        self.animation.setStartValue(self.circle_position)
        if value:
            self.animation.setEndValue(self.width() - 35)
        else:
            self.animation.setEndValue(3)
        self.animation.start()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(Qt.NoPen)

        rect = QRect(0, 0, self.width(), self.height())

        if not self.isChecked():
            p.setBrush(QColor(self._bg_color))
            p.drawRoundedRect(
                0, 0, 
                rect.width(), 
                self.height(), 
                self.height() / 2, 
                self.height() / 2
            )

            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._circle_position, 3, 32, 32)
        else:
            p.setBrush(QColor(self._active_color))
            p.drawRoundedRect(
                0, 0, 
                rect.width(), 
                self.height(), 
                self.height() / 2, 
                self.height() / 2
            )

            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._circle_position, 3, 32, 32)