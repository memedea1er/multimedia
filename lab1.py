import sys
import math
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QDoubleSpinBox, QLabel, QPushButton, QLineEdit
)
from PySide6.QtGui import QPainter, QPen, QBrush, QFont, QColor, QFontMetrics
from PySide6.QtCore import Qt, QPointF

import math

def func1(x):
    """f1(x) = x"""
    return x

def func2(x):
    """f2(x) = x^2"""
    return x**2

def func3(x):
    """f3(x) = 1/x (с разрывом в 0)"""
    if x == 0 or abs(x) < 1e-10:  # Добавили проверку на очень маленькие значения
        return None
    return 1/x

def func4(x):
    """f4(x) = sin(x)"""
    return math.sin(x)

def func5(x):
    """f5(x) = cos(x)"""
    return math.cos(x)

def func6(x):
    """f6(x) = 2*sin(x)"""
    return 2*math.sin(x)

def func7(x):
    """f7(x) = e^(-x^2)"""
    return math.exp(-x*x)

def func8(x):
    """f8(x) = ln(x), только для x>0"""
    if x <= 0:
        return None
    return math.log(x)

def func9(x):
    """f9(x) = x^3"""
    return x**3

# Для удобства: словарь, где ключ - строка "1","2",..., а значение - (функция, формула)
functions_map = {
    "1": (func1,  "f(x) = x"),
    "2": (func2,  "f(x) = x²"),
    "3": (func3,  "f(x) = 1/x"),
    "4": (func4,  "f(x) = sin(x)"),
    "5": (func5,  "f(x) = cos(x)"),
    "6": (func6,  "f(x) = 2*sin(x)"),
    "7": (func7,  "f(x) = e^(-x²)"),
    "8": (func8,  "f(x) = ln(x)"),
    "9": (func9,  "f(x) = x³")
}

