#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	 ||		  ____  _ __
#  +------+	  / __ )(_) /_______________ _____  ___
#  | 0xBC |	 / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+	/ /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||	/_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2011-2013 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
Attitude indicator widget.
"""

__author__ = 'Bitcraze AB'
__all__ = ['AttitudeIndicator']

import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class AttitudeIndicator(QWidget):
    """Widget for showing attitude"""

    sigMakeSpace = pyqtSignal()

    def __init__(self, hz=30):
        super().__init__()

        self.roll = 0
        self.pitch = 0
        self.hover = False
        self.hoverASL = 0.0
        self.hoverTargetASL = 0.0
        self.pixmap = None  # Background camera image
        self.needUpdate = True

        self.msg = ""
        self.hz = hz

        self.freefall = 0
        self.crashed = 0
        self.ff_acc = 0
        self.ff_m = 0
        self.ff_v = 0

        self.setMinimumSize(200, 200)
        self.setMaximumSize(200,200)

        # Update self at 30hz
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateAI)
        self.updateTimer.start(1000 // self.hz)

        self.msgRemove = 0

        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed,
                                       QSizePolicy.Policy.MinimumExpanding))

    def mouseDoubleClickEvent(self, e):
        self.sigMakeSpace.emit()

    def updateAI(self):
        if self.msgRemove > 0:
            self.msgRemove -= 1
            if self.msgRemove <= 0:
                self.msg = ""
                self.needUpdate = True

        if self.freefall > 0:
            self.freefall = self.freefall * 5 / 6 - 1
            self.needUpdate = True

        if self.crashed > 0:
            self.crashed = self.crashed * 5 / 6 - 1
            self.needUpdate = True

        if self.isVisible() and self.needUpdate:
            self.needUpdate = False
            self.repaint()

    def setRoll(self, roll):
        self.roll = roll
        self.needUpdate = True

    def setPitch(self, pitch):
        self.pitch = pitch
        self.needUpdate = True

    def setHover(self, target):
        self.hoverTargetASL = target
        self.hover = target > 0
        self.needUpdate = True

    def setBaro(self, asl):
        self.hoverASL = asl
        self.needUpdate = True

    def setRollPitch(self, roll, pitch):
        self.roll = roll
        self.pitch = pitch
        self.needUpdate = True

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        blue = QColor(min(255, 0 + self.crashed), min(255, 61 + self.freefall), 144, 255 if self.pixmap is None else 64)
        maroon = QColor(min(255, 59 + self.crashed), min(255, 41 + self.freefall), 39,
                        255 if self.pixmap is None else 64)

        # Draw background image (camera)
        if self.pixmap is not None:
            qp.drawPixmap(0, 0, w, h, self.pixmap)

        qp.translate(w / 2, h / 2)
        qp.rotate(self.roll)
        qp.translate(0, (self.pitch * h) / 50)
        qp.translate(-w / 2, -h / 2)
        qp.setRenderHint(qp.RenderHint.Antialiasing)

        font = QFont('Serif', 7, QFont.Weight.Light)
        qp.setFont(font)

        # Draw the blue
        qp.setPen(blue)
        qp.setBrush(blue)
        qp.drawRect(-w, h // 2, 3 * w, -3 * h)

        # Draw the maroon
        qp.setPen(maroon)
        qp.setBrush(maroon)
        qp.drawRect(-w, h // 2, 3 * w, 3 * h)

        pen = QPen(QColor(255, 255, 255), 1.5, Qt.PenStyle.SolidLine)
        qp.setPen(pen)
        qp.drawLine(-w, h // 2, 3 * w, h // 2)

        # Drawing pitch lines

        for ofset in [-180, 0, 180]:
            for i in range(-900, 900, 25):
                pos = int(((i / 10.0) + 25 + ofset) * h / 50.0)
                if i % 100 == 0:
                    length = 0.35 * w
                    if i != 0:
                        if ofset == 0:
                            qp.drawText(int((w / 2) + (length / 2) + (w * 0.06)),
                                        pos, "{}".format(-i / 10))
                            qp.drawText(int((w / 2) - (length / 2) - (w * 0.08)),
                                        pos, "{}".format(-i / 10))
                        else:
                            qp.drawText(int((w / 2) + (length / 2) + (w * 0.06)),
                                        pos, "{}".format(i / 10))
                            qp.drawText(int((w / 2) - (length / 2) - (w * 0.08)),
                                        pos, "{}".format(i / 10))
                elif i % 50 == 0:
                    length = 0.2 * w
                else:
                    length = 0.1 * w

                qp.drawLine(int((w / 2) - (length / 2)), pos,
                            int((w / 2) + (length / 2)), pos)

        qp.setWorldMatrixEnabled(False)

        pen = QPen(QColor(0, 0, 0), 2, Qt.PenStyle.SolidLine)
        qp.setBrush(QColor(0, 0, 0))
        qp.setPen(pen)
        qp.drawLine(0, h // 2, w, h // 2)

        # Draw Hover vs Target

        qp.setWorldMatrixEnabled(False)

        pen = QPen(QColor(255, 255, 255), 2, Qt.PenStyle.SolidLine)
        qp.setBrush(QColor(255, 255, 255))
        qp.setPen(pen)
        fh = max(7, h // 50)
        font = QFont('Sans', fh, QFont.Weight.Light)
        qp.setFont(font)
        qp.resetTransform()

        qp.translate(0, h / 2)
        if not self.hover:
            qp.drawText(int(w - fh * 10), int(fh / 2), str(round(self.hoverASL, 2)))  # asl

        if self.hover:
            qp.drawText(int(w - fh * 10), int(fh / 2), str(round(self.hoverTargetASL, 2)))  # target asl (center)
            diff = round(self.hoverASL - self.hoverTargetASL, 2)
            pos_y = -h // 6 * diff

            # cap to +- 2.8m
            if diff < -2.8:
                pos_y = -h // 6 * -2.8
            elif diff > 2.8:
                pos_y = -h // 6 * 2.8
            else:
                pos_y = -h // 6 * diff
            qp.drawText(int(w - fh * 3.8), int(pos_y + fh / 2),
                        str(diff))  # difference from target (moves up and down +- 2.8m)
            qp.drawLine(int(w - fh * 4.5), 0, int(w - fh * 4.5), int(pos_y))  # vertical line
            qp.drawLine(int(w - fh * 4.7), 0, int(w - fh * 4.5), 0)  # left horizontal line
            qp.drawLine(int(w - fh * 4.2), int(pos_y), int(w - fh * 4.5), int(pos_y))  # right horizontal line

        # FreeFall Detection
        qp.resetTransform()
        qp.translate(0, h / 2)
        #qp.drawText(int(fh * 6), int(fh / 2), str(round(self.ff_acc + 1, 2)) + 'G')  # acc

        pos_y = h / 6 * self.ff_acc

        # cap to +- 2.8m
        if self.ff_acc < -2.8:
            pos_y = -h / 6 * -2.8
        elif self.ff_acc > 2.8:
            pos_y = -h / 6 * 2.8
        else:
            pos_y = -h // 6 * self.ff_acc
        qp.drawLine(int(fh * 4.5), 0, int(fh * 4.5), int(pos_y))  # vertical line
        qp.drawLine(int(fh * 4.7), 0, int(fh * 4.5), 0)  # left horizontal line
        qp.drawLine(int(fh * 4.2), int(pos_y), int(fh * 4.5), int(pos_y))  # right horizontal line


if __name__ == "__main__":
    class Example(QWidget):

        def __init__(self):
            super(Example, self).__init__()

            self.initUI()

        def updatePitch(self, pitch):
            self.wid.setPitch(pitch - 90)

        def updateRoll(self, roll):
            self.wid.setRoll((roll / 10.0) - 180.0)

        def updateTarget(self, target):
            self.wid.setHover(target)

        def updateBaro(self, asl):
            self.wid.setBaro(asl)

        def initUI(self):
            vbox = QVBoxLayout()

            sld = QSlider(Qt.Horizontal, self)
            sld.setFocusPolicy(Qt.NoFocus)
            sld.setRange(0, 3600)
            sld.setValue(1800)
            vbox.addWidget(sld)

            self.wid = AttitudeIndicator()

            sld.valueChanged[int].connect(self.updateRoll)
            vbox.addWidget(self.wid)

            hbox = QHBoxLayout()
            hbox.addLayout(vbox)

            sldPitch = QSlider(Qt.Vertical, self)
            sldPitch.setFocusPolicy(Qt.NoFocus)
            sldPitch.setRange(0, 180)
            sldPitch.setValue(90)
            sldPitch.valueChanged[int].connect(self.updatePitch)
            hbox.addWidget(sldPitch)

            sldASL = QSlider(Qt.Vertical, self)
            sldASL.setFocusPolicy(Qt.NoFocus)
            sldASL.setRange(-200, 200)
            sldASL.setValue(0)
            sldASL.valueChanged[int].connect(self.updateBaro)

            sldT = QSlider(Qt.Vertical, self)
            sldT.setFocusPolicy(Qt.NoFocus)
            sldT.setRange(-200, 200)
            sldT.setValue(0)
            sldT.valueChanged[int].connect(self.updateTarget)

            hbox.addWidget(sldT)
            hbox.addWidget(sldASL)

            self.setLayout(hbox)

            self.setGeometry(50, 50, 510, 510)
            self.setWindowTitle('Attitude Indicator')
            self.show()

        def changeValue(self, value):
            self.c.updateBW.emit(value)
            self.wid.repaint()


    def main():
        app = QApplication(sys.argv)
        ex = Example()
        sys.exit(app.exec())


    main()
