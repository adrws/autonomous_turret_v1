import zenoh, json, util.keys, sys
from PyQt6 import QtWidgets, QtCore
import numpy as np
import pyqtgraph as pg
from collections import deque

class LivePlot(QtWidgets.QMainWindow):
    def update_plot(self):
        x_data_np = np.array(self.x_data)
        y_data_np = np.array(self.y_data)
        self.line.setData(x_data_np, y_data_np)

    def __init__(self):
        super().__init__()

        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        self.plot_widget.setYRange(-320, 320)
        self.plot_widget.showGrid(x=True, y=True)

        self.line = self.plot_widget.plot(pen=pg.mkPen('r', width=2))
        pg.setConfigOptions(antialias=True)

        self.buffer_size = 500
        self.x_data = deque(maxlen=100)
        self.y_data = deque(maxlen=100)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)


if __name__ == "__main__":
    def camera_centering_cb(sample: zenoh.Sample):
        data = json.loads(sample.payload.to_string())
        error = int(data["error"])
        time = float(data["time"])
        win.x_data.append(time)
        win.y_data.append(error)     

    with zenoh.open(zenoh.Config()) as session:
        camera_centering_sub = session.declare_subscriber(util.keys.camera_centering_data, camera_centering_cb)

        app = QtWidgets.QApplication(sys.argv)
        win = LivePlot()
        win.show()
        sys.exit(app.exec())

    