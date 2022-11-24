## Building your own Energy consumption metrics

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent fermentum porta libero auctor dapibus. Proin tincidunt euismod urna, ac facilisis neque scelerisque nec. Nunc mollis neque ligula, ac semper quam sodales sed. Aliquam sed augue quis tortor efficitur tristique nec in arcu. Nulla tincidunt pulvinar imperdiet. Suspendisse potenti. Nunc porta sollicitudin dolor vel porta. 

#### Why measuring Energy consumption realtime?

Cras consequat dignissim nibh vel auctor. Proin consectetur dictum velit, tincidunt dictum enim dapibus sed. In non leo nec leo commodo convallis. Morbi sed libero venenatis, tempus ligula non, vestibulum libero. Nam quis faucibus urna, eget malesuada erat. Curabitur sodales volutpat accumsan. Sed quis lorem et libero laoreet consequat vitae sed ante. Aliquam faucibus bibendum pulvinar. Vestibulum et elit a nulla aliquam porttitor vitae nec ipsum. Integer dapibus diam nibh, vel pellentesque purus mollis eu. Sed gravida nisi nec metus varius elementum. In condimentum pulvinar bibendum. Absolutely

#### Dutch Smart Meters
Cras nisi leo, luctus id molestie id, viverra nec eros. Mauris ut sapien purus. Aenean arcu nibh, dictum eu pellentesque ac, malesuada nec eros. Aliquam eu dolor eget quam rhoncus faucibus. Ut molestie in ante in auctor. Maecenas vitae tortor quam. Fusce ultricies laoreet pharetra. Morbi blandit nulla ac tellus hendrerit vehicula. Curabitur vitae nibh lobortis, vulputate libero sit amet, tempor neque. Nunc ac elit sodales tellus semper dapibus. Fusce justo justo, lacinia et blandit accumsan, volutpat vitae est. Pellentesque at varius orci. 

Fusce sed feugiat enim, sed congue orci. Curabitur erat lectus, tincidunt at justo sit amet, facilisis fermentum elit. Proin pellentesque enim ut ligula convallis, quis tristique sem dapibus. Aliquam blandit est egestas dui venenatis malesuada. Nunc id dolor sed massa sodales accumsan. Proin a viverra justo, a ultricies tellus. Nunc ipsum libero, porttitor vitae est eu, finibus dapibus mauris. Nulla consequat rhoncus fermentum. Praesent eget nisl urna. Quisque luctus sapien sed quam lobortis, eu tincidunt dui condimentum. Suspendisse potenti. 

#### A way to read smart meter data
Mauris eu turpis rutrum, aliquet est quis, rutrum justo. Phasellus ac elementum velit. Sed mattis orci in commodo semper. Nunc nec eros sed ex bibendum molestie. In non eros lacus. Etiam eu vestibulum augue. Maecenas posuere, magna quis dignissim dapibus, felis erat luctus dui, quis elementum urna quam quis nunc. Phasellus diam enim, commodo in convallis et, blandit non arcu. Etiam lorem magna, blandit non semper ut, efficitur at arcu. Morbi eu erat placerat, posuere ante eget, sagittis tellus. 

Pellentesque a felis facilisis, vehicula nibh vel, placerat nunc. Fusce venenatis scelerisque libero non volutpat. Praesent hendrerit tortor id urna gravida consequat. Nam consectetur placerat nunc, fermentum consequat metus lobortis posuere. Vestibulum mauris ante, pulvinar ac rutrum et, placerat venenatis arcu. Quisque pulvinar sit amet nisl sed viverra. Pellentesque tristique nisl ex, faucibus ullamcorper sem maximus vel. 

```python

```

```python
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
```

*Fusce* sed est orci. Etiam at odio odio. Praesent ultricies turpis cursus sodales ornare. Morbi euismod at nibh ornare facilisis. Pellentesque  est ex, imperdiet iaculis velit nec, interdum pharetra ex. Duis  ultricies aliquet diam, consectetur interdum ligula elementum id.  Suspendisse dui neque, hendrerit eu risus eu, sollicitudin aliquet erat. Curabitur in nunc cursus, cursus tellus a, aliquam eros. Mauris  accumsan ac metus eu sagittis. Donec aliquet nibh non erat fermentum, et tempor nibh mattis. Etiam posuere purus nec metus bibendum feugiat. Nam vitae ante id velit finibus fermentum sit amet at turpis.

