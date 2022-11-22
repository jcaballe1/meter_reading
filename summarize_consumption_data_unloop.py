#!/usr/bin/env python3

import pandas as pd
from time import sleep
import time
#import subprocess
from datetime import datetime
import matplotlib.pyplot as plt
#from datetime import datetime
#pd.set_option('precision', 2)

#read csv data and summarize
def serve_file():
    start_time = time.time()
    mylist =[]
    for chunk in pd.read_csv('~/Documents/meter_reading/db/data.csv', sep=',', chunksize=2000):
        mylist.append(chunk)
    df = pd.concat(mylist, axis = 0)
    del mylist
    #df = pd.read_csv('~/Documents/meter_reading/meter_reading/db/data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['timestamp'].dt.to_period('M')
    df['day'] = df['timestamp'].dt.day_name()

    #remove extreme point (reason unknown, but best to exclude)
    df = df[df['date'] != "2021-12-18"]

    #group data
    df_grouped = df.groupby(['date', 'day', 'month']).agg({'consumption_day': ['min', 'max'], 'consumption_night': ['min', 'max'], 'gas_consumption': ['min', 'max']})
    del(df)
    df_grouped['electricity_high'] = df_grouped[('consumption_day', 'max')] - df_grouped[('consumption_day', 'min')]
    df_grouped['electricity_low'] = df_grouped[('consumption_night', 'max')] - df_grouped[('consumption_night', 'min')]
    df_grouped['electricity_total'] = df_grouped['electricity_high'] + df_grouped['electricity_low']
    df_grouped['gas'] = df_grouped[('gas_consumption', 'max')] - df_grouped[('gas_consumption', 'min')]
    df_grouped = df_grouped.drop([('consumption_day', 'max'), ('consumption_day', 'min'), ('consumption_night', 'min')], axis=1)
    df_grouped = df_grouped.drop([('consumption_night', 'max'), ('gas_consumption', 'min'), ('gas_consumption', 'max')], axis=1)
    df_grouped = df_grouped.round(2)
    df_grouped.columns = ["electricity high", "electricity low", "electricity total", "gas m3"]
    df_grouped['moving_av_e'] = df_grouped['electricity total'].rolling(15).mean()
    df_grouped['moving_av_gas'] = df_grouped['gas m3'].rolling(15).mean()


    #find modified date of index file - taken from https://geekflare.com/python-run-bash/
    #process = subprocess.Popen(["date", "-r", "index.html"], stdout=subprocess.PIPE, text=True)
    #result = process.communicate()

    #produce charts - electricity
    plt.figure(figsize=(7,8))
    plt.subplot(2,1,1)
    df_grouped.droplevel(['day', 'month'])['electricity total'].plot()
    df_grouped.droplevel(['day', 'month'])['moving_av_e'].plot()
    plt.xticks(rotation = 30)
    plt.title("Daily Electricity consumption")
    plt.ylabel("KWH")
    plt.grid()

    plt.subplot(2,1,2)
    df_grouped.groupby(['month'])['electricity total'].sum().plot(kind='bar')
    plt.xticks(rotation = 30)
    plt.title("Monthly Electricity consumption")
    plt.ylabel("KWH")
    
    plt.tight_layout()

    plt.savefig('/home/andres/Documents/meter_reading/subplot_electricity.png')
    

    #produce charts - gas
    plt.figure(figsize=(7,8))
    plt.subplot(2,1,1)
    df_grouped.droplevel(['day', 'month'])['gas m3'].plot()
    df_grouped.droplevel(['day', 'month'])['moving_av_gas'].plot()
    plt.xticks(rotation = 30)
    plt.title("Daily Gas consumption")
    plt.ylabel("M3")
    plt.grid()

    plt.subplot(2,1,2)
    df_grouped.groupby(['month'])['gas m3'].sum().plot(kind='bar')
    plt.xticks(rotation = 30)
    plt.title("Monthly Gas consumption")
    plt.ylabel("M3")

    plt.tight_layout()

    plt.savefig('/home/andres/Documents/meter_reading/subplot_gas.png')

    #### Calculate projected consumption of current month   

    #find current month and filter dataset
    date_month = datetime.today().strftime("%Y-%m")
    month_number = datetime.today().month
    df_projection = df_grouped[df_grouped.index.get_level_values('month') == date_month]

    #dictionary with calendar days in month
    days_in_month = {
        1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}

    #number of past days
    n = len(df_projection)
    df_projection = df_projection.drop(df_projection.tail(1).index) #drop last row

    #cumulated gas and electricity consumption
    cumul_electricity = df_projection['electricity total'].sum()
    cumul_gas = df_projection['gas m3'].sum()

    #interpolate expected month consumption
    if n > 1:
        projected_electricity = days_in_month[month_number]*cumul_electricity/(n-1)
        projected_gas = days_in_month[month_number]*cumul_gas/(n-1)
    else:
        projected_electricity = None
        projected_gas = None

    #create and format current date month table
    date_month = [{'month': date_month}]
    date_month = pd.DataFrame(date_month)
    #convert date_month into period 'M' object
    date_month['month'] = pd.to_datetime(date_month['month'])
    date_month['month_formatted'] = date_month['month'].dt.to_period('M')

    #aggregate projected values with current month into a dataframe with the year month format
    temp_df = [{'projected electricity': projected_electricity,
    'projected gas': projected_gas,
       'month_formatted': date_month['month_formatted'][0]
    }]

    #date_month = date_month.dt.to_period('M')
    #date_month = datetime.strptime(date_month, '%Y-%m')
    temp_df = pd.DataFrame(temp_df, index=[date_month['month_formatted'][0]])

    #monthly aggregation and projections
    monthly_aggregation = df_grouped.groupby(['month'])[['electricity total', 'gas m3']].sum()
    monthly_aggregation['month_formatted'] = monthly_aggregation.index.get_level_values('month')
    newdf = monthly_aggregation.merge(temp_df, how="left", on="month_formatted")
    newdf.set_index("month_formatted", inplace=True)

    #plot  projection figures
    newdf[['electricity total', 'projected electricity']].plot(kind='area', 
                                                   subplots=False,
                                                  stacked = False)
    #plt.xticks(rotation = 30)
    plt.title("Electricity projection")
    plt.ylabel("KWH")

    plt.tight_layout()

    plt.savefig('/home/andres/Documents/meter_reading/subplot_electricity_projection.png')

    newdf[['gas m3', 'projected gas']].plot(kind='area', 
                                                   subplots=False,
                                                  stacked = False)
    #plt.xticks(rotation = 30)
    plt.title("Gas projection")
    plt.ylabel("m3")

    plt.tight_layout()

    plt.savefig('/home/andres/Documents/meter_reading/subplot_gas_projection.png')

    plt.close('all')
    del(newdf, monthly_aggregation, df_projection)

    #create html file
    html = df_grouped.droplevel(2).tail(10).to_html()
    del(df_grouped)
    timestamp = datetime.now()
    text_file = open("/home/andres/Documents/meter_reading/index.html", "w")
    pre_text = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>Energy and Gas consumption</title>
        </head>
        <h1> Electricity and Gas consumption Monitor </h1>
        <p>Modified date:  {timestamp} </p>
     """
    text_file.write(pre_text)
    text_file.write(html)
    post_text = f"""
    <hr>
        <h3>Electricity</h3>
            <figure>
            <img src="subplot_electricity.png">
            </figure>
        <hr>
        <h3>Gas</h3>
            <figure>
            <img src="subplot_gas.png">
            </figure>
    </figure>
    <hr>
    <h3>Projections</h3>
    <figure>
    <img src="subplot_electricity_projection.png">
    </figure>
    <figure>
    <img src="subplot_gas_projection.png">
    </figure>
    </html>
    """
    text_file.write(post_text)
    text_file.close()
    print("----- %s seconds -----" % (time.time() - start_time))
    


try:
    serve_file()
except KeyboardInterrupt:
    print("Program is terminated by the user")
