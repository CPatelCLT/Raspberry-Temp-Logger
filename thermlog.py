#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import glob
import time
import datetime
import sqlite3


#--------------------#
# Database functions #
#--------------------#
conn = sqlite3.connect('tempreadings.db')
c = conn.cursor()

def create_tempstore_table():
    c.execute('CREATE TABLE IF NOT EXISTS tempstore (datestamp text, reading real)')
    conn.commit()

def create_log_table():
    c.execute('CREATE TABLE IF NOT EXISTS log (datestamp text, avg real, min real, max real)')
    conn.commit()

def put_data_temporary(datestamp, value):
    c.execute('INSERT INTO tempstore VALUES (?,?)', [datestamp, value])
    conn.commit()

def dump_to_log():
    c.execute('INSERT INTO log (datestamp, avg, min, max) SELECT ?, avg(reading), min(reading), max(reading) FROM tempstore', [datetime.datetime.now()])
    c.execute('DELETE FROM tempstore')
    conn.commit()


#------------#
# Probe init #
#------------#
os.system('modprobe w1-gpio')
time.sleep(2)       # Small delay to let system initialize device
os.system('modprobe w1-therm')
time.sleep(2)
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '10*')[0]
device_file = device_folder + '/w1_slave'


#---------------#
# Probe reading #
#---------------#
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.5)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = (lines[1])[equals_pos + 2:]

        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f


#-------------#
# Store temps #
#-------------#
create_log_table()
create_tempstore_table()
counter = 0
while True:
    
    # Logs every 30 seconds for an hour then dumps avg, min, max to the main log table
    if (counter < 120):
        # put_data_temporary(datetime.datetime.now(), input("enter temp"))   #-# Used in testing without Pi
        put_data_temporary(datetime.datetime.now(), read_temp())
        counter += 1
    else:
        dump_to_log()
        counter = 0
    time.sleep(30)
    
