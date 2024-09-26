import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QComboBox, QTextEdit, QGridLayout)
from PyQt5.QtCore import QTimer, QTime
import matplotlib.pyplot as plt
from folium import Map
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWebEngineWidgets import QWebEngineView
import io
import folium

class SerialReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.serial = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_serial_data)

        self.latitudes = []
        self.longitudes = []
        self.altitudes = []
        self.discharge_volume = []
        self.gas_volume = []
        self.times = []
        self.start_time = QTime.currentTime()

    def initUI(self):
        self.setWindowTitle('浮空器控制平台')

        # 串口设置相关控件
        self.port_label = QLabel('串口:')
        self.baudrate_label = QLabel('波特率:')
        self.port_box = QComboBox()
        self.baudrate_box = QComboBox()
        self.baudrate_box.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.scan_ports()

        # 操作按钮
        self.start_button = QPushButton('开始读取')
        self.stop_button = QPushButton('停止读取')
        self.start_button.clicked.connect(self.start_reading)
        self.stop_button.clicked.connect(self.stop_reading)

        # 系统参数模块
        self.sensor_status_label = QLabel('传感器状态: 正常')
        self.main_control_status_label = QLabel('主控状态: 正常')
        self.comm_status_label = QLabel('测控与通信: 正常')

        # 球体参数模块
        self.gas_volume_label = QLabel('充气量: ')
        self.ballast_label = QLabel('压舱物: ')
        self.battery_label = QLabel('电量: ')

        # 标志位模块
        self.flight_status_label = QLabel('飞行状态: 平飞')
        self.parachute_status_label = QLabel('降落伞状态: 未开伞')
        self.ballast_device_label = QLabel('抛球装置: 未执行')

        # 实时数据模块
        self.altitude_label = QLabel('高度: 22000 米')
        self.temp_label = QLabel('舱外平均温度: -50 °C')
        self.humidity_label = QLabel('舱内湿度: 30 %')
        self.wind_speed_label = QLabel('风速: 5.3 m/s')
        self.ext_humidity_label = QLabel('舱外湿度: 9.23 %')
        self.pressure_label = QLabel('气压: 3538 Pa')

        # 地图显示窗口
        self.map_view = QWebEngineView()

        # 高度曲线显示
        self.canvas = FigureCanvas(plt.Figure())
        self.ax_altitude = self.canvas.figure.add_subplot(311)
        self.ax_gas_volume = self.canvas.figure.add_subplot(312)
        self.ax_discharge_volume = self.canvas.figure.add_subplot(313)

        # 发送数据
        self.send_port_label = QLabel('发送串口:')
        self.send_port_box = QComboBox()
        self.send_ports = serial.tools.list_ports.comports()
        self.send_port_box.addItems([port.device for port in self.send_ports])

        self.ballast_send_label = QLabel('抛物量:')
        self.ballast_send_edit = QTextEdit()
        self.ballast_send_edit.setMaximumHeight(30)  # 限制高度

        self.gas_volume_send_label = QLabel('排气量:')
        self.gas_volume_send_edit = QTextEdit()
        self.gas_volume_send_edit.setMaximumHeight(30)  # 限制高度

        self.send_button = QPushButton('发送数据')
        self.send_button.clicked.connect(self.send_serial_data)
        # 布局设置
        grid = QGridLayout()
        grid.addWidget(self.port_label, 0, 0)
        grid.addWidget(self.port_box, 0, 1)
        grid.addWidget(self.baudrate_label, 1, 0)
        grid.addWidget(self.baudrate_box, 1, 1)
        grid.addWidget(self.start_button, 2, 0, 1, 2)
        grid.addWidget(self.stop_button, 3, 0, 1, 2)

        grid.addWidget(QLabel('系统参数'), 4, 0)
        grid.addWidget(self.sensor_status_label, 5, 0, 1, 2)
        grid.addWidget(self.main_control_status_label, 6, 0, 1, 2)
        grid.addWidget(self.comm_status_label, 7, 0, 1, 2)

        grid.addWidget(QLabel('球体参数'), 8, 0)
        grid.addWidget(self.gas_volume_label, 9, 0, 1, 2)
        grid.addWidget(self.ballast_label, 10, 0, 1, 2)
        grid.addWidget(self.battery_label, 11, 0, 1, 2)

        grid.addWidget(QLabel('标志位'), 12, 0)
        grid.addWidget(self.flight_status_label, 13, 0, 1, 2)
        grid.addWidget(self.parachute_status_label, 14, 0, 1, 2)
        grid.addWidget(self.ballast_device_label, 15, 0, 1, 2)

        grid.addWidget(QLabel('实时数据'), 16, 0)
        grid.addWidget(self.altitude_label, 17, 0, 1, 2)
        grid.addWidget(self.temp_label, 18, 0, 1, 2)
        grid.addWidget(self.humidity_label, 19, 0, 1, 2)
        grid.addWidget(self.wind_speed_label, 20, 0, 1, 2)
        grid.addWidget(self.ext_humidity_label, 21, 0, 1, 2)
        grid.addWidget(self.pressure_label, 22, 0, 1, 2)

        data_layout = QVBoxLayout()
        data_layout.addWidget(QLabel('地图视图'))
        data_layout.addWidget(self.map_view)
        data_layout.addWidget(QLabel('数据曲线'))
        data_layout.addWidget(self.canvas)
        data_layout.addWidget(QLabel('接收到的数据:'))
        self.data_text_edit = QTextEdit()
        data_layout.addWidget(self.data_text_edit)
        # 发送数据布局
        self.send_layout = QVBoxLayout()
        self.send_layout.addWidget(self.send_port_label)
        self.send_layout.addWidget(self.send_port_box)
        self.send_layout.addWidget(self.ballast_send_label)
        self.send_layout.addWidget(self.ballast_send_edit)
        self.send_layout.addWidget(self.gas_volume_send_label)
        self.send_layout.addWidget(self.gas_volume_send_edit)
        self.send_layout.addWidget(self.send_button)
        main_layout = QHBoxLayout()
        main_layout.addLayout(grid)
        main_layout.addLayout(data_layout)
        main_layout.addLayout(self.send_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # 初始化地图
        self.init_map()

    def scan_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_box.clear()
        self.port_box.addItems([port.device for port in ports])

    def start_reading(self):
        port = self.port_box.currentText()
        baudrate = int(self.baudrate_box.currentText())

        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.timer.start(100)  # 每100毫秒读取一次

    def stop_reading(self):
        if self.serial:
            self.timer.stop()
            self.serial.close()

    def send_serial_data(self):
        send_port = self.send_port_box.currentText()
        ballast_value = self.ballast_send_edit.toPlainText()
        gas_volume_value = self.gas_volume_send_edit.toPlainText()

        if send_port and ballast_value and gas_volume_value:
            try:
                with serial.Serial(send_port, int(self.baudrate_box.currentText()), timeout=1) as ser:
                    # 生成发送的数据字符串，假设格式为 "BXX,ballast_value,gas_volume_value"
                    data_to_send = f"BXX,{ballast_value},{gas_volume_value}\n"
                    ser.write(data_to_send.encode())
                    print(f"发送数据: {data_to_send}")
            except Exception as e:
                print(f"发送数据失败: {e}")

    def read_serial_data(self):
        if self.serial.in_waiting:
            line = self.serial.readline().decode().strip()
            print(f"Received line: {line}")

            self.data_text_edit.append(line)  # 将接收到的数据添加到文本框中

            if 'MXX' in line:
                data = line.split(',')
                if len(data) >= 19:
                    lat, lon, alt = float(data[7]), float(data[6]), float(data[8])
                    discharge, gas_volume = float(data[-4]), float(data[-3])
                    time_str = data[-1]
                    hours, minutes, seconds = int(time_str[0:2]), int(time_str[2:4]), int(time_str[4:6])
                    time_in_seconds = hours * 3600 + minutes * 60 + seconds

                    self.latitudes.append(lat)
                    self.longitudes.append(lon)
                    self.altitudes.append(alt)
                    self.discharge_volume.append(discharge)
                    self.gas_volume.append(gas_volume)
                    self.times.append(time_in_seconds)


                    self.update_map()
                    self.plot_data()
                    self.update_system_status(data)

    def update_system_status(self, data):
        self.sensor_status_label.setText(f'传感器状态: {data[1]}')
        self.main_control_status_label.setText(f'主控状态: {data[2]}')
        self.comm_status_label.setText(f'测控与通信: {data[3]}')

        self.gas_volume_label.setText(f'充气量: {data[-3]} %')
        self.ballast_label.setText(f'压舱物: {data[-4]} %')

        flight_status = "平飞" if data[10] == "0" else "爬升/下降"
        parachute_status = "未开伞" if data[11] == "0" else "开伞"
        ballast_status = "未执行" if data[12] == "0" else "执行"

        self.flight_status_label.setText(f'飞行状态: {flight_status}')
        self.parachute_status_label.setText(f'降落伞状态: {parachute_status}')
        self.ballast_device_label.setText(f'抛球装置: {ballast_status}')

        # 实时数据更新
        self.altitude_label.setText(f'高度: {self.altitudes[-1]:.2f} 米')
        self.temp_label.setText(f'舱外平均温度: {data[4]} °C')
        self.humidity_label.setText(f'舱内湿度: {data[5]} %')
        self.wind_speed_label.setText(f'风速: {data[6]} m/s')
        self.ext_humidity_label.setText(f'舱外湿度: {data[7]} %')
        self.pressure_label.setText(f'气压: {data[8]} Pa')

    def update_map(self):
        # 更新地图
        if self.latitudes and self.longitudes:
            map_center = [self.latitudes[-1], self.longitudes[-1]]
            m = folium.Map(location=map_center, zoom_start=13)
            folium.Marker(location=map_center, popup=f'高度: {self.altitudes[-1]} 米').add_to(m)

            for lat, lon in zip(self.latitudes, self.longitudes):
                folium.CircleMarker(location=[lat, lon], radius=5, color='blue').add_to(m)

            # Convert map to HTML and display it
            map_html = io.BytesIO()
            m.save(map_html, close_file=False)
            self.map_view.setHtml(map_html.getvalue().decode())

    def plot_data(self):
        self.ax_altitude.clear()
        self.ax_gas_volume.clear()
        self.ax_discharge_volume.clear()
        # Convert seconds to HH:MM:SS for x-axis labels
        time_labels = [f'{int(t // 3600):02}:{int((t % 3600) // 60):02}:{int(t % 60):02}' for t in self.times]

        self.ax_altitude.plot(time_labels, self.altitudes, label='Altitude')
        self.ax_altitude.set_xlabel('Time (HH:MM:SS)')
        self.ax_altitude.set_ylabel('Altitude (m)')
        self.ax_altitude.legend()

        self.ax_gas_volume.plot(time_labels, self.gas_volume, label='Gas Volume', color='green')
        self.ax_gas_volume.set_xlabel('Time (HH:MM:SS)')
        self.ax_gas_volume.set_ylabel('Gas Volume (%)')
        self.ax_gas_volume.legend()

        self.ax_discharge_volume.plot(time_labels, self.discharge_volume, label='Discharge Volume', color='red')
        self.ax_discharge_volume.set_xlabel('Time (HH:MM:SS)')
        self.ax_discharge_volume.set_ylabel('Discharge Volume (%)')
        self.ax_discharge_volume.legend()

        self.canvas.draw()

    def init_map(self):
            # 初始化地图（世界地图）
            self.map = Map(location=[0, 0], zoom_start=2)
            data = io.BytesIO()
            self.map.save(data, close_file=False)
            self.map_view.setHtml(data.getvalue().decode())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    reader = SerialReader()
    reader.show()
    sys.exit(app.exec_())
