import zenoh, json, config, sys
from PyQt6 import QtWidgets, QtCore
import numpy as np
import pyqtgraph as pg
from collections import deque

class LivePlots(QtWidgets.QMainWindow):
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

        self.line = self.plot_widget.plot(pen=pg.mkPen('g', width=2))
        pg.setConfigOptions(antialias=True)

        self.deadzone = 15  
        self.deadzone_upper = pg.InfiniteLine(pos=self.deadzone, angle=0, pen=pg.mkPen('r', style=QtCore.Qt.PenStyle.DashLine), labelOpts={'position': 0.95, 'color': 'y'})
        self.deadzone_lower = pg.InfiniteLine(pos=-self.deadzone, angle=0, pen=pg.mkPen('r', style=QtCore.Qt.PenStyle.DashLine), labelOpts={'position': 0.95, 'color': 'y'})
        self.plot_widget.addItem(self.deadzone_upper)
        self.plot_widget.addItem(self.deadzone_lower)

        self.buffer_size = 500
        self.x_data = deque(maxlen=100)
        self.y_data = deque(maxlen=100)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)


if __name__ == "__main__":
    def camera_centering_data_cb(sample: zenoh.Sample):
        data = json.loads(sample.payload.to_string())
        error = int(data["error"])
        time = float(data["time"])
        win.x_data.append(time)
        win.y_data.append(error)     

    with zenoh.open(zenoh.Config()) as session:
        camera_centering_sub = session.declare_subscriber(config.camera_centering_data, camera_centering_data_cb)

        app = QtWidgets.QApplication(sys.argv)
        win = LivePlots()
        win.show()
        sys.exit(app.exec())

    