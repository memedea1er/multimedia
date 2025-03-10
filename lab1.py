import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QDoubleSpinBox, QLabel, QPushButton,
                               QHBoxLayout, QLineEdit)
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QPainterPath
from PySide6.QtCore import Qt, QPointF, QRectF


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.x_min = -10.0
        self.x_max = 10.0
        self.y_min = self.x_min
        self.y_max = self.x_max
        self.step = 1.0
        self.available_functions = {
            "1": (lambda x: x, Qt.blue),  # f(x) = x^2
            "2": (lambda x: x ** 2, Qt.green),  # f(x) = sin(x) * exp(-0.1 * x^2)
            "3": (lambda x: 1 / x if x != 0 else None, Qt.red)  # f(x) = 1/x
        }
        self.function_formulas = {
            "1": "f(x) = x",
            "2": "f(x) = x^2",
            "3": "f(x) = 1/x"
        }
        self.selected_functions = []  # Список выбранных функций

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width, height = self.width(), self.height()
        grid_step = min(width, height) / (self.x_max - self.x_min)

        painter.fillRect(self.rect(), QBrush(Qt.white))

        # Рисуем сетку
        pen = QPen(Qt.lightGray, 1, Qt.DashLine)
        painter.setPen(pen)

        # Сетка по X
        i = self.x_min
        while i <= self.x_max:
            x = (i - self.x_min) * grid_step
            painter.drawLine(x, 0, x, height)
            i += self.step

        # Сетка по Y
        i = self.y_min
        while i <= self.y_max:
            y = (self.y_max - i) * grid_step
            painter.drawLine(0, y, width, y)
            i += self.step

        # Рисуем оси
        pen.setColor(Qt.black)
        pen.setWidth(2)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)

        # Ось X
        x_axis_y = (self.y_max - 0) * grid_step
        painter.drawLine(0, x_axis_y, width, x_axis_y)

        # Ось Y
        y_axis_x = (0 - self.x_min) * grid_step
        painter.drawLine(y_axis_x, 0, y_axis_x, height)

        # Рисуем выбранные функции
        pen.setWidth(2)
        for key in self.selected_functions:
            if key in self.available_functions:
                func, color = self.available_functions[key]
                pen.setColor(color)
                self.draw_function(painter, func, y_axis_x, x_axis_y, grid_step, pen)

        # Рисуем легенду
        self.draw_legend(painter, width, height)

        # Рисуем оси
        pen.setColor(Qt.black)
        painter.setPen(pen)

        # Подписи осей
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(width - 30, x_axis_y - 5, "X")
        painter.drawText(y_axis_x + 10, 15, "Y")

        # Подписи меток на осях
        font.setPointSize(10)
        painter.setFont(font)
        i = self.x_min + self.step
        while i <= self.x_max:
            x = (i - self.x_min) * grid_step
            y = (self.y_max - i) * grid_step
            if i != 0:
                painter.drawText(x - 15, x_axis_y + 20, f"{i:.2f}")
                painter.drawText(y_axis_x - 40, y + 5, f"{i:.2f}")
            i += self.step

    def draw_function(self, painter, func, cx, cy, scale, pen):
        bar_width = scale * self.step * 0.8  # Ширина треугольника
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))

        for x in np.arange(self.x_min, self.x_max+self.step, self.step):
            y = func(x)

            if y is not None and self.x_min <= x <= self.x_max:
                painter.setPen(Qt.NoPen)  # Убираем контур для заливки
                px = cx + x * scale
                py = cy - y * scale

                # Точки треугольника
                top = QPointF(px, py)  # Верхушка
                left = QPointF(px - bar_width / 2, cy)  # Левая нижняя
                right = QPointF(px + bar_width / 2, cy)  # Правая нижняя

                rect = QRectF(px - bar_width / 2, cy - bar_width / 4, bar_width, bar_width / 2)

                if y > 0:
                    painter.drawPie(rect, 180 * 16, 180 * 16)  # Верхняя половина
                else:
                    painter.drawPie(rect, 0 * 16, 180 * 16)  # Нижняя половина

                # Заливаем конус
                painter.drawPolygon([top, left, right])

                painter.setPen(pen)  # Используем тот же цвет для границы

                if y > 0:
                    painter.drawArc(rect, 180 * 16, 180 * 16)  # Верхняя дуга
                else:
                    painter.drawArc(rect, 0 * 16, 180 * 16)  # Нижняя дуга

                # Отдельно рисуем только боковые линии, не соединяя их снизу
                painter.drawLine(top, left)
                painter.drawLine(top, right)

    def draw_legend(self, painter, width, height):
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)

        legend_x = width - 150
        legend_y = 30
        line_height = 20

        for key in self.selected_functions:
            if key in self.function_formulas:
                formula = self.function_formulas[key]
                painter.setPen(QPen(self.available_functions[key][1]))
                painter.drawText(legend_x, legend_y, f"{key}: {formula}")
                legend_y += line_height

    def update_settings(self, x_min, x_max, selected_functions):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = x_min
        self.y_max = x_max
        self.step = abs(x_max-x_min) / 20
        self.selected_functions = selected_functions
        self.update()


class SettingsWindow(QWidget):
    def __init__(self, plot_widget):
        super().__init__()
        self.setWindowTitle("Настройки")
        layout = QVBoxLayout()

        self.x_min_spin = QDoubleSpinBox()
        self.x_min_spin.setRange(-1000.0, 1000.0)
        self.x_min_spin.setValue(plot_widget.x_min)
        self.x_min_spin.valueChanged.connect(self.update_plot)

        self.x_max_spin = QDoubleSpinBox()
        self.x_max_spin.setRange(-1000.0, 1000.0)
        self.x_max_spin.setValue(plot_widget.x_max)
        self.x_max_spin.valueChanged.connect(self.update_plot)

        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Введите номера функций, например: 1,2,3")
        self.function_input.textChanged.connect(self.update_plot)

        layout.addWidget(QLabel("X min:"))
        layout.addWidget(self.x_min_spin)
        layout.addWidget(QLabel("X max:"))
        layout.addWidget(self.x_max_spin)
        layout.addWidget(QLabel("Функции:"))
        layout.addWidget(self.function_input)
        self.setLayout(layout)

        self.plot_widget = plot_widget

    def update_plot(self):
        selected_functions = [f.strip() for f in self.function_input.text().split(",") if
                              f.strip() in self.plot_widget.available_functions]
        self.plot_widget.update_settings(self.x_min_spin.value(), self.x_max_spin.value(),
                                         selected_functions)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графики функций")
        self.setGeometry(100, 100, 700, 700)

        self.plot_widget = PlotWidget()
        self.settings_window = SettingsWindow(self.plot_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)

        settings_button = QPushButton("Настройки")
        settings_button.clicked.connect(self.settings_window.show)
        layout.addWidget(settings_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
