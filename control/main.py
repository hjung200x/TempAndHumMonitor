import sys
import traceback
import time
# import AM2315
import sqlite3
import RPi.GPIO as GPIO
from datetime import datetime
from adc import ADC
import Adafruit_DHT
import AM2315
from DFRobot_SHT3X import *

GPIO_PIN_TempAndHumiditySensor = 24
GPIO_PIN_CoolFan = 27
GPIO_PIN_WaterPump = 18
GPIO_PIN_WaterLevelSensor = 26
GPIO_PIN_Humidifier1 = 22
GPIO_PIN_Humidifier2 = 23

class Config:
    def __init__(self):
        now = datetime.now()
        print('[{}] Initializing config...' .format(now))
        sys.stdout.flush()
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        cur.execute("SELECT * FROM config_configtbl")
        self.config = dict((y, x) for x, y in cur)
        now = datetime.now()
        print('[{}] Configuration'.format(now))
        print(self.config)
        sys.stdout.flush()
        db_conn.close()

    def refresh(self):
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        cur.execute("SELECT * FROM config_configtbl")
        self.config = dict((y, x) for x, y in cur)
        db_conn.close()

    def update(self, key, value):
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        cur.execute("UPDATE config_configtbl SET value = ? WHERE key = ?", (value, key))
        db_conn.commit()
        db_conn.close()

class Status:
    def __init__(self):
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        cur.execute("SELECT * FROM status_status")
        self.status = dict((x, y) for x, y in cur)
        db_conn.close()
        
    def update(self, start=False, end=False):
        if (start):
            self.status['run'] = '1'
            self.status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif (end):
            self.status['run'] = '0'
            self.status['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            pass
        v = [(name, value) for name, value in self.status.items()]
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        for row in v:
            cur.execute("UPDATE status_status SET value = ? WHERE name = ?", (row[1], row[0]))
        db_conn.commit()
        db_conn.close()

class Event:
    def __init__(self, humidifier, fan, pump, wl_sensor) -> None:
        self.humidifier = humidifier
        self.fan = fan
        self.pump = pump
        self.wl_sensor = wl_sensor
        
    def write(self):
        h = self.humidifier.get_status()
        f = self.fan.get_status()
        p = self.pump.get_status()
        w = self.wl_sensor.get_status()
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO monitor_event(date, humidifier_event, fan_event, pump_event, water_level_event) \
                        VALUES(?, ?, ?, ?, ?)", \
                            (now, h, f, p, w))
        db_conn.commit()
        db_conn.close()
        
    def delete_all(self):
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        cur.execute("DELETE FROM monitor_event")
        db_conn.commit()
        db_conn.close()
        
class Operation:
    def __init__(self, status, fan, humidifier, pump) -> None:
        self.status = status
        self.fan = fan
        self.humidifier = humidifier
        self.pump = pump

        self.is_operation = False

    def start(self):
        if (self.is_operation == False):
            now = datetime.now()
            print('[{}] Operation Start...'.format(now))
            sys.stdout.flush()
            self.status.update(start=True)
            self.is_operation = True
        
    def stop(self):
        if (self.is_operation == True):
            now = datetime.now()
            print('[{}] Operation Stop...'.format(now))
            sys.stdout.flush()
            self.pump.off()
            self.fan.off()
            self.humidifier.off()

            self.status.update(end=True)
            self.is_operation = False

class RecordingTandH:
    def __init__(self):
        '''
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        cur.execute("DELETE FROM monitor_monitor")
        db_conn.commit()
        db_conn.close()
        '''
        
    def record(self, t, h):
        now = datetime.now()
        t_rounded = round(t, 1)
        h_rounded = round(h, 1)
        print('[{}] Recording...'.format(now))
        print(f'[{now}] Temperature: {t_rounded}℃, Hummidity: {h_rounded}%')
        sys.stdout.flush()
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO monitor_monitor(date, temperature, hummidity) \
                        VALUES(?,?,?)", \
                            (now, t_rounded, h_rounded))
        db_conn.commit()
        db_conn.close()
        
    def delete_all(self):
        db_conn = sqlite3.connect('/home/hjung/proj/Achamber/db/db.sqlite3')
        cur = db_conn.cursor()
        cur.execute("DELETE FROM monitor_monitor")
        db_conn.commit()
        db_conn.close()

# class TempAndHummiditySensor:
#     def __init__(self):
#         self.handle = AM2315.AM2315()
        
#     def poll(self):
#         h,t,c = self.handle.read_humidity_temperature_crc()
#         return t, h

class CoolFan:
    def __init__(self, pin):
        self.status = False
        self.outpin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.outpin, GPIO.OUT, initial=GPIO.HIGH)
    
    def on(self):
        if (self.status == False):
            now = datetime.now()
            print(f'[{now}] CoolFan On..')
            sys.stdout.flush()
            GPIO.output(self.outpin, GPIO.LOW)
            self.status = True
            return True
        return False
        
    def off(self):
        if (self.status == True):
            now = datetime.now()
            print(f'[{now}] CoolFan Off..')
            sys.stdout.flush()
            GPIO.output(self.outpin, GPIO.HIGH)
            self.status = False
            return True
        return False
            
    def get_status(self):
        return self.status

