from tkinter import *
from tkinter.messagebox import *
from tkinter import ttk
import sys
import serial
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser
import time
import os
import random

import ctypes

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams["axes.unicode_minus"] = False  # 设置正常显示符号
tempData = 0
humData = 0


class zsh_serial:
    def __init__(self):
        self.window = Tk()  # 实例化出一个父窗口
        self.com = serial.Serial()
        self.serial_combobox = None
        self.bound_combobox = None
        self.txt = None

    def ui(self):
        ############################################
        # 窗口配置
        ############################################
        # self.window = Tk()  # 实例化出一个父窗口
        self.window.title("串口调试助手")
        # self.window.iconbitmap(default='data\\COM.ico')  # 修改 logo
        width = self.window.winfo_screenwidth()
        height = self.window.winfo_screenheight()
        print(width, height)
        win = '{}x{}+{}+{}'.format(880, 800, width // 3, height // 5)  # {}x{} 窗口大小，+10 +10 定义窗口弹出时的默认展示位置
        self.window.geometry(win)
        self.window.resizable(False, False)

        # 调用api设置成由应用程序缩放
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # 调用api获得当前的缩放因子
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        # 设置缩放因子
        self.window.tk.call('tk', 'scaling', ScaleFactor / 75)

        ############################################
        # 串口设置子菜单 1
        ############################################

        # 串口设置
        group_serial_set = LabelFrame(self.window, text="串口设置")
        group_serial_set.grid(row=0, column=0, padx=10, pady=10)

        serial_label = Label(group_serial_set, text="串口号")
        serial_label.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        self.serial_combobox = ttk.Combobox(group_serial_set, width=8)
        self.serial_combobox['value'] = zsh_serial.getSerialPort()
        self.serial_combobox.grid(row=0, column=1, padx=10, pady=10)

        bound_label_set = Label(group_serial_set, text="波特率")
        bound_label_set.grid(row=1, column=0)
        self.bound_combobox = ttk.Combobox(group_serial_set, width=8)
        self.bound_combobox['value'] = ("9600", "19200", "38400", "57600", "115200", "128000")
        self.bound_combobox.grid(row=1, column=1)

        databits_label = Label(group_serial_set, text="数据位")
        databits_label.grid(row=2, column=0, pady=10)
        databits_combobox = ttk.Combobox(group_serial_set, width=8)
        databits_combobox['value'] = ("1", "1.5", "2")
        databits_combobox.grid(row=2, column=1)

        checkbits_label = Label(group_serial_set, text="校验位")
        checkbits_label.grid(row=3, column=0)
        checkbits_combobox = ttk.Combobox(group_serial_set, width=8)
        checkbits_combobox['value'] = ("None", "Odd", "Even")
        checkbits_combobox.grid(row=3, column=1)

        xxx_label = Label(group_serial_set, text="   ")
        xxx_label.grid(row=4, column=0, pady=1)

        # 接收设置
        recv_set = LabelFrame(self.window, text="接收设置")
        recv_set.grid(row=1, column=0, padx=10)

        recv_set_v = IntVar()
        recv_set_radiobutton1 = Radiobutton(recv_set, text="ASCII", variable=recv_set_v, value=1)
        recv_set_radiobutton1.grid(row=0, column=0, sticky=W, padx=10)
        recv_set_radiobutton2 = Radiobutton(recv_set, text="HEX", variable=recv_set_v, value=2)
        recv_set_radiobutton2.grid(row=0, column=1, sticky=W, padx=10)

        recv_set_v1 = IntVar()
        recv_set_v2 = IntVar()
        recv_set_v3 = IntVar()
        recv_set_checkbutton1 = Checkbutton(recv_set, text="自动换行", variable=recv_set_v1, onvalue=1, offvalue=2)
        recv_set_checkbutton1.grid(row=1, column=0, padx=10)
        recv_set_checkbutton2 = Checkbutton(recv_set, text="显示发送", variable=recv_set_v2, onvalue=1, offvalue=2)
        recv_set_checkbutton2.grid(row=2, column=0, padx=10)
        recv_set_checkbutton3 = Checkbutton(recv_set, text="显示时间", variable=recv_set_v3, onvalue=1, offvalue=2)
        recv_set_checkbutton3.grid(row=3, column=0, padx=10)

        # 串口操作
        group_serial_event = LabelFrame(self.window, text="串口操作")
        group_serial_event.grid(row=2, column=0, padx=10, pady=10)

        self.serial_btn_flag_str = StringVar()
        self.serial_btn_flag_str.set("串口未打开")
        label_name = Label(group_serial_event, textvariable=self.serial_btn_flag_str, bg='#ff001a', fg='#ffffff')
        label_name.grid(row=0, column=0, padx=55, pady=2)

        self.serial_btn_str = StringVar()
        self.serial_btn_str.set("打开串口")
        serial_btn = Button(group_serial_event, textvariable=self.serial_btn_str, command=self.hit1)
        serial_btn.grid(row=1, column=0, padx=55, pady=10)

        # 数据显示
        group_shuju = LabelFrame(self.window, text="串口操作")
        group_shuju.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

        serial_label = Label(group_shuju, text="接收区")
        serial_label.grid(row=0, padx=5, pady=5, sticky='w')
        self.txt = Text(group_shuju, width=70, height=18, font=("SimHei", 10))
        self.txt.grid(row=1, columnspan=2, padx=8, pady=5, sticky='s')
        serial_label = Label(group_shuju, text="发送区")
        serial_label.grid(row=2, padx=5, pady=5, sticky='w')

        self.serial_btn_send = StringVar()  # 添加发送按键
        self.serial_btn_send.set("发送")
        serial_btn = Button(group_shuju, textvariable=self.serial_btn_send, command=self.send_data)
        serial_btn.grid(row=2, column=1, padx=10, pady=5, sticky='E')
        self.txt1 = Text(group_shuju, width=70, height=7, font=("SimHei", 10))
        self.txt1.grid(row=3, columnspan=2, padx=8, pady=5, sticky='s')

        # 串口子菜单设置初值
        self.bound_combobox.set(self.bound_combobox['value'][0])
        self.serial_combobox.set(self.serial_combobox['value'][0])
        databits_combobox.set(databits_combobox['value'][0])
        checkbits_combobox.set(checkbits_combobox['value'][0])
        recv_set_v.set(2)
        recv_set_v1.set(1)
        recv_set_v2.set(2)
        recv_set_v3.set(2)

        ############################################
        # 配置tkinter样式
        ############################################
        # self.window.config(menu=menubar)

        ############################################
        # 退出检测
        ############################################
        def bye():
            self.window.destroy()

        self.window.protocol("WM_DELETE_WINDOW", bye)

        # 窗口循环显示
        self.window.mainloop()

    def readSerial(self, com):
        """
        读取串口数据
        :return:
        """
        global serialData
        while True:
            if self.com.in_waiting:
                textSetial = self.com.read(self.com.in_waiting)
                serialData = textSetial
                # print(textSetial)
                self.txt.config(state=NORMAL)
                self.txt.insert(END, textSetial)
                self.txt.config(state=DISABLED)
            # print("Debug: thread_readSerial is running")

    def hit1(self):
        """
        打开串口按钮回调
        """
        print(self.com.isOpen())
        if self.com.isOpen():
            self.com.close()
            print("--- 串口未打开 ---")
            self.serial_btn_flag_str.set("串口未打开")
            self.serial_btn_str.set("打开串口")
        else:
            self.com, ser_flag = self.openSerial(self.serial_combobox.get(), self.bound_combobox.get(), None)
            if ser_flag:
                print("--- 串口已打开 ---")
                self.serial_btn_flag_str.set("串口已打开")
                self.serial_btn_str.set("关闭串口")

    @staticmethod
    def getSerialPort():
        port = []
        portList = list(serial.tools.list_ports.comports())
        # print(portList)

        if len(portList) == 0:
            print("--- 无串口 ---")
            port.append('None')
        else:
            for comport in portList:
                # print(list(comport)[0])
                # print(list(comport)[1])
                port.append(list(comport)[0])
                pass
        return port

    def openSerial(self, port, bps, timeout):
        """
        打开串口
        :param port: 端口号
        :param bps: 波特率
        :param timeout: 超时时间
        :return: True or False
        """
        ser_flag = False
        try:
            # 打开串口
            self.com = serial.Serial(port, bps, timeout=timeout)
            if self.com.isOpen():
                ser_flag = True
                threading.Thread(target=self.readSerial, args=(self.com,)).start()
                # print("Debug: 串口已打开\n")
            # else:
            #     print("Debug: 串口未打开")
        except Exception as e:
            print("error: ", e)
            error = "error: {}".format(e)
            showerror('error', error)
        return self.com, ser_flag

    def send_data(self):
        """
        发送函数
        """
        global serial_send_Data
        serial_send_Data = self.txt1.get("1.0", END).rstrip()
        serial_send_Data = serial_send_Data + '\r\n'
        self.com.write(serial_send_Data.encode("gbk"))
        print("send data: ", serial_send_Data)
        # self.com.write('send string by serial\r\n'.encode("gbk"))
        # print("send data: ")

    def readSerial(self, com):
        """
        读取串口数据
        :return:
        """
        global serialData
        while True:
            if self.com.in_waiting:
                textSetial = self.com.read(self.com.in_waiting)
                serialData = textSetial
                # print(textSetial)
                self.txt.config(state=NORMAL)
                self.txt.insert(END, textSetial)
                self.txt.config(state=DISABLED)
            # print("Debug: thread_readSerial is running")

    def cleanSerial(self):
        self.txt.config(state=NORMAL)
        self.txt.delete("1.0", END)
        self.txt.config(state=DISABLED)


if __name__ == "__main__":
    mySerial = zsh_serial()
    mySerial.ui()
