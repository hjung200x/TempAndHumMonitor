import sys
import traceback
import time
import sqlite3
import RPi.GPIO as GPIO
from datetime import datetime
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

class SHT31_F_TempAndHumiditySensor:
    def __init__(self, iic_addr = 0x45, bus = 1):
        self.SHT3X =  DFRobot_SHT3x(iic_addr = iic_addr, bus = 1)
        
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


def main():
    now = datetime.now()
    print('[{}] Start Acham control' .format(now))
    sys.stdout.flush()
    config = Config()
    record = RecordingTandH()
    t_h_sensor = SHT31_F_TempAndHumiditySensor()
    
    while (1):
        try:
            config.refresh()

            temperature, humidity = t_h_sensor.poll()
            record.record(temperature, humidity)

            time.sleep(int(config.config['The interval time of probing T and H']))
        
        except KeyboardInterrupt:
            print('KeyboardInterrupt occured!!')
            print('Terminated...')
            sys.stdout.flush()
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
 