################################
#        PlotWidget
################################
class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)

        # Изначальные границы
        self.x_min = -2.0
        self.x_max =  2.0
        self.y_min = -2.0
        self.y_max =  2.0

        # В plot_widget по-прежнему храним "step", но теперь
        # пользователь напрямую задаёт не его, а кол-во точек.
        self.step = 1.0

        # Список выбранных функций (не более 3)
        self.selected_functions = []

        # Цветовая схема для ключей "1".."9"
        self.color_map = {
            "1": QColor(Qt.blue),
            "2": QColor(Qt.green),
            "3": QColor(Qt.red),
            "4": QColor(Qt.magenta),
            "5": QColor(Qt.darkCyan),
            "6": QColor(Qt.darkYellow),
            "7": QColor(Qt.darkBlue),
            "8": QColor(Qt.darkGreen),
            "9": QColor(Qt.darkRed)
        }

    def update_settings(self, x_min, x_max, step, selected_functions):
        self.x_min = x_min
        self.x_max = x_max
        self.step  = step

        # Берём максимум 3 функций
        self.selected_functions = selected_functions[:3]

        # Автоматически определяем y-границы по выбранным функциям
        computed_values = []
        # Проходим по всем x от x_min до x_max с вычисленным шагом
        for x in np.arange(x_min, x_max + step*0.5, step):
            for key in self.selected_functions:
                if key in functions_map:
                    func, _ = functions_map[key]
                    val = func(x)
                    if val is not None:
                        computed_values.append(val)

        if computed_values:
            y_min_computed = min(computed_values)
            y_max_computed = max(computed_values)
            # Небольшой запас, например 2.5% от диапазона
            margin = (y_max_computed - y_min_computed) * 0.025
            self.y_min = y_min_computed - margin
            self.y_max = y_max_computed + margin
        else:
            # Если функций нет, то оставляем x_min..x_max
            self.y_min = x_min
            self.y_max = x_max

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()

        # Обеспечиваем, что 0 по f(x) попадёт
        self.y_min = min(self.y_min, 0)
        self.y_max = max(self.y_max, 0)

        # Добавляем отступ, чтобы цилиндры не обрезались
        x_min_m = self.x_min - self.step
        x_max_m = self.x_max + self.step
        y_min_m = self.y_min - self.step
        y_max_m = self.y_max + self.step

        # Масштабы
        scale_x = H / (x_max_m - x_min_m)  # x - вертикальная ось
        scale_y = W / (y_max_m - y_min_m)  # f(x) - горизонтальная

        def screenY(x):
            return (x_max_m - x) * scale_x

        def screenX(fval):
            return (fval - y_min_m) * scale_y

        # 1) Фон
        painter.fillRect(self.rect(), Qt.white)

        # 2) Сетка (рисуем в целых координатах x и f(x), чтобы совпадало с подписями)
        pen = QPen(Qt.lightGray, 1, Qt.DashLine)
        painter.setPen(pen)

        # Горизонтальные линии (ось X: целые j от floor(x_min) до ceil(x_max))
        j_min = math.floor(self.x_min)
        j_max = math.ceil(self.x_max)
        for j in range(j_min, j_max + 1):
            painter.drawLine(0, screenY(j), W, screenY(j))

        # Вертикальные линии (ось f(x): целые i от floor(y_min) до ceil(y_max))
        i_min = math.floor(self.y_min)
        i_max = math.ceil(self.y_max)
        for i in range(i_min, i_max + 1):
            painter.drawLine(screenX(i), 0, screenX(i), H)

        # 3) Оси
        pen.setColor(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        # Горизонтальная ось X (если 0 попадает в диапазон)
        if x_min_m <= 0 <= x_max_m:
            painter.drawLine(0, screenY(0), W, screenY(0))

        # Вертикальная ось f(x) (в x0)
        x0 = screenX(0)
        painter.drawLine(x0, 0, x0, H)

        # 4) Подписи осей
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(W - 40, screenY(0) - 5, "f(x)")
        if x_min_m <= 0 <= x_max_m:
            painter.drawText(x0 + 10, 15, "X")

        fm = QFontMetrics(painter.font())

        # --- Подписи вдоль оси X (вертикальная) ---
        last_y_label = None
        for j in range(j_min, j_max + 1):
            y_pos = screenY(j)
            text = f"{j:.2f}"
            text_height = fm.height()
            if last_y_label is None or abs(y_pos - last_y_label) > text_height + 5:
                painter.drawText(5, y_pos + 5, text)
                last_y_label = y_pos

        # --- Подписи вдоль оси f(x) (горизонтальная) ---
        last_x_label = None
        for i in range(i_min, i_max + 1):
            x_pos = screenX(i)
            text = f"{i:.2f}"
            text_width = fm.horizontalAdvance(text)
            if last_x_label is None or abs(x_pos - last_x_label) > text_width + 5:
                painter.drawText(x_pos - text_width / 2, H - 5, text)
                last_x_label = x_pos

        # 5) Отрисовка «цилиндров» для выбранных функций
        x_val = self.x_min
        # Чтобы гарантированно захватить x_max, можно идти чуть дальше x_max + step*0.5
        while x_val <= self.x_max + self.step*0.5:
            valid_funcs = []
            for key in self.selected_functions:
                if key in functions_map:
                    func, _ = functions_map[key]
                    val = func(x_val)
                    if val is not None:
                        valid_funcs.append((key, func, val))

            n = len(valid_funcs)
            if n > 0:
                step_px = abs(screenY(0) - screenY(self.step))
                base_thickness = step_px * 0.8
                reduce_factor_map = {1: 1.0, 2: 0.5, 3: 0.3}
                reduce_factor = reduce_factor_map.get(n, 1.0)
                bar_thickness = base_thickness * reduce_factor

                # Если несколько функций, «разносим» цилиндры
                offset_schemes = {
                    1: [0],
                    2: [-bar_thickness * 0.6, +bar_thickness * 0.6],
                    3: [-bar_thickness, 0, +bar_thickness]
                }
                offsets = offset_schemes[n]

                for i, (key, func, val_f) in enumerate(valid_funcs):
                    offset_y = offsets[i]
                    self.draw_one_cylinder_vertical_offset(
                        painter,
                        func,
                        self.color_map.get(key, QColor(Qt.black)),
                        x_val, val_f,
                        screenX, screenY,
                        bar_thickness,
                        offset_y
                    )

            x_val += self.step

    def draw_one_cylinder_vertical_offset(self, painter, func, color,
                                        x_val, val,
                                        screenX, screenY,
                                        bar_thickness,
                                        offset_y):
        # ... (тот же код, что у вас сейчас) ...
        ellipse_w = bar_thickness / 2
        ellipse_h = bar_thickness

        left_half_start = 90 * 16
        left_half_span  = 180 * 16
        full_ellipse_start = 0
        full_ellipse_span  = 360 * 16

        py_base = screenY(x_val)
        py = py_base + offset_y

        px0 = screenX(0)
        px1 = screenX(val)

        rect_x = min(px0, px1)
        rect_w = abs(px1 - px0)
        rect_y = py - bar_thickness / 2
        rect_h = bar_thickness

        # Определяем, какая сторона "передняя", а какая "задняя"
        if val >= 0:
            front_center_x = px1
            back_center_x  = px0
        else:
            front_center_x = px0
            back_center_x  = px1

        back_bounding_x  = back_center_x  - ellipse_w / 2
        back_bounding_y  = py - ellipse_h / 2
        front_bounding_x = front_center_x - ellipse_w / 2
        front_bounding_y = py - ellipse_h / 2

        brush_color = color.lighter(150)

        # 1) Задняя полу-крышка
        if val >= 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(brush_color, Qt.SolidPattern))
            painter.drawPie(back_bounding_x, back_bounding_y, ellipse_w, ellipse_h,
                            left_half_start, left_half_span)
            painter.setPen(QPen(color, 2))
            painter.drawArc(back_bounding_x, back_bounding_y, ellipse_w, ellipse_h,
                            left_half_start, left_half_span)

        # 2) Тело конуса
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(brush_color, Qt.SolidPattern))
        if val >= 0:
            painter.drawPolygon([QPointF(rect_x, rect_y), QPointF(rect_x, rect_y + rect_h),
                                 QPointF(rect_x + rect_w, rect_y + rect_h / 2)])
        else:
            painter.drawPolygon([QPointF(rect_x + rect_w, rect_y), QPointF(rect_x + rect_w, rect_y + rect_h),
                                 QPointF(rect_x, rect_y + rect_h / 2)])

        # 4) Обводка верха/низа
        painter.setPen(QPen(color, 2))
        if val >= 0:
            painter.drawLine(rect_x, rect_y, rect_x + rect_w, rect_y + rect_h / 2)
            painter.drawLine(rect_x, rect_y + rect_h, rect_x + rect_w, rect_y + rect_h / 2)
        else:
            painter.drawLine(rect_x, rect_y + rect_h / 2, rect_x + rect_w, rect_y)
            painter.drawLine(rect_x, rect_y + rect_h / 2, rect_x + rect_w, rect_y + rect_h)

        # 5) Передняя (полная) крышка
        if val < 0:
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(front_bounding_x, front_bounding_y, ellipse_w, ellipse_h)
            painter.setPen(QPen(color, 2))
            painter.drawArc(front_bounding_x, front_bounding_y, ellipse_w, ellipse_h,
                            full_ellipse_start, full_ellipse_span)

