from PyQt5 import QtWidgets, QtCore, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import os
import time
import serial
from random import randint

PORT = 'COM4'
RESISTANCE = 10000

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('plot.ui', self)

        self.show_currence = False
        self.is_stopped = False
        self.seconds = 5
        self.scale_k = 0
        self.autoscaled = True

        self.bt_currence.toggled.connect(self.currence_selected)
        self.bt_voltage.toggled.connect(self.voltage_selected)
        self.bt_stop.toggled.connect(self.stop_graphing)
        self.bt_reboot.clicked.connect(self.reboot)
        self.dial.valueChanged.connect(self.change_x)
        self.auto_scale.toggled.connect(self.autoscale)
        self.y_from.valueChanged.connect(self.change_y)
        self.y_to.valueChanged.connect(self.change_y)

        self.x = [(i * 0.1) for i in range(self.seconds * 10)]

        self.ser = serial.Serial(PORT, 9600)
        time.sleep(2)
        self.I = list()
        self.U1 = list()
        self.U2 = list()
        self.ser.readline()
        while len(self.U2) != (self.seconds * 10) and len(self.I) != (self.seconds * 10):
            if len(self.U2) > (self.seconds * 10):
                self.U2 = self.U2[(len(self.U2) + 1) - (self.seconds * 10):]
            if len(self.I) > (self.seconds * 10):
                self.I = self.I[(len(self.I) + 1) - (self.seconds * 10):]
            self.data = str(self.ser.readline())[2:-5].split()
            if len(self.data) == 2:
                if len(self.data[1]) <= 7:
                    self.U2_temp = float(self.data[1]) / 1024 * 5
                    self.U1_temp = float(self.data[0]) / 1024 * 5
                    self.U2.append(abs(self.U2_temp - self.U1_temp))
                    self.I.append(self.U2_temp / RESISTANCE)
            else:
                self.U2.append(float(0))
                self.I.append(float(0))

        self.pen = pg.mkPen(color=(0, 255, 0), width=1)
        self.data_line = self.graphWidget.plot(self.x, self.U2, pen=self.pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        self.data = str(self.ser.readline())[2:-5].split()
        self.U2_temp = float(self.data[1]) / 1024 * 5
        self.U1_temp = float(self.data[0]) / 1024 * 5
        self.U2 = self.U2[1:]
        self.I = self.I[1:]
        if len(self.data) == 2:
            if len(self.data[1]) <= 7:
                self.U2.append(abs(self.U2_temp - self.U1_temp))
                self.I.append(self.U2_temp / RESISTANCE)
        else:
            self.U2.append(float(0))
        if not self.is_stopped:
            if self.show_currence:
                if len(self.x) == len(self.I):
                    self.data_line.setData(self.x, self.I)
            else:
                if len(self.x) == len(self.U2):
                    self.data_line.setData(self.x, self.U2)

    def currence_selected(self, selected):
        if selected:
            self.show_currence = True

    def voltage_selected(self, selected):
        if selected:
            self.show_currence = False

    def stop_graphing(self, selected):
        if selected:
            self.is_stopped = True
        else:
            self.is_stopped = False

    def autoscale(self, selected):
        if selected:
            self.autoscaled = True
            self.graphWidget.enableAutoRange()
        else:
            self.autoscaled = False
            self.change_y()

    def change_x(self):
        self.seconds = self.dial.value()
        self.x = [(i * 0.1) for i in range(self.seconds * 10)]

        while len(self.U2) != (self.seconds * 10) and len(self.I) != (self.seconds * 10):
            if len(self.U2) > (self.seconds * 10):
                self.U2 = self.U2[(len(self.U2) + 1) - (self.seconds * 10):]
            if len(self.I) > (self.seconds * 10):
                self.I = self.I[(len(self.I) + 1) - (self.seconds * 10):]
            self.data = str(self.ser.readline())[2:-5].split()
            if len(self.data) == 2:
                if len(self.data[1]) <= 7:
                    self.U2_temp = float(self.data[1]) / 1024 * 5
                    self.U1_temp = float(self.data[0]) / 1024 * 5
                    self.U2.append(abs(self.U2_temp - self.U1_temp))
                    self.I.append(self.U2_temp / RESISTANCE)
            else:
                self.U2.append(float(0))
                self.I.append(float(0))

    def change_y(self):
        if not self.autoscaled:
            if self.show_currence:
                self.scale_k = 0.023 / 100
            else:
                self.scale_k = 5 / 100
            if self.y_from.value() <= self.y_to.value():
                self.graphWidget.setYRange(self.y_from.value() * self.scale_k,
                                           self.y_to.value() * self.scale_k)
            else:
                self.graphWidget.setYRange(self.y_to.value() * self.scale_k,
                                           self.y_from.value() * self.scale_k)

    def reboot(self):
        self.graphWidget.clear()
        uic.loadUi('oscilloscope.ui', self)

        self.show_currence = False
        self.is_stopped = False
        self.seconds = 5
        self.scale_k = 0
        self.autoscaled = True

        self.bt_currence.toggled.connect(self.currence_selected)
        self.bt_voltage.toggled.connect(self.voltage_selected)
        self.bt_stop.toggled.connect(self.stop_graphing)
        self.bt_reboot.clicked.connect(self.reboot)
        self.dial.valueChanged.connect(self.change_x)
        self.auto_scale.toggled.connect(self.autoscale)
        self.y_from.valueChanged.connect(self.change_y)
        self.y_to.valueChanged.connect(self.change_y)

        self.x = [(i * 0.1) for i in range(self.seconds * 10)]

        time.sleep(2)
        self.I = list()
        self.U1 = list()
        self.U2 = list()
        self.ser.readline()
        while len(self.U2) != (self.seconds * 10) and len(self.I) != (self.seconds * 10):
            if len(self.U2) > (self.seconds * 10):
                self.U2 = self.U2[(len(self.U2) + 1) - (self.seconds * 10):]
            if len(self.I) > (self.seconds * 10):
                self.I = self.I[(len(self.I) + 1) - (self.seconds * 10):]
            self.data = str(self.ser.readline())[2:-5].split()
            if len(self.data) == 2:
                if len(self.data[1]) <= 7:
                    self.U2_temp = float(self.data[1]) / 1024 * 5
                    self.U1_temp = float(self.data[0]) / 1024 * 5
                    self.U2.append(abs(self.U2_temp - self.U1_temp))
                    self.I.append(self.U2_temp / RESISTANCE)
            else:
                self.U2.append(float(0))
                self.I.append(float(0))

        self.pen = pg.mkPen(color=(0, 255, 0), width=1)
        self.data_line = self.graphWidget.plot(self.x, self.U2, pen=self.pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
print(w.ser.name)
w.show()
sys.exit(app.exec_())
