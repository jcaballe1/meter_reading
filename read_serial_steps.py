#!/usr/bin/env python


import serial
import re
import sys
from datetime import datetime
import sqlite3

#dictionary of codes
obiscodes = {
    "0-0:1.0.0": "Timestamp",
    #"0-0:96.1.1": "Electricity Meter Serial",
    "1-0:1.8.1": "Rate 1 (day) - total consumption kWh",
    "1-0:1.8.2": "Rate 2 (night) - total consumption kWh",
    "1-0:2.8.1": "Rate 1 (day) - total production kWh",
    "1-0:2.8.2": "Rate 2 (night) - total production kWh",
    #"0-1:96.1.0": "Gas Meter Serial",
    "0-1:24.2.1": "Gas Total Consumption m3",
    }
db = '/home/pi/Documents/projects/meter_reading/db/ac_meter_read.db'
# Seriele poort confguratie
ser = serial.Serial()


# ESMR 5.0
ser.baudrate = 115200
ser.bytesize=serial.EIGHTBITS
ser.parity=serial.PARITY_NONE
ser.stopbits=serial.STOPBITS_ONE
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 12
ser.port = "/dev/ttyUSB0"

#Open serial port
try:
    ser.open()
except:
    sys.exit ("Could not open serial port"  % ser.name)
    
#read N number of lines
cont = 1

while cont < 28:
    p1_line = ''
    line_raw = ser.readline()
    line_str = str(line_raw)
    p1_line = line_str.strip()
  
    if re.search("0-0:1.0.0",p1_line):
        timestamp_str = p1_line[12:24]
        timestamp = datetime.strptime(timestamp_str,
                                      '%y%m%d%H%M%S')
    
    if re.search("1-0:1.8.1",p1_line):
        consumption_night = float(p1_line[12:22])
    
    if re.search("1-0:1.8.2",p1_line):
        consumption_day = float(p1_line[12:22])
    
    if re.search("1-0:2.8.1",p1_line):
        production_night = float(p1_line[12:22])
    
    if re.search("1-0:2.8.2",p1_line):
        production_day = float(p1_line[12:22])
        
    if re.search("0-1:24.2.1",p1_line):
        gas_consumption = float(p1_line[28:37])
        gas_timestamp_str = p1_line[13:25]
        gas_timestamp = datetime.strptime(gas_timestamp_str,
                                      '%y%m%d%H%M%S')
        
    cont = cont + 1

# print("timestamp is ", timestamp)
# print("consumption_day = ", consumption_day)
# print("consumption_night = ", consumption_night)
# print("production_day = ", production_day)
# print("production_night = ", production_night)
# print("gas_consumption = ", gas_consumption)
# print("gas_timestamp is ", gas_timestamp)

#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Oops %s. Cannot close the serial port." % ser.name )


#Connect to db and insert reading
#steps to create db
conn = sqlite3.connect(db)
cur = conn.cursor()
#cur.execute(create table reads
#(timestamp, consumption_day, consumption_night, production_day, production_night, gas_consumption, gas_timestamp)#''')

#insert read values in table
cur.execute("insert into reads values(?,?,?,?,?,?,?)",
            (timestamp, consumption_day, consumption_night,
             production_day, production_night, gas_consumption,
             gas_timestamp))

#save and close db connection
conn.commit()
conn.close()

###########################################
######## uploading data to influxdb #######
###########################################
#write data into influxdb -- all this code segment was commented out on 16/08/2022
#from influxdb_client import InfluxDBClient, Point, WritePrecision
#from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate an API token from the "API Tokens Tab" in the UI
#token = "ue6kIcaNh8kJHfnedKzAvFGC74HwObLZP9c6TtIshsVZRZKzYtsFKX01EdeTa_7R_Nr-JvOALLqAYjeJbTxFXQ=="
#org = "jcaballe@eafit.edu.co"
#bucket = "meter_reads"

#with InfluxDBClient(url="https://eu-central-1-1.aws.cloud2.influxdata.com", token=token, org=org) as client:
#    write_api = client.write_api(write_options=SYNCHRONOUS)
#    data = f"mem,host=host1 consumption_day={consumption_day}"
#    write_api.write(bucket, org, data)
#    data = f"mem,host=host1 consumption_night={consumption_night}"
#    write_api.write(bucket, org, data)
#    data = f"mem,host=host1 consumption_gas={gas_consumption}"
#    write_api.write(bucket, org, data)
#client.close()