################################
#   LegendWidget
################################
class LegendWidget(QWidget):
    def __init__(self, plot_widget):
        super().__init__()
        self.setMinimumSize(400, 50)
        self.plot_widget = plot_widget

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), Qt.white)

        x_off = 10
        y_off = self.height() // 2
        gap = 20

        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        fm = painter.fontMetrics()

        for key in self.plot_widget.selected_functions:
            if key in functions_map:
                color = self.plot_widget.color_map.get(key, QColor(Qt.black))
                _, formula = functions_map[key]

                marker_size = 15
                painter.setBrush(color)
                painter.setPen(color)
                painter.drawRect(x_off, y_off - marker_size, marker_size, marker_size)

                painter.setPen(Qt.black)
                text_width = fm.horizontalAdvance(formula)
                text_x = x_off + marker_size + 5
                text_y = y_off - marker_size // 2 + fm.ascent() // 2
                painter.drawText(text_x, text_y, formula)

                x_off += marker_size + 5 + text_width + gap

################################
#   SettingsWindow
################################
class SettingsWindow(QWidget):
    def __init__(self, plot_widget, legend_widget):
        super().__init__()
        self.setWindowTitle("Настройки")
        layout = QVBoxLayout()

        self.plot_widget = plot_widget
        self.legend_widget = legend_widget

        # 1) x_min
        self.x_min_spin = QDoubleSpinBox()
        self.x_min_spin.setRange(-1000.0, 1000.0)
        self.x_min_spin.setValue(plot_widget.x_min)
        layout.addWidget(QLabel("X min:"))
        layout.addWidget(self.x_min_spin)

        # 2) x_max
        self.x_max_spin = QDoubleSpinBox()
        self.x_max_spin.setRange(-1000.0, 1000.0)
        self.x_max_spin.setValue(plot_widget.x_max)
        layout.addWidget(QLabel("X max:"))
        layout.addWidget(self.x_max_spin)

        # 3) Количество точек (дробное, если нужно)
        ### ИЗМЕНЕНО: вместо step_spin теперь npoints_spin
        self.npoints_spin = QDoubleSpinBox()
        self.npoints_spin.setRange(2.0, 1000.0)
        self.npoints_spin.setDecimals(1)      # можно настроить, сколько знаков после запятой
        self.npoints_spin.setValue(5.0)       # например, по умолчанию 5 точек
        layout.addWidget(QLabel("Количество точек (N):"))
        layout.addWidget(self.npoints_spin)

        # 4) Функции
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Введите номера функций (1..9), напр: 1 3 9")
        layout.addWidget(QLabel("Функции:"))
        layout.addWidget(self.function_input)

        # Связки сигналов
        self.x_min_spin.valueChanged.connect(self.apply_settings)
        self.x_max_spin.valueChanged.connect(self.apply_settings)
        self.npoints_spin.valueChanged.connect(self.apply_settings)
        self.function_input.textChanged.connect(self.apply_settings)

        # Кнопка "Применить"
        apply_button = QPushButton("Применить")
        apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(apply_button)

        self.setLayout(layout)

    def apply_settings(self):
        selected_functions = [
            f.strip() for f in self.function_input.text().split()
            if f.strip() in functions_map
        ]
        x_min = self.x_min_spin.value()
        x_max = self.x_max_spin.value()
        n_points = self.npoints_spin.value()  # Теперь это число точек

        # Вычисляем step по формуле (x_max - x_min) / (n_points - 1)
        distance = (x_max - x_min)
        if n_points <= 1 or abs(distance) < 1e-9:
            # Защита от деления на ноль
            step = 1.0
        else:
            step = distance / (n_points - 1)

        # Передаём в plot_widget уже вычисленный шаг
        self.plot_widget.update_settings(x_min, x_max, step, selected_functions)
        # Обновляем легенду
        self.legend_widget.update()

################################
#   MainWindow
################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Диаграмма с функциями, легендой и настройками")
        self.setGeometry(100, 100, 1000, 700)

        self.plot_widget = PlotWidget()
        self.legend_widget = LegendWidget(self.plot_widget)
        self.settings_window = SettingsWindow(self.plot_widget, self.legend_widget)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # График
        main_layout.addWidget(self.plot_widget, stretch=1)
        # Легенда
        main_layout.addWidget(self.legend_widget, stretch=0)

        # Кнопка "Настройки"
        settings_button = QPushButton("Настройки")
        settings_button.clicked.connect(self.settings_window.show)
        main_layout.addWidget(settings_button)

        self.setCentralWidget(main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

