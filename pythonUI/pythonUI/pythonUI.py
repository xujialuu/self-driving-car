import tkinter
import tkinter.messagebox
import customtkinter
import requests

customtkinter.set_appearance_mode("System") 
customtkinter.set_default_color_theme("blue")
import time
import cv2 as cv
import numpy as np
from urllib.request import urlopen
import os
import datetime
import sys

class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()


        self.title("python上位机控制小车")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=1800,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_left.grid_rowconfigure(1, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="小车基本控制",
                                              text_font=("Roboto Medium", -16)).place(x=0, y=10, anchor='nw')  # font name and size in px

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="前进",
                                                command=self.button_qianjin,
                                                width=40, height=40,).place(x=70, y=50, anchor='nw')

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="后退",
                                                command=self.button_houtui,
                                                width=40, height=40,).place(x=70, y=150, anchor='nw')

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="左转",
                                                command=self.button_zuozhuan,
                                                width=40, height=40,).place(x=20, y=100, anchor='nw')

        self.button_4 = customtkinter.CTkButton(master=self.frame_left,
                                                text="右转",
                                                command=self.button_youzhuan,
                                                width=40, height=40,).place(x=120, y=100, anchor='nw')

        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="显示主题:")
        self.label_mode.grid(row=9, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Light", "Dark", "System"],
                                                        command=self.change_appearance_mode)
        self.optionmenu_1.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                text="电脑连接小车开发板控制程序",
                                                height=100,
                                                corner_radius=6,  # <- custom corner radius
                                                fg_color=("white", "gray38"),  # <- custom tuple-color
                                                justify=tkinter.LEFT)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_info)
        #self.progressbar.grid(row=1, column=0, sticky="ew", padx=15, pady=15)

        # ============ frame_right ============

        self.radio_var = tkinter.IntVar(value=0)

        self.label_radio_group = customtkinter.CTkLabel(master=self.frame_right,
                                                        text="车辆信息监控:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, pady=20, padx=10, sticky="")

        self.radio_button_1 = customtkinter.CTkButton(master=self.frame_right,
                                                        text = "打印车速与转角",
                                                        command=self.button_dayin,
                                                        )
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")

        self.slider_1 = customtkinter.CTkSlider(master=self.frame_right,
                                                from_=0,
                                                to=100,
                                                command=self.progressbar.set
                                                )
        self.slider_1.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        self.slider_2 = customtkinter.CTkSlider(master=self.frame_right,
                                                from_=0,
                                                to=100,
                                                command=self.progressbar.set)
        self.slider_2.grid(row=5, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        self.switch_1 = customtkinter.CTkLabel(master=self.frame_right,
                                                text="转角调整")
        self.switch_1.grid(row=4, column=2, columnspan=1, pady=10, padx=20, sticky="we")

        self.switch_2 = customtkinter.CTkLabel(master=self.frame_right,
                                                text="速度调整")
        self.switch_2.grid(row=5, column=2, columnspan=1, pady=10, padx=20, sticky="we")

        self.check_box_1 = customtkinter.CTkButton(master=self.frame_right,
                                                    text="直行",
                                                    command = self.button_zhixing)
        self.check_box_1.grid(row=6, column=0, pady=10, padx=20, sticky="w")

        self.check_box_2 = customtkinter.CTkButton(master=self.frame_right,
                                                    text="停止",
                                                    command = self.button_tingzhi)
        self.check_box_2.grid(row=6, column=1, pady=10, padx=20, sticky="w")

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="查看摄像头画面",
                                                border_width=2,  # <- custom border_width
                                                fg_color=None,  # <- no fg_color
                                                command=self.button_shexiang)
        self.button_5.grid(row=8, column=2, columnspan=1, pady=20, padx=20, sticky="we")


        self.optionmenu_1.set("Dark")
        self.slider_2.set(0.7)
        self.progressbar.set(0.5)

    def button_dayin(self):
        r = requests.get('http://192.168.4.1/read_speed')
        print(r.text)
        a = requests.get('http://192.168.4.1/read_angle')
        print(a.text)
    
    def button_qianjin(self):
        v = self.slider_2.value*100
        r = requests.post('http://192.168.4.1/motor_control?speed={}'.format(v))
    def button_houtui(self):
        v = -self.slider_2.value*100
        r = requests.post('http://192.168.4.1/motor_control?speed={}'.format(v))
    def button_zuozhuan(self):
        a = 90-self.slider_1.value*45
        r = requests.post('http://192.168.4.1/servo_control?angle={}'.format(a))
    def button_youzhuan(self):
        a = 90+self.slider_1.value*45
        r = requests.post('http://192.168.4.1/servo_control?angle={}'.format(a))
    def button_zhixing(self):
        a = 90
        v = self.slider_2.value*100
        p = requests.post('http://192.168.4.1/servo_control?angle={}'.format(a))
        r = requests.post('http://192.168.4.1/motor_control?speed={}'.format(v))
    def button_tingzhi(self):
        v = 0
        r = requests.post('http://192.168.4.1/motor_control?speed={}'.format(v))
    def button_shexiang(self):
        url = 'http://192.168.4.5:80/'
        CAMERA_BUFFRER_SIZE = 4096
        stream = urlopen(url)
        bts=b''
        i=0
        while True:    
            try:
                bts+=stream.read(CAMERA_BUFFRER_SIZE)
                jpghead=bts.find(b'\xff\xd8')
                jpgend=bts.find(b'\xff\xd9')
                if jpghead>-1 and jpgend>-1:
                    jpg=bts[jpghead:jpgend+2]
                    bts=bts[jpgend+2:]
                    img=cv.imdecode(np.frombuffer(jpg,dtype=np.uint8),cv.IMREAD_UNCHANGED)
                    cv.imshow("real-time camera",img)
            except Exception as e:
                print("Error:" + str(e))
                bts=b''
                stream=urlopen(url)
                continue
            k=cv.waitKey(1)
            if k & 0xFF == ord('s'):
                cv.imwrite(str(i) + ".jpg", img)
                i=i+1
            if k & 0xFF == ord('q'):
                break
        cv.destroyAllWindows()

    def change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def on_closing(self, event=0):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
