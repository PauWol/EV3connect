import ev3_dc as ev3
import time
import threading
from helpers import Logger

class EV3connect(Logger):
    def __init__(self,macaddres:str):
        """
        Initilises a connection with the Provided EV3 macaddres

        Args:
            `macaddres` (str): MAC address of the EV3
        """
        super().__init__("EV3connect", debug=False)
        self.motorD = None
        self.motorC = None
        self.motorB = None
        self.motorA = None
        self.MACADDRES = macaddres
        
        #Init connection:
        self.EV3 = ev3.EV3(protocol=ev3.BLUETOOTH, host=macaddres)

        thread_a = threading.Thread(target=self.initializeA, daemon=True)
        thread_a.start()
        thread_b = threading.Thread(target=self.initializeB, daemon=True)
        thread_b.start()
        thread_c = threading.Thread(target=self.initializeC, daemon=True)
        thread_c.start()
        thread_d = threading.Thread(target=self.initializeD, daemon=True)
        thread_d.start()
        
    def initializeA(self):
        while True:
            acheck = self.MotorsAsDict()
            acheck = acheck["port_1"]
            if acheck is not None:
                self.motorA = ev3.Motor(port=ev3.PORT_A,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                self.motorA.verbosity = 0
                break
            time.sleep(0.1)
    
    def initializeB(self):
        while True:
            acheck = self.MotorsAsDict()
            acheck = acheck["port_2"]
            if acheck is not None:
                self.motorB = ev3.Motor(port=ev3.PORT_B,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                self.motorB.verbosity = 0
                break
            time.sleep(0.1)
    
    def initializeC(self):
        while True:
            acheck = self.MotorsAsDict()
            acheck = acheck["port_3"]
            if acheck is not None:
                self.motorC = ev3.Motor(port=ev3.PORT_C,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                self.motorC.verbosity = 0
                break
            time.sleep(0.1)
    
    def initializeD(self):
        while True:
            acheck = self.MotorsAsDict()
            acheck = acheck["port_4"]
            if acheck is not None:
                self.motorD = ev3.Motor(port=ev3.PORT_D,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                self.motorD.verbosity = 0
                break
            time.sleep(0.1)





    def Led(self, color, action_type ='static'):
        """
        Changes the color of the integrated LED

        Args:
            `color` (str): red | orange | green
            `type` (str): flash | pulse | static | off
        """
        if action_type == 'off':
            led = ev3.LED_OFF
        elif color == 'red':
            if action_type == 'flash':
                led = ev3.LED_RED_FLASH
            if action_type == 'pulse':
                led = ev3.LED_RED_PULSE
            if action_type == 'static':
                led = ev3.LED_RED
        elif color == 'orange':
            if action_type == 'flash':
                led = ev3.LED_ORANGE_FLASH
            if action_type == 'pulse':
                led = ev3.LED_ORANGE_PULSE
            if action_type == 'static':
                led = ev3.LED_ORANGE
        elif color == 'green':
            if action_type == 'flash':
                led = ev3.LED_GREEN_FLASH
            if action_type == 'pulse':
                led = ev3.LED_GREEN_PULSE
            if action_type == 'static':
                led = ev3.LED_GREEN     
        else:
            raise ValueError(f"Invalid color: {color} or type: {action_type}")

        jb = ev3.Jukebox(protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
        jb.change_color(led)

    def Sound(self,path,loudness = 100):
        """
        Plays a sound file

        Args:
            `path` (str): path to sound file on EV3 device
            `loudness` (int): volume the sound is played at (1-100)

        """
        snd = ev3.Sound(protocol=ev3.BLUETOOTH,ev3_obj=self.EV3, volume=loudness)
        snd.verbosity = 0
        snd.stop_sound()
        snd.play_sound(path)

    def Tone(self,frequency,duration = 1,volume = 100):
        """
        Plays a tone

        Args:
            `frequency` (int): frequency in Hz (250-10000)
            `duration` (int): time the tone is being played
            `volume` (int): volume the tone is played at (1-100)

        """
        tn = ev3.Sound(protocol=ev3.BLUETOOTH,ev3_obj=self.EV3, volume=volume)
        tn.verbosity = 0
        tn.stop_sound()
        tn.tone(frequency, duration=duration, volume=volume)

    def Status(self):
        """
        Returns a dictionary with general information of the EV3 brick

        Information:
            `mac`
            `memory_total`
            `memory_free`
            `verion`
            `name`
            `percentage`

        """
        info = ev3.EV3(protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
        return dict(mac=info.host, memory_total=info.memory.total, memory_free=info.memory.free, version=info.system.os_version, name=info.name, percentage=info.battery.percentage)
    
    def SensorsAsDict(self):
        def dataTrans(port, type):
            if type == 16: #touch
                sen = ev3.Touch(port=port,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                sor = str(sen.touched)
                sen.__del__()
                return sor
            elif type == 29: #color
                sen = ev3.Color(port=port,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                sor = sen.color
                sen.__del__()
                colors = {0: 'None',1: 'Black',2: 'Blue',3: 'Green',4: 'Yellow',5: 'Red',6: 'White',7: 'Brown'}
                return colors.get(sor, 'None')
            elif type == 30: #ultrasonic
                sen = ev3.Ultrasonic(port=port,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                sor = sen.distance
                sen.__del__()
                return sor
            elif type == 32: #gyro
                sen = ev3.Gyro(port=port,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                sor = sen.angle
                sen.__del__()
                return sor
            elif type == 33: #infrared
                sen = ev3.Infrared(port=port,protocol=ev3.BLUETOOTH,ev3_obj=self.EV3)
                sor = sen.distance
                sen.__del__()
                return sor

        self.EV3._physical_ev3.introspection(self.EV3._verbosity)
        port_1 = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_1]["type"]
        port_2 = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_2]["type"]
        port_3 = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_3]["type"]
        port_4 = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_4]["type"]
        return dict(
            port_1=port_1, 
            port_2=port_2, 
            port_3=port_3, 
            port_4=port_4,
            data_1=dataTrans(ev3.PORT_1, port_1),
            data_2=dataTrans(ev3.PORT_2, port_2),
            data_3=dataTrans(ev3.PORT_3, port_3),
            data_4=dataTrans(ev3.PORT_4, port_4)
        )

    
    def MotorsAsDict(self):
        self.EV3._physical_ev3.introspection(self.EV3._verbosity)
        port_a = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_A_SENSOR]["type"]
        port_b = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_B_SENSOR]["type"]
        port_c = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_C_SENSOR]["type"]
        port_d = self.EV3._physical_ev3._introspection["sensors"][ev3.PORT_D_SENSOR]["type"]
        return dict(
            port_1=port_a, 
            port_2=port_b, 
            port_3=port_c, 
            port_4=port_d
        )
    
    def try_motor_func(self, func, direction, speed):
        try:
            return func(direction=direction, speed=speed)
        except Exception as e:
            self.logger.error(e)
    
    def MotorA(self,direction,speed = 90):
        if self.motorA is None:
            self.logger.debug("Motor A not found!Missing connection?")
            return
        if direction == 0 and self.motorA.busy:
                self.motorA.stop()
        elif direction != 0:
            self.try_motor_func(self.motorA.start_move,direction=direction,speed=speed)

    def MotorB(self,direction = 1,speed = 90):
        if self.motorB is None:
            self.logger.debug("Motor B not found!Missing connection?")
            return
        if direction == 0 and self.motorB.busy:
                self.motorB.stop()
        elif direction != 0:
            self.try_motor_func(self.motorB.start_move,direction=direction,speed=speed)

    def MotorC(self,direction = 1,speed = 90):
        if self.motorC is None:
            self.logger.debug("Motor C not found!Missing connection?")
            return
        if direction == 0 and self.motorC.busy:
                self.motorC.stop()
        elif direction != 0:
            self.try_motor_func(self.motorC.start_move,direction=direction,speed=speed)

    def MotorD(self,direction = 1,speed = 90):
        if self.motorD is None:
            self.logger.debug("Motor D not found!Missing connection?")
            return
        if direction == 0 and self.motorD.busy:
                self.motorD.stop()
        elif direction != 0:
            self.try_motor_func(self.motorD.start_move,direction=direction,speed=speed)
    