class Hummidifier:
    def __init__(self, pin1, pin2):
        self.status = False
        self.outpin_1 = pin1
        self.outpin_2 = pin2
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.outpin_1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.outpin_2, GPIO.OUT, initial=GPIO.LOW)
    
    def on(self):
        if (self.status == False):
            now = datetime.now()
            print(f'[{now}] Hummidifier On..')
            sys.stdout.flush()
            GPIO.output(self.outpin_1, GPIO.HIGH)
            GPIO.output(self.outpin_2, GPIO.HIGH)
            self.status = True
            return True
        return False
        
    def off(self):
        if (self.status == True):
            now = datetime.now()
            print(f'[{now}] Hummidifier Off..')
            sys.stdout.flush()
            GPIO.output(self.outpin_1, GPIO.LOW)
            GPIO.output(self.outpin_2, GPIO.LOW)
            self.status = False
            return True
        return False

    def get_status(self):
        return self.status

class HummidifierPWM:
    def __init__(self, pwm_pin):
        self.status = False
        self.outpin = pwm_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.outpin, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(self.outpin, 100)
        self.pwm.start(0)
        
    def on(self, duty=100):
        if (self.status == False):
            now = datetime.now()
            print(f'[{now}] Hummidifier On..')
            sys.stdout.flush()
            self.pwm.ChangeDutyCycle(duty)
            self.status = True
            return True
        return False
        
    def off(self):
        if (self.status == True):
            now = datetime.now()
            print(f'[{now}] Hummidifier Off..')
            sys.stdout.flush()
            self.pwm.ChangeDutyCycle(0)
            self.status = False
            return True
        return False

    def get_status(self):
        return self.status

class WaterPump:
    def __init__(self, pin):
        self.status = False
        self.outpin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.outpin, GPIO.OUT, initial=GPIO.LOW)
    
    def on(self):
        if (self.status == False):
            now = datetime.now()
            print(f'[{now}] Pump On..')
            sys.stdout.flush()
            GPIO.output(self.outpin, GPIO.HIGH)
            self.status = True
            return True
        return False
        
    def off(self):
        if (self.status == True):
            now = datetime.now()
            print(f'[{now}] Pump Off..')
            sys.stdout.flush()
            GPIO.output(self.outpin, GPIO.LOW)
            self.status = False
            return True
        return False

    def get_status(self):
        return self.status

class WaterLevelSensor:
    def __init__(self, pin):
        self.status = False
        self.inpin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.inpin, GPIO.IN)
    
    def poll(self):
        level = GPIO.input(self.inpin)
        is_changed = False
        if (self.status != level):
            is_changed = True
        self.status = level
        
        return level, is_changed

    def get_status(self):
        return self.status

# 습도에 따라 PWM 제어를 하기 위하여 PID 제어기를 사용한다.
class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.P = 0
        self.I = 0
        self.D = 0
        self.last_error = 0
        self.last_time = time.time()
        self.output = 0
        self.target = 0
        
    def set_target(self, target):
        self.target = target
        
    def update(self, value):
        now = time.time()
        error = self.target - value
        self.P = error
        self.I += error * (now - self.last_time)
        self.D = (error - self.last_error) / (now - self.last_time)
        self.output = self.Kp * self.P + self.Ki * self.I + self.Kd * self.D
        self.last_error = error
        self.last_time = now
        
        return self.output
        
    def get_output(self):
        return self.output