```python
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
        timestamp = datetime.strptime(timestamp_str,'%y%m%d%H%M%S')
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
        gas_timestamp = datetime.strptime(gas_timestamp_str,'%y%m%d%H%M%S')
        
    cont = cont + 1

#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Oops %s. Cannot close the serial port." % ser.name )
```

Ut hendrerit vehicula nibh, id congue risus euismod in. Aenean bibendum, nulla sit amet convallis bibendum, sapien odio consectetur massa, quis  aliquet ligula turpis vel turpis. Cras pretium fringilla dui molestie  accumsan. Duis dictum orci vitae lectus molestie, eu finibus quam  maximus. Nullam lacinia sodales massa. Donec lobortis risus id fermentum vehicula. Suspendisse dui metus, pharetra a convallis quis, iaculis vel mauris. Nunc tincidunt sem quis quam molestie, sed scelerisque lectus  pretium. Nullam a ipsum mi. Vestibulum quis ipsum nisl. Morbi imperdiet  vehicula elit, ut vestibulum sapien auctor et. Morbi ut gravida lorem.  Aliquam non blandit neque.

Donec dapibus diam augue, eget laoreet lorem placerat vel. Donec  pellentesque lacus sapien, vitae dapibus purus feugiat in. Cras semper  quam ut mattis tincidunt. Morbi vel dui at erat tristique accumsan.  Mauris euismod lacus sed luctus facilisis. Praesent pretium lectus a  augue imperdiet, nec consectetur nulla consectetur. Nullam et justo non  tortor interdum tincidunt. Ut a porta risus.

```python
#Connect to db and insert reading
#steps to create db
conn = sqlite3.connect(db)
cur = conn.cursor()

#insert read values in table
cur.execute("insert into reads values(?,?,?,?,?,?,?)",
            (timestamp, consumption_day, consumption_night,
             production_day, production_night, gas_consumption,
             gas_timestamp))

#save and close db connection
conn.commit()
conn.close()
```

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla a ex  ultricies, bibendum neque sit amet, cursus justo. Aliquam dictum erat a  pellentesque tincidunt. Interdum et malesuada fames ac ante ipsum primis in faucibus. Maecenas tempus lacus odio. Fusce eget facilisis neque, at faucibus dolor. Maecenas dapibus volutpat iaculis. Proin dapibus, leo  ac facilisis laoreet, nibh ligula convallis leo, et laoreet neque nulla  suscipit lacus. Vestibulum in orci ante. Aenean at mollis nisl. Proin  mollis nisl nisi, et aliquet ligula pulvinar a.

Fusce sed est orci. Etiam at odio odio. Praesent ultricies turpis cursus sodales ornare. Morbi euismod at nibh ornare facilisis. Pellentesque  est ex, imperdiet iaculis velit nec, interdum pharetra ex. Duis  ultricies aliquet diam, consectetur interdum ligula elementum id.  Suspendisse dui neque, hendrerit eu risus eu, sollicitudin aliquet erat. Curabitur in nunc cursus, cursus tellus a, aliquam eros. Mauris  accumsan ac metus eu sagittis. Donec aliquet nibh non erat fermentum, et tempor nibh mattis. Etiam posuere purus nec metus bibendum feugiat. Nam vitae ante id velit finibus fermentum sit amet at turpis.

```bash
#!/bin/bash
sqlite3 -header -csv ~/Documents/projects/meter_reading/db/ac_meter_read.db "select * from reads;" > ~/Documents/projects/meter_reading/db/data.csv

#secure copy to server
scp -r ~/Documents/projects/meter_reading/db andres@andres-hpelitebook8560w:~/Documents/meter_reading/
```
Fusce sed est orci. Etiam at odio odio. Praesent ultricies turpis cursus sodales ornare. Morbi euismod at nibh ornare facilisis. Pellentesque  est ex, imperdiet iaculis velit nec, interdum pharetra ex. Duis  ultricies aliquet diam, consectetur interdum ligula elementum id.  Suspendisse dui neque, hendrerit eu risus eu, sollicitudin aliquet erat. Curabitur in nunc cursus, cursus tellus a, aliquam eros. Mauris  accumsan ac metus eu sagittis. Donec aliquet nibh non erat fermentum, et tempor nibh mattis. Etiam posuere purus nec metus bibendum feugiat. Nam vitae ante id velit finibus fermentum sit amet at turpis.

![Alt text](https://file%2B.vscode-resource.vscode-cdn.net/home/andres/Documents/meter_reading/post%20writeup/subplot_electricity.png?version%3D1668858387600)
