import keyboard
import time
import threading
import subprocess
import re

from customtkinter import *
from PIL import Image
from tkinter import messagebox
from EV3connect import EV3connect
from ev3_dc.exceptions import NoEV3
from helpers import Logger, resolve_path , information


root = CTk()

# Define general app settings
# ---------------------------
root.state('zoomed')
root.title("EV3connect")
root.iconbitmap(resolve_path(__file__, "ev3/a_logo.ico"))
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
w = ws / 1.5
h = hs / 1.5
root.focus_set()
root.minsize(width=int(ws / 1.2), height=int(hs / 1.2))
root.after(0, lambda: root.wm_state('zoomed'))


class header(Logger):

    def __init__(self):
        super().__init__("header", debug=False)
        self.head_frame = CTkFrame(root, fg_color="#dbdbdb", corner_radius=0)
        self.head_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self.info_header = CTkFrame(self.head_frame, fg_color="#ffffff", corner_radius=25)
        self.info_header.place(relx=0.25, rely=0.2, relwidth=0.5, relheight=0.6)
        self.info = CTkLabel(self.info_header, text="⛔", text_color="#000000", height=40, font=("Helvetica", 20))
        self.info.pack()

    def stop(self):
        self.head_frame.destroy()


class ev3_connection(Logger):
    def __init__(self,mac):
        super().__init__("ev3_connection")
        try:
            self.ev3_brick = EV3connect(mac)
            self.logger.info(f"Connected to EV3 with MAC: {mac}")
        except NoEV3:
            self.logger.error("No EV3 device found!\nPlease connect a valid EV3 device and try again.")
            self.error_alert("No EV3 device found!\nPlease connect a valid EV3 device and try again.")
            return
        #Variables
        self.old_sensors = None
        self.old_motors = None

        #Initialise Graphical User Interface
        root.bind("<KeyPress>", lambda event: self.on_key_press(event))
        root.bind("<KeyRelease>", lambda event: self.on_key_release(event))

        self.twv = False

        self.motor_vars = {
            "motor_a": IntVar(value=0),
            "motor_b": IntVar(value=0),
            "motor_c": IntVar(value=0),
            "motor_d": IntVar(value=0)
        }


        self.key_binds = dict(a_for=None, b_for=None, c_for=None, d_for=None, a_back=None, b_back=None, c_back=None,d_back=None)

        self.ev3_display = CTkFrame(root, fg_color="#ffffff", corner_radius=0)
        self.ev3_display.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.logo = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/a_ev3.png')),size=(int(w / 4), int(w / 13))))
        self.logo.place(relx=0.5, rely=0.15, anchor=CENTER)

        self.framea1 = CTkFrame(self.ev3_display, fg_color="#ffffff", border_color="#7f7f7f", border_width=20,corner_radius=0).place(relx=0.18, rely=0.445, relwidth=0.3, relheight=0.39,anchor=CENTER)
        self.frameb1 = CTkFrame(self.ev3_display, fg_color="#ffffff", border_color="#7f7f7f", border_width=20,corner_radius=0).place(relx=0.5, rely=0.55, relwidth=0.3, relheight=0.6, anchor=CENTER)
        self.framec2 = CTkFrame(self.ev3_display, fg_color="#ffffff", border_color="#7f7f7f", border_width=20,corner_radius=0).place(relx=0.82, rely=0.655, relwidth=0.3, relheight=0.39,anchor=CENTER)
        self.framec1 = CTkFrame(self.ev3_display, fg_color="#ffffff", border_color="#7f7f7f", border_width=20,corner_radius=0).place(relx=0.82, rely=0.34, relwidth=0.3, relheight=0.18,anchor=CENTER)
        self.framea2 = CTkFrame(self.ev3_display, fg_color="#ffffff", border_color="#7f7f7f", border_width=20,corner_radius=0).place(relx=0.18, rely=0.76, relwidth=0.3, relheight=0.18,anchor=CENTER)

        self.colortypemenu_var = StringVar(value="Static")
        self.colortypemenu = CTkOptionMenu(self.ev3_display, dynamic_resizing=True,values=["Static", "Flash", "Pulse", "Off"], variable=self.colortypemenu_var)
        self.colortypemenu.place(relx=0.7, rely=0.35, anchor=W)
        self.colormenu_var = StringVar(value="Green")
        self.colormenu = CTkOptionMenu(self.ev3_display, dynamic_resizing=True, values=["Green", "Red", "Orange"],variable=self.colormenu_var)
        self.colormenu.place(relx=0.79, rely=0.35, anchor=W)
        self.color_activate = CTkButton(self.ev3_display, fg_color="#3b8ed0", text="💡", font=("Arial Black", 30),command=lambda: self.color_button())
        self.color_activate.place(relx=0.88, rely=0.35, relwidth=0.03, relheight=0.03, anchor=W)
        self.colorbox = CTkLabel(self.ev3_display, text="Sound", text_color="#000000", font=("Arial Black", 22)).place(relx=0.7, rely=0.51, anchor=W)
        self.displaybox = CTkLabel(self.ev3_display, text="Color", text_color="#000000", font=("Arial Black", 22)).place(relx=0.7, rely=0.3, anchor=W)

        self.soundmenu_var = StringVar(value="Startup")
        self.soundmenu = CTkOptionMenu(self.ev3_display, dynamic_resizing=True,values=["Startup", "Power Down", "Overpower Alert", "General Alarm","Download Succes", "Click"],variable=self.soundmenu_var)
        self.soundmenu.place(relx=0.7825, rely=0.6725, anchor=W)
        self.sound_activate = CTkButton(self.ev3_display, fg_color="#3b8ed0", text="🔊", font=("Arial Black", 30),command=lambda: self.play_sounds())
        self.sound_activate.place(relx=0.895, rely=0.6725, relwidth=0.03, relheight=0.03, anchor=W)
        self.volumebox = CTkLabel(self.ev3_display, text="Volume",text_color="#000000", font=("Arial", 18))
        self.volumebox.place(relx=0.72, rely=0.575, anchor=W)
        self.volume_percent = CTkLabel(self.ev3_display, text="60%",text_color="#000000", font=("Arial", 18))
        self.volume_percent.place(relx=0.9, rely=0.575, anchor=W)
        self.volume_bar = CTkSlider(self.ev3_display, bg_color="#ffffff", number_of_steps=9, command=self.volume,from_=10, to=100)
        self.volume_bar.set(60)
        self.volume_bar.place(relx=0.78, rely=0.575, anchor=W)
        self.tone_percent = CTkLabel(self.ev3_display, text="4000hz",text_color="#000000", font=("Arial", 18))
        self.tone_percent.place(relx=0.72, rely=0.77, anchor=W)
        self.tone_bar = CTkSlider(self.ev3_display, bg_color="#ffffff", number_of_steps=39, command=self.tone,from_=250, to=10000)
        self.tone_bar.set(4000)
        self.tone_bar.place(relx=0.78, rely=0.77, anchor=W)
        self.tone_activate = CTkButton(self.ev3_display, fg_color="#3b8ed0", text="🔊", font=("Arial Black", 30),command=lambda: self.ev3_brick.Tone(frequency=self.tone_bar.get(),volume=int(self.volume_bar.get())))
        self.tone_activate.place(relx=0.895, rely=0.77, relwidth=0.03, relheight=0.03, anchor=W)
        self.soundbox = CTkLabel(self.ev3_display, text="Sound",text_color="#000000", font=("Arial", 18))
        self.soundbox.place(relx=0.72, rely=0.6725, anchor=W)

        self.one = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_1f.png')), size=(int(w / 18), int(w / 18))))
        self.one.place(relx=0.09, rely=0.35, anchor=CENTER)
        self.two = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_2f.png')), size=(int(w / 18), int(w / 18))))
        self.two.place(relx=0.15, rely=0.35, anchor=CENTER)
        self.three = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_3f.png')), size=(int(w / 18), int(w / 18))))
        self.three.place(relx=0.21, rely=0.35, anchor=CENTER)
        self.four = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_4f.png')), size=(int(w / 18), int(w / 18))))
        self.four.place(relx=0.27, rely=0.35, anchor=CENTER)

        self.one_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.one_pic.place(relx=0.09, rely=0.47, anchor=CENTER)
        self.two_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.two_pic.place(relx=0.15, rely=0.47, anchor=CENTER)
        self.three_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.three_pic.place(relx=0.21, rely=0.47, anchor=CENTER)
        self.four_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.four_pic.place(relx=0.27, rely=0.47, anchor=CENTER)

        self.one_data = CTkLabel(self.ev3_display, text_color="#000000", text="", font=("Arial Black", 18))
        self.one_data.place(relx=0.09, rely=0.56, anchor=CENTER)
        self.two_data = CTkLabel(self.ev3_display, text_color="#000000", text="", font=("Arial Black", 18))
        self.two_data.place(relx=0.15, rely=0.56, anchor=CENTER)
        self.three_data = CTkLabel(self.ev3_display, text_color="#000000", text="", font=("Arial Black", 18))
        self.three_data.place(relx=0.21, rely=0.56, anchor=CENTER)
        self.four_data = CTkLabel(self.ev3_display, text_color="#000000", text="", font=("Arial Black", 18))
        self.four_data.place(relx=0.27, rely=0.56, anchor=CENTER)

        self.a_for = CTkButton(self.ev3_display,hover=False,fg_color="#3b8ed0", text="⤊", font=("Arial Black", 30))
        self.a_for.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_a", self.a_for, 1))
        self.a_for.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_a", self.a_for))
        self.a_for.place(relx=0.41, rely=0.525, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.b_for = CTkButton(self.ev3_display,hover=False, fg_color="#3b8ed0", text="⤊", font=("Arial Black", 30))
        self.b_for.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_b", self.b_for, 1))
        self.b_for.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_b", self.b_for))
        self.b_for.place(relx=0.47, rely=0.525, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.c_for = CTkButton(self.ev3_display,hover=False, fg_color="#3b8ed0", text="⤊", font=("Arial Black", 30))
        self.c_for.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_c", self.c_for, 1))
        self.c_for.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_c", self.c_for))
        self.c_for.place(relx=0.53, rely=0.525, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.d_for = CTkButton(self.ev3_display,hover=False, fg_color="#3b8ed0", text="⤊", font=("Arial Black", 30))
        self.d_for.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_d", self.d_for, 1))
        self.d_for.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_d", self.d_for))
        self.d_for.place(relx=0.59, rely=0.525, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.a_back = CTkButton(self.ev3_display,hover=False, fg_color="#3b8ed0", text="⤋", font=("Arial Black", 30))
        self.a_back.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_a", self.a_back, -1))
        self.a_back.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_a", self.a_back))
        self.a_back.place(relx=0.41, rely=0.675, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.b_back = CTkButton(self.ev3_display,hover=False, fg_color="#3b8ed0", text="⤋", font=("Arial Black", 30))
        self.b_back.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_b", self.b_back, -1))
        self.b_back.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_b", self.b_back))
        self.b_back.place(relx=0.47, rely=0.675, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.c_back = CTkButton(self.ev3_display,hover=False, fg_color="#3b8ed0", text="⤋", font=("Arial Black", 30))
        self.c_back.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_c", self.c_back, -1))
        self.c_back.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_c", self.c_back))
        self.c_back.place(relx=0.53, rely=0.675, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.d_back = CTkButton(self.ev3_display,hover=False, fg_color="#3b8ed0", text="⤋", font=("Arial Black", 30))
        self.d_back.bind("<ButtonPress-1>", lambda event: self.on_button_press(event, "motor_d", self.d_back, -1))
        self.d_back.bind("<ButtonRelease-1>", lambda event: self.on_button_release(event, "motor_d", self.d_back))
        self.d_back.place(relx=0.59, rely=0.675, relwidth=0.03, relheight=0.03, anchor=CENTER)

        self.a_for_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.a_for_bind, "a_for"))
        self.a_for_bind.place(relx=0.41, rely=0.45, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.b_for_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.b_for_bind, "b_for"))
        self.b_for_bind.place(relx=0.47, rely=0.45, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.c_for_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.c_for_bind, "c_for"))
        self.c_for_bind.place(relx=0.53, rely=0.45, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.d_for_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.d_for_bind, "d_for"))
        self.d_for_bind.place(relx=0.59, rely=0.45, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.a_back_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.a_back_bind, "a_back"))
        self.a_back_bind.place(relx=0.41, rely=0.75, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.b_back_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.b_back_bind, "b_back"))
        self.b_back_bind.place(relx=0.47, rely=0.75, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.c_back_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.c_back_bind, "c_back"))
        self.c_back_bind.place(relx=0.53, rely=0.75, relwidth=0.03, relheight=0.03, anchor=CENTER)
        self.d_back_bind = CTkButton(self.ev3_display,hover=False, text="Key",command=lambda: self.binder(self.d_back_bind, "d_back"))
        self.d_back_bind.place(relx=0.59, rely=0.75, relwidth=0.03, relheight=0.03, anchor=CENTER)

        self.a = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_af.png')), size=(int(w / 18), int(w / 18))))
        self.a.place(relx=0.41, rely=0.35, anchor=CENTER)
        self.b = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_bf.png')), size=(int(w / 18), int(w / 18))))
        self.b.place(relx=0.47, rely=0.35, anchor=CENTER)
        self.c = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_cf.png')), size=(int(w / 18), int(w / 18))))
        self.c.place(relx=0.53, rely=0.35, anchor=CENTER)
        self.d = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/b_df.png')), size=(int(w / 18), int(w / 18))))
        self.d.place(relx=0.59, rely=0.35, anchor=CENTER)

        self.a_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.a_pic.place(relx=0.41, rely=0.6, anchor=CENTER)
        self.b_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.b_pic.place(relx=0.47, rely=0.6, anchor=CENTER)
        self.c_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.c_pic.place(relx=0.53, rely=0.6, anchor=CENTER)
        self.d_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="")
        self.d_pic.place(relx=0.59, rely=0.6, anchor=CENTER)

        self.twoweel_btn = CTkButton(self.ev3_display, text="Two Wheel Vehicle", command=lambda: self.twv_open())
        self.twoweel_btn.place(relx=0.5, rely=0.81, anchor=CENTER)

        self.info_1 = CTkLabel(self.ev3_display, text_color="#000000", text="MAC: ", font=("Arial Black", 18))
        self.info_1.place(relx=0.06, rely=0.71, anchor=W)
        self.info_2 = CTkLabel(self.ev3_display, text_color="#000000", text="Total Memory: ", font=("Arial Black", 18))
        self.info_2.place(relx=0.06, rely=0.74, anchor=W)
        self.info_3 = CTkLabel(self.ev3_display, text_color="#000000", text="Free Memory: ", font=("Arial Black", 18))
        self.info_3.place(relx=0.06, rely=0.77, anchor=W)
        self.info_4 = CTkLabel(self.ev3_display, text_color="#000000", text="Version: ", font=("Arial Black", 18))
        self.info_4.place(relx=0.06, rely=0.8, anchor=W)
        self.header = header()
        background_thread = threading.Thread(target=self.update_sensors, daemon=True)
        background_thread.start()
        background_thread2 = threading.Thread(target=self.update_motors, daemon=True)
        background_thread2.start()
        background_thread3 = threading.Thread(target=self.update_info, daemon=True)
        background_thread3.start()

    @staticmethod
    def error_alert(message:str):
        messagebox.showerror("Error", message)

    def twv_close(self):
        self.twv = False
        self.twoWheelVFrame.place_forget()
        self.control_btn.place_forget()
        self.robot_pic.place_forget()
        self.twoWheelVText.place_forget()
        self.wasd_pic.place_forget()

    def twv_open(self):
        self.twv = True
        self.twoWheelVFrame = CTkFrame(self.ev3_display, fg_color="#ffffff", border_color="#7f7f7f", border_width=20,corner_radius=0)
        self.twoWheelVFrame.place(relx=0.5, rely=0.55, relwidth=0.3, relheight=0.6, anchor=CENTER)
        self.control_btn = CTkButton(self.ev3_display, text="Control Panel", command=lambda: self.twv_close())
        self.control_btn.place(relx=0.5, rely=0.81, anchor=CENTER)
        self.robot_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__, 'ev3/a_robot.png')),size=(int(w / 3.5), int(w / 3.5))))
        self.robot_pic.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.twoWheelVText = CTkLabel(self.ev3_display, bg_color="#ffffff", text="Movement Motors A & B (left to right)",font=("Arial Black", 15))
        self.twoWheelVText.place(relx=0.5, rely=0.675, anchor=CENTER)
        self.wasd_pic = CTkLabel(self.ev3_display, bg_color="#ffffff", text="",image=CTkImage(Image.open(resolve_path(__file__,'ev3/a_wasd.png')), size=(int(w / 8), int(w / 16))))
        self.wasd_pic.place(relx=0.5, rely=0.7375, anchor=CENTER)

    def try_motor_func(self, func, direction, speed=90):
        try:
            return func(direction=direction, speed=speed)
        except Exception as e:
            self.logger.error(e)


    def on_key_press(self, event):
        if not self.twv:
            if self.key_binds["a_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorA, direction=1, speed=100)
                self.a_for.configure(fg_color="#ff0000")
            if self.key_binds["b_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorB, direction=1, speed=100)
                self.b_for.configure(fg_color="#ff0000")
            if self.key_binds["c_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorC, direction=1, speed=100)
                self.c_for.configure(fg_color="#ff0000")
            if self.key_binds["d_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorD, direction=1, speed=100)
                self.d_for.configure(fg_color="#ff0000")
            if self.key_binds["a_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorA, direction=-1, speed=100)
                self.a_back.configure(fg_color="#ff0000")
            if self.key_binds["b_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorB, direction=-1, speed=100)
                self.b_back.configure(fg_color="#ff0000")
            if self.key_binds["c_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorC, direction=-1, speed=100)
                self.c_back.configure(fg_color="#ff0000")
            if self.key_binds["d_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorD, direction=-1, speed=100)
                self.d_back.configure(fg_color="#ff0000")
        elif self.twv:
            if event.keysym == "w":
                self.try_motor_func(self.ev3_brick.MotorA, direction=1, speed=100)
                self.try_motor_func(self.ev3_brick.MotorB, direction=1, speed=100)
            if event.keysym == "a":
                self.try_motor_func(self.ev3_brick.MotorA, direction=-1, speed=100)
                self.try_motor_func(self.ev3_brick.MotorB, direction=1, speed=100)
            if event.keysym == "s":
                self.try_motor_func(self.ev3_brick.MotorA, direction=-1, speed=100)
                self.try_motor_func(self.ev3_brick.MotorB, direction=-1, speed=100)
            if event.keysym == "d":
                self.try_motor_func(self.ev3_brick.MotorA, direction=1, speed=100)
                self.try_motor_func(self.ev3_brick.MotorB, direction=-1, speed=100)

    def on_key_release(self, event):
        if not self.twv:
            if self.key_binds["a_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorA, 0)
                self.a_for.configure(fg_color="#3b8ed0")
            if self.key_binds["b_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorB, 0)
                self.b_for.configure(fg_color="#3b8ed0")
            if self.key_binds["c_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorC, 0)
                self.c_for.configure(fg_color="#3b8ed0")
            if self.key_binds["d_for"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorD, 0)
                self.d_for.configure(fg_color="#3b8ed0")
            if self.key_binds["a_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorA, 0)
                self.a_back.configure(fg_color="#3b8ed0")
            if self.key_binds["b_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorB, 0)
                self.b_back.configure(fg_color="#3b8ed0")
            if self.key_binds["c_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorC, 0)
                self.c_back.configure(fg_color="#3b8ed0")
            if self.key_binds["d_back"] == event.keysym:
                self.try_motor_func(self.ev3_brick.MotorD, 0)
                self.d_back.configure(fg_color="#3b8ed0")
        elif self.twv:
            self.try_motor_func(self.ev3_brick.MotorA, 0)
            self.try_motor_func(self.ev3_brick.MotorB, 0)
            self.try_motor_func(self.ev3_brick.MotorC, 0)
            self.try_motor_func(self.ev3_brick.MotorD, 0)

    def on_button_press(self, event, motor_name, button, value):
        self.motor_vars[motor_name].set(value)
        button.configure(fg_color="#ff0000")

        if motor_name == "motor_a":
            self.try_motor_func(self.ev3_brick.MotorA,self.motor_vars["motor_a"].get())
        elif motor_name == "motor_b":
            self.try_motor_func(self.ev3_brick.MotorB,self.motor_vars["motor_b"].get())
        elif motor_name == "motor_c":
            self.try_motor_func(self.ev3_brick.MotorC,self.motor_vars["motor_c"].get())
        elif motor_name == "motor_d":
            self.try_motor_func(self.ev3_brick.MotorD,self.motor_vars["motor_d"].get())



    def on_button_release(self, event, motor_name, button):
        self.motor_vars[motor_name].set(0)
        button.configure(fg_color="#3b8ed0")

        if motor_name == "motor_a":
            self.try_motor_func(self.ev3_brick.MotorA, 0)
        elif motor_name == "motor_b":
            self.try_motor_func(self.ev3_brick.MotorB, 0)
        elif motor_name == "motor_c":
            self.try_motor_func(self.ev3_brick.MotorC, 0)
        elif motor_name == "motor_d":
            self.try_motor_func(self.ev3_brick.MotorD, 0)

    def volume(self, value):
        self.volume_percent.configure(text=f"{round(value)}%")

    def tone(self, value):
        self.tone_percent.configure(text=f"{round(value)}hz")

    def color_button(self):
        option_type = self.colortypemenu.get()
        led_type = option_type.lower()

        color_type = self.colormenu.get()
        color = color_type.lower()

        self.ev3_brick.Led(color=color, action_type=led_type)

    def play_sounds(self):
        file = self.soundmenu.get()
        path = ''
        if file == "Startup":
            path = './ui/Startup.rsf'
        elif file == "Power Down":
            path = './ui/PowerDown.rsf'
        elif file == "Overpower Alert":
            path = './ui/OverpowerAlert.rsf'
        elif file == "General Alarm":
            path = './ui/GeneralAlarm.rsf'
        elif file == "Download Succes":
            path = './ui/DownloadSucces.rsf'
        elif file == "Click":
            path = './ui/Click.rsf'

        self.ev3_brick.Sound(path=path, loudness=int(self.volume_bar.get()))



    def binder(self, button, identifier):
        button.configure(fg_color="#ff0000")

        def on_key(event):
            key_press = event.name
            keyboard.unhook_all()
            if key_press == "esc" or key_press == "entf":
                self.key_binds[identifier] = None
                button.configure(text="Keybind")
                button.configure(fg_color="#3b8ed0")
            else:
                self.key_binds[identifier] = key_press
                button.configure(text=key_press)
                button.configure(fg_color="#36719f")

        keyboard.hook(on_key)

    def update_motors(self):
        self.old_motors = dict(port_1=None, port_2=None, port_3=None, port_4=None)
        while True:
            motors = self.ev3_brick.MotorsAsDict()
            if motors != self.old_motors:
                ports = ["", "", "", ""]
                icons = ["", "", "", ""]
                char = ""
                for x in range(4):
                    if x + 1 == 1:
                        char = "a"
                    if x + 1 == 2:
                        char = "b"
                    if x + 1 == 3:
                        char = "c"
                    if x + 1 == 4:
                        char = "d"

                    if motors[f"port_{x + 1}"] is None:
                        ports[x] = f"b_{char}f.png"
                    else:
                        ports[x] = f"b_{char}t.png"

                    if motors[f"port_{x + 1}"] == 8:
                        icons[x] = CTkImage(Image.open(resolve_path(__file__, 'ev3/c_medium.png')),
                                            size=(int(w / 18), int(w / 18)))
                    elif motors[f"port_{x + 1}"] == 7:
                        icons[x] = CTkImage(Image.open(resolve_path(__file__, 'ev3/c_large.png')),
                                            size=(int(w / 18), int(w / 18)))
                    else:
                        icons[x] = None

                self.a.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[0]}')), size=(int(w / 18), int(w / 18))))
                self.b.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[1]}')), size=(int(w / 18), int(w / 18))))
                self.c.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[2]}')), size=(int(w / 18), int(w / 18))))
                self.d.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[3]}')), size=(int(w / 18), int(w / 18))))
                self.a_pic.configure(image=icons[0])
                self.b_pic.configure(image=icons[1])
                self.c_pic.configure(image=icons[2])
                self.d_pic.configure(image=icons[3])

                self.old_motors = motors
            time.sleep(0.05)

    def update_sensors(self):
        self.old_sensors = dict(port_1=None, port_2=None, port_3=None, port_4=None)
        while True:
            sensors = self.ev3_brick.SensorsAsDict()
            if not sensors["port_1"] == self.old_sensors["port_1"] or not sensors["port_2"] == self.old_sensors["port_2"] or not sensors["port_3"] == self.old_sensors["port_3"] or not sensors["port_4"] == self.old_sensors["port_4"]:
                ports = ["", "", "", ""]
                icons = ["", "", "", ""]

                for x in range(4):

                    if sensors[f"port_{x + 1}"] is None:
                        ports[x] = f"b_{x + 1}f.png"
                    else:
                        ports[x] = f"b_{x + 1}t.png"

                    if sensors[f"port_{x + 1}"] == 16:
                        icons[x] = CTkImage(Image.open(resolve_path(__file__, 'ev3/c_touch.png')),
                                            size=(int(w / 20), int(w / 20)))
                    elif sensors[f"port_{x + 1}"] == 29:
                        icons[x] = CTkImage(Image.open(resolve_path(__file__, 'ev3/c_color.png')),
                                            size=(int(w / 20), int(w / 20)))
                    elif sensors[f"port_{x + 1}"] == 30:
                        icons[x] = CTkImage(Image.open(resolve_path(__file__, 'ev3/c_ultrasonic.png')),
                                            size=(int(w / 20), int(w / 20)))
                    elif sensors[f"port_{x + 1}"] == 32:
                        icons[x] = CTkImage(Image.open(resolve_path(__file__, 'ev3/c_gyro.png')), size=(int(w / 20), int(w / 20)))
                    elif sensors[f"port_{x + 1}"] == 33:
                        icons[x] = CTkImage(Image.open(resolve_path(__file__, 'ev3/c_ir.png')), size=(int(w / 20), int(w / 20)))
                    else:
                        icons[x] = None
                self.one.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[0]}')), size=(int(w / 18), int(w / 18))))
                self.two.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[1]}')), size=(int(w / 18), int(w / 18))))
                self.three.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[2]}')), size=(int(w / 18), int(w / 18))))
                self.four.configure(
                    image=CTkImage(Image.open(resolve_path(__file__, f'ev3/{ports[3]}')), size=(int(w / 18), int(w / 18))))
                self.one_pic.configure(image=icons[0])
                self.two_pic.configure(image=icons[1])
                self.three_pic.configure(image=icons[2])
                self.four_pic.configure(image=icons[3])

                self.old_sensors = sensors

            if sensors[f"port_1"] is not None:
                self.one_data.configure(text=sensors["data_1"])
            else:
                self.one_data.configure(text="")
            if sensors[f"port_2"] is not None:
                self.two_data.configure(text=sensors["data_2"])
            else:
                self.two_data.configure(text="")
            if sensors[f"port_3"] is not None:
                self.three_data.configure(text=sensors["data_3"])
            else:
                self.three_data.configure(text="")
            if sensors[f"port_4"] is not None:
                self.four_data.configure(text=sensors["data_4"])
            else:
                self.four_data.configure(text="")

            time.sleep(0.05)

    def update_info(self):
        while True:
            info = self.ev3_brick.Status()
            self.header.info.configure(text=info["name"] + "  -  " + str(info["percentage"]) + "%")
            self.info_1.configure(text=f"MAC: {info['mac']}")
            self.info_2.configure(text=f"Total Memory: {info['memory_total']}kb")
            self.info_3.configure(text=f"Free Memory: {info['memory_free']}kb")
            self.info_4.configure(text=f"Version: {info['version']}")

            time.sleep(1)

    def stop(self):
        try:
            for widget in self.ev3_display.winfo_children():
                widget.place_forget()
                widget.destroy()
            self.ev3_display.place_forget()
            self.ev3_display.destroy()
        except Exception as e:
            self.logger.error(e)


class index(Logger):
    def __init__(self):
        super().__init__("index")
        information()
        self.no_devices_counter = 0
        self.cycle = 0
        self.nearby_devices = None
        self.ev3_instance = None
        self.no_display = CTkFrame(root, fg_color="#ffffff")
        self.no_display.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.text = CTkLabel(self.no_display, text="No Device connected", font=("Arial", 20), text_color="#cbcbcb")
        self.text.place(relx=0.5, rely=0.1, anchor=CENTER)
        self.text2 = CTkLabel(self.no_display, text="Turn on Bluetooth and connect to a device", font=("Arial", 20),text_color="#cbcbcb")
        self.text2.place(relx=0.5, rely=0.125, anchor=CENTER)
        self.frame = CTkFrame(self.no_display, corner_radius=10, fg_color="#cbcbcb")
        self.frame.place(relx=0.5, rely=0.575, relwidth=0.25, relheight=0.8, anchor=CENTER)
        self.button_frame = CTkFrame(self.no_display, corner_radius=0, fg_color="#cbcbcb", bg_color="#cbcbcb")
        self.button_frame.place(relx=0.5, rely=0.6, relwidth=0.25, relheight=0.725, anchor=CENTER)
        self.menu_header = CTkLabel(self.no_display, fg_color="#cbcbcb", text="Devices", font=("Arial Black", 20),text_color="#000000")
        self.menu_header.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.reload_button = CTkButton(self.no_display, command=self.reload, text="↻", bg_color="#cbcbcb",font=("Arial Black", 20), fg_color="#cbcbcb", corner_radius=0,hover_color="#bdbdbd", text_color="#000000")
        self.reload_button.place(relx=0.6, rely=0.187, relwidth=0.02, relheight=0.03)
        self.reload()

    @staticmethod
    def error_alert(message:str):
        messagebox.showerror("Error", message)

    
    def check_bluetooth(self,status):
        if "Bluetooth off" in status:
            self.logger.warning("Bluetooth is off!")
            self.error_alert("Bluetooth is off!")
        if "No devices found" in status:
            self.logger.warning("No devices found!\nDevice may not paired with Ev3!")
            self.error_alert("No devices found!\nDevice may not paired with Ev3!")

    def bluetooth_scan(self, executable_path):
        try:
            # Run the executable and capture output
            result = subprocess.run(executable_path, capture_output=True, text=True, check=True)
            # Process the output using regex
            output_dict = {}

            # Match status line
            status_match = re.search(r'Status:\s*(.*)', result.stdout)
            if status_match:
                output_dict["status"] = status_match.group(1).strip()

            # Find all devices and their addresses
            devices = []
            device_pattern = re.compile(r'Device Name:\s*(.*)\n\s*Address:\s*(.*)')

            # Use re.finditer to find matches
            for match in device_pattern.finditer(result.stdout):
                device_name = match.group(1).strip()
                address = match.group(2).strip()

                # Reverse the MAC address
                reversed_address = ':'.join(reversed(address.split(':')))

                devices.append((str(reversed_address), str(device_name)))

            output_dict["devices"] = devices if devices else []

            return output_dict

        except subprocess.CalledProcessError as e:
            self.logger.error(e)
            return {"status": "Error", "message": str(e)}



    def start_bluetooth_scan(self):
        def run_scan():
            blueout = self.bluetooth_scan(resolve_path(__file__, 'bluetooth.exe'))
            self.update_clients(blueout["devices"])
            self.check_bluetooth(blueout["status"])

        scan_thread = threading.Thread(target=run_scan)
        scan_thread.start()

    def update_clients(self, name_list):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        for name in name_list:
            button = CTkButton(self.button_frame, text=name, corner_radius=0, fg_color="#cbcbcb", hover_color="#bdbdbd",width=320, font=("Arial", 20), height=50, text_color="#000000",command=lambda n=name: self.connect(n))
            button.pack(pady=5)
        self.reload_button.configure(state="normal")

    def connect(self, name):
            self.ev3_instance = ev3_connection(name[0])
        

    def reload(self):
        self.reload_button.configure(state="disabled")
        self.start_bluetooth_scan()
        for widget in self.button_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    ind = index()
    try:
        root.mainloop()
    except Exception as e:
        ind.logger.error(e)
    except KeyboardInterrupt:
        ind.logger.info("Shutting down...")