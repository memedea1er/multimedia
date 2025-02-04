from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QPointF
import sys
import math

# Определение функций
functions = {
    1: (lambda x: x, "Простая функция: y = x"),
    2: (lambda x: x ** 2, "Сложная функция: y = x^2"),
    3: (lambda x: 1 if x != 0 else 0, "Функция с точкой разрыва: y = 1 (x ≠ 0), 0 (x = 0)")
}

class GraphWidget(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width, height = self.width(), self.height()
        margin = 40
        graph_width = width - 2 * margin
        graph_height = height - 2 * margin

        # Рисуем сетку и координатные оси
        painter.setPen(QPen(Qt.lightGray, 1, Qt.DashLine))
        step_x = graph_width / 10
        step_y = graph_height / 10
        for i in range(11):
            # Вертикальные линии
            x = margin + i * step_x
            painter.drawLine(x, margin, x, height - margin)
            # Горизонтальные линии
            y = margin + i * step_y
            painter.drawLine(margin, y, width - margin, y)

        # Оси координат
        painter.setPen(QPen(Qt.black, 2))
        x_axis_y = margin + graph_height - ((0 - min_y) / (max_y - min_y)) * graph_height if min_y <= 0 <= max_y else height - margin
        y_axis_x = margin + ((0 - min_x) / (max_x - min_x)) * graph_width if min_x <= 0 <= max_x else margin
        painter.drawLine(margin, x_axis_y, width - margin, x_axis_y)
        painter.drawLine(y_axis_x, margin, y_axis_x, height - margin)

        # Подписи осей
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        for i in range(11):
            x_val = min_x + i * (max_x - min_x) / 10
            y_val = max_y - i * (max_y - min_y) / 10
            x = margin + i * step_x
            y = margin + i * step_y
            painter.drawText(x - 10, x_axis_y + 15, f"{x_val:.1f}")
            painter.drawText(y_axis_x - 30, y + 5, f"{y_val:.1f}")

        # Рисуем графики
        colors = [Qt.red, Qt.green, Qt.blue]
        for idx, (func_id, points) in enumerate(self.data.items()):
            pen = QPen(colors[idx % len(colors)])
            pen.setWidth(2)
            painter.setPen(pen)
            prev_point = None
            for x, y in points:
                px = margin + ((x - min_x) / (max_x - min_x)) * graph_width
                py = margin + graph_height - ((y - min_y) / (max_y - min_y)) * graph_height
                if prev_point:
                    painter.drawLine(prev_point, QPointF(px, py))
                prev_point = QPointF(px, py)
            # Легенда
            painter.drawText(margin, margin + 20 * idx, functions[func_id][1])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("График функций")
        layout = QVBoxLayout()
        self.input_a = QLineEdit()
        self.input_a.setPlaceholderText("Введите a")
        layout.addWidget(self.input_a)
        self.input_b = QLineEdit()
        self.input_b.setPlaceholderText("Введите b")
        layout.addWidget(self.input_b)
        self.input_n = QLineEdit()
        self.input_n.setPlaceholderText("Введите n (кол-во точек)")
        layout.addWidget(self.input_n)
        self.input_funcs = QLineEdit()
        self.input_funcs.setPlaceholderText("Введите номера функций (например: 1,2)")
        layout.addWidget(self.input_funcs)
        self.plot_button = QPushButton("Построить график")
        self.plot_button.clicked.connect(self.plot_graph)
        layout.addWidget(self.plot_button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def plot_graph(self):
        try:
            a = float(self.input_a.text())
            b = float(self.input_b.text())
            n = int(self.input_n.text())
            func_ids = [int(f.strip()) for f in self.input_funcs.text().split(',') if f.strip().isdigit()]
            if a >= b or n <= 1 or any(fid not in functions for fid in func_ids):
                raise ValueError
            step = (b - a) / (n - 1)
            data = {}
            global min_x, max_x, min_y, max_y
            min_x, max_x = a, b
            min_y, max_y = float('inf'), float('-inf')
            for fid in func_ids:
                func, _ = functions[fid]
                points = [(x, func(x)) for x in [a + i * step for i in range(n)]]
                data[fid] = points
                min_y = min(min_y, min(y for _, y in points))
                max_y = max(max_y, max(y for _, y in points))
            self.graph_window = GraphWidget(data)
            self.graph_window.resize(800, 600)
            self.graph_window.show()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректные данные.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
