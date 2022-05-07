'''
Created on Aug 19, 2014

@author: bitcraze
'''
import sys
from PyQt6 import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class CompassWidget(QWidget):
    angleChanged = pyqtSignal(float)

    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        self.setMinimumSize(200, 200)
        self.setMaximumSize(200, 200)

        self.setStyleSheet("background-color:transparent;")
        self._angle = 0.0
        self._bug_angle = 0.0
        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S",
                           225: "SW", 270: "W", 315: "NW"}

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(event.rect(), self.palette().brush(QPalette.ColorRole.Window))
        self.drawMarkings(painter)
        self.drawNeedle(painter)

        painter.end()

    def drawMarkings(self, painter):

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)

        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)

        painter.setFont(font)

        i = 0
        while i < 360:
            if i == 0:
                painter.setPen(self.palette().color(QPalette.ColorRole.Highlight))
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(int(-metrics.horizontalAdvance(self._pointText[i]) / 2.0), -52, self._pointText[i])
                painter.setPen(self.palette().color(QPalette.ColorRole.Shadow))
            elif i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(int(-metrics.horizontalAdvance(self._pointText[i]) / 2.0), -52,
                                 self._pointText[i])
            else:
                painter.drawLine(0, -45, 0, -50)

            painter.rotate(15)
            i += 15

        painter.restore()

    def drawNeedle(self, painter):

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(self.palette().color(QPalette.ColorRole.Shadow), 2, Qt.PenStyle.SolidLine))
        painter.setBrush(self.palette().brush(QPalette.ColorRole.Shadow))

        # painter.drawLine(0, -20, 0, 20)
        # painter.drawLine(-20, -5, 20, -5)
        # painter.drawLine(10, 15, -10, 15)

        painter.setPen(QPen(Qt.PenStyle.NoPen))
        # painter.drawEllipse(QPoint(0,c), r, r)
        # painter.drawEllipse(QPoint(-c,0), r, r)
        # painter.drawEllipse(QPoint(c,0), r, r)

        painter.setBrush(self.palette().brush(QPalette.ColorRole.Highlight))

        # painter.drawEllipse(QPoint(0,-c), r, r)
        # needle = QPolygon([QPoint(-5, -20), QPoint(0, -35), QPoint(5, -20), QPoint(0, -25), QPoint(-5, -20)])
        needle = QPolygon([QPoint(0, -40), QPoint(4, -30), QPoint(5, -15), QPoint(35, -2), QPoint(35, 3), QPoint(4, 0),
                           QPoint(3, 28), QPoint(11, 33), QPoint(11, 37), QPoint(0, 35), QPoint(-11, 37), QPoint(-11, 33),
                           QPoint(-3, 28), QPoint(-4, 0), QPoint(-35, 3), QPoint(-35, -2), QPoint(-5, -15),
                           QPoint(-4, -30), QPoint(0, -40)])
        painter.drawPolygon(needle)

        painter.restore()

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(self.palette().color(QPalette.ColorRole.Shadow), 0, Qt.PenStyle.SolidLine))
        painter.setBrush(self.palette().brush(QPalette.ColorRole.Highlight))

        painter.restore()

    def sizeHint(self):
        return QSize(150, 150)

    def angle(self):
        return self._angle

    def setAngle(self, angle):
        if angle != self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()

    # angle = pyqtProperty(float, angle, setAngle)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    compass = CompassWidget()
    spinBox = QSpinBox()
    spinBox.setRange(0, 359)
    spinBox.valueChanged.connect(compass.setAngle)

    layout = QVBoxLayout()
    layout.addWidget(compass)
    layout.addWidget(spinBox)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec())