# 아날로그 습도 센서의 클래스를 정의한다.
class AnanlogHumiditySensor:
    def __init__(self, pin, size=10):
        self.adc = ADC()
        self.pin = pin
        self.humidity = 0
        # self.min_voltage = 300  # 최소 voltage 값
        # self.max_voltage = 2251  # 최대 voltage 값
        self.min_voltage = 1400  # 최소 voltage 값
        self.max_voltage = 3088  # 최대 voltage 값
        self.min_value = 0  # 매핑된 최소 값
        self.max_value = 100  # 매핑된 최대 값
        self.size = size
        self.buffer = []
        
    def poll(self):
        voltage = self.adc.read_voltage(self.pin)
        
        print(f'voltage: {voltage}\n')
        
        # # 입력된 voltage를 0 ~ 1 범위로 정규화
        # normalized_voltage = (voltage - self.min_voltage) / (self.max_voltage - self.min_voltage)

        # # 정규화된 voltage를 0 ~ max_value 범위로 매핑
        # humidity = self.min_value + normalized_voltage * (self.max_value - self.min_value)

        humidity = -(19.7 / 0.54) + (100 / 0.54) * (voltage / 3200)
        print(f'humidity: {humidity}\n')
        # 값이 최대값을 초과하면 최대값으로 설정
        if humidity > self.max_value:
            humidity = self.max_value

        # 값이 최소값 미만이면 최소값으로 설정
        if humidity < self.min_value:
            humidity = self.min_value

        # 값을 버퍼에 저장하고, 버퍼의 사이즈만큼 평균값을 사용한다.
        self.buffer.append(humidity)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)

        avg_humidity = sum(self.buffer) / len(self.buffer)

        self.humidity = avg_humidity
        
        return avg_humidity

    def get_humidity(self):
        return self.humidity

class AnanlogTemperatureSensor:
    def __init__(self, pin, size=10):
        self.adc = ADC()
        self.pin = pin
        self.temperature = 0
        # self.min_voltage = 300  # 최소 voltage 값
        # self.max_voltage = 2251  # 최대 voltage 값
        self.min_voltage = 1300  # 최소 voltage 값
        self.max_voltage = 3251  # 최대 voltage 값
        self.min_value = 0  # 매핑된 최소 값
        self.max_value = 100  # 매핑된 최대 값
        self.size = size
        self.buffer = []
        
    def poll(self):
        voltage = self.adc.read_voltage(self.pin)
        
        # 입력된 voltage를 0 ~ 1 범위로 정규화
        normalized_voltage = (voltage - self.min_voltage) / (self.max_voltage - self.min_voltage)

        # 정규화된 voltage를 0 ~ max_value 범위로 매핑
        temperature = self.min_value + normalized_voltage * (self.max_value - self.min_value)

        # 값이 최대값을 초과하면 최대값으로 설정
        if temperature > self.max_value:
            temperature = self.max_value

        # 값이 최소값 미만이면 최소값으로 설정
        if temperature < self.min_value:
            temperature = self.min_value

        # 값을 버퍼에 저장하고, 버퍼의 사이즈만큼 평균값을 사용한다.
        self.buffer.append(temperature)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)

        avg_temperature = sum(self.buffer) / len(self.buffer)

        self.temperature = avg_temperature
        
        return avg_temperature

    def get_humidity(self):
        return self.temperature

