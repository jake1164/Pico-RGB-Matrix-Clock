import math
import time
import busio
import board

import adafruit_ds3231
import adafruit_display_text.label
import ntp_client
from date_utils import *

i2c = busio.I2C(board.GP7,board.GP6)  # uses board.SCL and board.SDA
rtc = adafruit_ds3231.DS3231(i2c)


def _update():
    try:
        new_time = ntp_client.get_time()
        rtc.datetime = new_time
        print('updated RTC datetime')
    except Exception as e:
        print(e)


class DISPLAYSUBSYSTEM:
    def __init__(self, timeFormat):
        self.time_format = timeFormat
        self._first_enter_page = True

    def showDateTimePage(self,line1,line2,line3):
        line1.x = 2
        line1.y = 5
        line2.x = 8
        line2.y = 15
        line3.x = 10
        line3.y = 25
        t = rtc.datetime  
        date =  "%04d" % t.tm_year + '-' + "%02d" % t.tm_mon + '-' + "%02d" % t.tm_mday
        if self.time_format == 0: # 12 hour
            if t.tm_hour == 0:
                hour = 12
            elif t.tm_hour < 13:
                hour = t.tm_hour
            else:
                hour = t.tm_hour - 12
                
            dayOfTime = "{:2d}:{:02d} {}".format(
                hour,
                t.tm_min,
                "PM" if t.tm_hour > 11 else "AM")
        else: # 24 hour
            dayOfTime = "%02d" % t.tm_hour + ':' + "%02d" % t.tm_min + ':' + "%02d" % t.tm_sec
            
        line1.text = date
        line2.text = dayOfTime
        line3.text= DAYS_OF_WEEK[int(t.tm_wday)]


    def showSetListPage(self,line1,line2,_selectSettingOptions):
        line1.x = 8
        line1.y = 7
        line2.x = 8
        line2.y = 23
        line1.text = "SET LIST"
        if _selectSettingOptions == 0:
            line2.text = "TIME SET"
        if _selectSettingOptions == 1:
            line2.text = "DATE SET"
        if _selectSettingOptions == 2:
            line2.text = "BEEP SET"
        if _selectSettingOptions == 3:
            line2.text = "AUTODIM"
        if _selectSettingOptions == 4:
            line2.text = "12/24 HR"            
        if not self._first_enter_page:
            self._first_enter_page = True
            

    def timeSettingPage(self,line2,line3,_timeSettingLabel,_timeTemp):
        if self._first_enter_page:
            line2.x = 8
            line2.y = 13
            currentT = rtc.datetime
            _timeTemp[0] = currentT.tm_hour
            _timeTemp[1] = currentT.tm_min
            _timeTemp[2] = currentT.tm_sec
            self._first_enter_page = False
        currentTime = "%02d" % _timeTemp[0] + ':' + "%02d" % _timeTemp[1] + ':' + "%02d" % _timeTemp[2]
        line2.text = currentTime
        line3.text = "^"
        if _timeSettingLabel == 0:
            line3.x = 12
            line3.y = 24
        elif _timeSettingLabel == 1:
            line3.x = 29
            line3.y = 24
        else:
            line3.x = 47
            line3.y = 24


    def dateSettingPage(self, line2, line3, _timeSettingLabel, _dateTemp):
        if self._first_enter_page:
            line2.x = 3
            line2.y = 13
            currentD = rtc.datetime
            _dateTemp[0] = currentD.tm_year
            _dateTemp[1] = currentD.tm_mon
            _dateTemp[2] = currentD.tm_mday
            self._first_enter_page = False
        currentDate = "%02d" % _dateTemp[0] + '-' + "%02d" % _dateTemp[1] + '-' + "%02d" % _dateTemp[2]
        line2.text = currentDate
        line3.text = "^"
        if _timeSettingLabel == 0:
            line3.x = 12
            line3.y = 24
        elif _timeSettingLabel == 1:
            line3.x = 36
            line3.y = 24
        else:
            line3.x = 54
            line3.y = 24
            

    def onOffPage(self,line2,line3,_selectSettingOptions,_beepFlag,_autoLightFlag, _timeFormatFlag):
        if _selectSettingOptions == 2:
            line2.x = 20
            line2.y = 7
            line3.x = 20
            line3.y = 23
            if _beepFlag:
                line2.text = "> on"
                line3.text = "  off"
            else:
                line2.text = "  on"
                line3.text = "> off"
        if _selectSettingOptions == 3:
            line2.x = 20
            line2.y = 7
            line3.x = 20
            line3.y = 23
            
            if _autoLightFlag:
                line2.text = "> on"
                line3.text = "  off"
            else:
                line2.text = "  on"
                line3.text = "> off"
        if _selectSettingOptions == 4:
            line2.x = 10
            line2.y = 7
            line3.x = 10
            line3.y = 23

            if _timeFormatFlag:
                line2.text = "  12 Hr"
                line3.text = "> 24 Hr"
            else:
                line2.text = "> 12 Hr"
                line3.text = "  24 Hr"
                
        
    def network_update(self):
        _update()
        
    
    def get_interval(self):
        return ntp_client.get_interval()
        
    def setDateTime(self,_selectSettingOptions,_dateTemp,_timeTemp):
        getTime = rtc.datetime
        if _selectSettingOptions == 0:
            t = time.struct_time((getTime.tm_year, getTime.tm_mon, getTime.tm_mday, _timeTemp[0], _timeTemp[1], _timeTemp[2], getTime.tm_wday, -1, -1))
            rtc.datetime = t
        if _selectSettingOptions == 1:
            w = (ymd2ord(_dateTemp[0],_dateTemp[1], _dateTemp[2]) + 6) % 7
            t = time.struct_time((_dateTemp[0], _dateTemp[1], _dateTemp[2], getTime.tm_hour, getTime.tm_min, getTime.tm_sec, w, -1, -1))
            rtc.datetime = t


    def setTimeFormat(self, _selectFormat):
        self.time_format = _selectFormat            