class DHT22_TempAndHumiditySensor:
    def __init__(self, pin):
        self.sensor = Adafruit_DHT.DHT22
        self.pin = pin
        
    def poll(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
        return humidity, temperature

class AM2315_TempAndHumiditySensor:
    def __init__(self):
        self.sensor = AM2315.AM2315()
        
    def poll(self):
        temperature = self.sensor.read_temperature()
        humidity = self.sensor.read_humidity()
        return temperature, humidity

class SHT31_F_TempAndHumiditySensor:
    def __init__(self, iic_addr = 0x45, bus = 1):
        self.SHT3X =  DFRobot_SHT3x(iic_addr = 0x45,bus = 1)
        
        while(self.SHT3X.begin(RST = 4) != 0):
            print("The initialization of the chip is failed, please confirm whether the chip connection is correct")
            time.sleep(1)
            
        if(self.SHT3X.soft_reset() == False):
            print("Failed to reset the chip")
            
        if(self.SHT3X.start_periodic_mode(measure_freq = self.SHT3X.measureFreq_10Hz,repeatability = self.SHT3X.repeatability_high) == False):
            print("Failed to enter the periodic mode")

    def poll(self):
        temperature = self.SHT3X.get_temperature_C()
        humidity = self.SHT3X.get_humidity_RH()
        
        return temperature, humidity

class HummidifierController:
    def __init__(self, hum1, hum2):
        self.hum1 = hum1
        self.hum2 = hum2
        self.status = False
        
    def on(self, duty=100):
        if (self.status == False):
            self.hum1.on(duty)
            self.hum2.on(duty)
            self.status = True
            return True
        return False
    
    def off(self):
        if (self.status == True):
            self.hum1.off()
            self.hum2.off()
            self.status = False
            return True
        return False
    
    def get_status(self):
        return self.status


def main():
    now = datetime.now()
    print('[{}] Start Acham control' .format(now))
    sys.stdout.flush()
    config = Config()
    status = Status()
    record = RecordingTandH()
    # t_h_sensor = TempAndHummiditySensor()
    analog_humidity_sensor = AnanlogHumiditySensor(0)
    #t_h_sensor = DHT22_TempAndHumiditySensor(GPIO_PIN_TempAndHumiditySensor)
    t_h_sensor = SHT31_F_TempAndHumiditySensor()
    fan = CoolFan(GPIO_PIN_CoolFan)
    humidifier = Hummidifier(GPIO_PIN_Humidifier1, GPIO_PIN_Humidifier2)
    # hum1 = HummidifierPWM(12)
    # hum2 = HummidifierPWM(13)
    # humidifier = HummidifierController(hum1, hum2)
    pump = WaterPump(GPIO_PIN_WaterPump)
    wl_sensor = WaterLevelSensor(GPIO_PIN_WaterLevelSensor)
    event = Event(humidifier, fan, pump, wl_sensor)
    operation = Operation(status, fan, humidifier, pump)
    humidifier_off_start_time = 0
    humidifier_on_start_time = 0
    pid = PIDController(0.1, 0.01, 0.01)
    
    while (1):
        try:
            while (config.config['Operate chamber(0 - stop, 1 - run)'] == '0'):
                operation.stop()
                config.refresh()
                time.sleep(1)
            
            if (operation.is_operation == False):
                operation.start()
                start_time = time.time()
                coolfan_start_time = time.time()
                #record.delete_all()
                #event.delete_all()
                
            config.refresh()

            temperature, humidity = t_h_sensor.poll()
            #humidity = analog_humidity_sensor.poll()
            if humidity is not None and temperature is not None:
                print(f'Temperature: {temperature:.1f}℃, Humidity: {humidity:.1f}%')
                if (time.time() - start_time >= int(config.config['The interval time of recording T and H'])):
                    record.record(temperature, humidity)
                    start_time = time.time()
            else:
                print('Failed to get reading temperature and humidity')

            if (config.config['Enforce to run humidifier'] == '0'):
                if humidity is not None and temperature is not None:
                    # pid.set_target(int(config.config['The threshold of humidity']))
                    # pid.update(humidity)
                    # output = pid.get_output()
                    # if (output <= 0):
                    #     hum1.off()
                    #     hum2.off()
                    # elif (output <= 50):
                    #     hum1.on()
                    #     hum2.off()
                    # else:
                    #     hum1.on()
                    #     hum2.on()
                    
                    if (temperature > int(config.config['The threshold of temperature'])):
                        if (fan.on()):
                            event.write()
                    else:
                        if (fan.off()):
                            event.write()
                    
                    if (humidity > int(config.config['The threshold of hummidity'])):
                        if (humidifier.off()):
                            event.write()
                    else:
                        if (humidifier.on()):
                            event.write()
            else:
                # 가습기가 꺼져 있다면 'the duration of humidifier on'동안 가습기를 작동시키고, 가습기가 켜져 있다면 'the duration of humidifier off'동안 가습기를 중지시킨다.
                if (humidifier.get_status() == False):
                    if (time.time() - humidifier_off_start_time >= int(config.config['The duration of humidifier off'])):
                        humidifier.on()
                        humidifier_on_start_time = time.time()
                else:
                    if (time.time() - humidifier_on_start_time >= int(config.config['The duration of humidifier on'])):
                        humidifier.off()
                        humidifier_off_start_time = time.time()

            level, is_changed = wl_sensor.poll()
            if (is_changed):
                event.write()

            if (level == False):
                print('Not enough water ... watering')
                if (pump.on()):
                    event.write()
                time.sleep(int(config.config['The duration of watering']))
                if (pump.off()):
                    event.write()
                level, is_changed = wl_sensor.poll()
                if (level == False):
                    print('FAULT ERROR:::water empty!!')
                    sys.stdout.flush()
                    config.update('Operate chamber(0 - stop, 1 - run)', '0')

            if (int(config.config['enforce watering']) == 1):
                if (pump.get_status() == False):
                    if (pump.on()):
                        event.write()
                    time.sleep(int(config.config['The duration of watering']))
                    if (pump.off()):
                        pump.off()
                    config.update('enforce watering', '0')
                    event.write()

            if (config.config['enable periodical coolfan'] == '1'):
                if (time.time() - coolfan_start_time >= int(config.config['The interval time of coolfan'])):
                    if (fan.on()):
                        event.write()
                    time.sleep(3)
                    if (fan.off()):
                        event.write()
                    coolfan_start_time = time.time()

            time.sleep(int(config.config['The interval time of probing T and H']))
        
        except KeyboardInterrupt:
            print('KeyboardInterrupt occured!!')
            print('Terminated...')
            sys.stdout.flush()
            operation.stop()
            event.write()
            time.sleep(1)
            GPIO.cleanup()
            exit(1)

        except Exception as e:
            print('Exception ocurred!!')
            print(e)
            traceback.print_exc()
            sys.stdout.flush()
            

if __name__ == "__main__":
	main()
 
