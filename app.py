from shiny import App, render, ui
import pandas as pd
from datetime import datetime
import time
from datetime import date
import matplotlib.pyplot as plt
import seaborn as sns
import os
from htmltools import HTML, div

season_dict = {1: "Winter",
               2: "Winter",
               3: "Spring",
               4: "Spring",
               5: "Spring",
               6: "Summer",
               7: "Summer",
               8: "Summer",
               9: "Fall",
               10: "Fall",
               11: "Fall",
               12: "Winter"
              }

#load initial dataset

#Read and prepare initial data
mylist =[]
for chunk in pd.read_csv('/home/andres/Documents/meter_reading/db/data.csv', sep=',', chunksize=2000):
    mylist.append(chunk)
df = pd.concat(mylist, axis = 0)
del mylist

#add extra time features to dataset
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date
df['date'] = pd.to_datetime(df['date'])
df['date_object'] = df['timestamp'].dt.date
df['month'] = df['timestamp'].dt.to_period('M')
df['month_number'] = df['timestamp'].dt.month
df['day'] = df['timestamp'].dt.day_name()
df['hour'] = df['timestamp'].dt.hour
df['season'] = df['month_number'].map(season_dict)

#remove extreme point (reason unknown, but best to exclude)
df = df[df['date'] != "2021-12-18"]

def group_per_period(df_in, periods, moving_periods, rounding_places):
    temp_df_grouped = df_in.groupby(periods).agg({'consumption_day': ['min', 'max'], 'consumption_night': ['min', 'max'], 'gas_consumption': ['min', 'max']})
    temp_df_grouped['electricity_high'] = temp_df_grouped[('consumption_day', 'max')] - temp_df_grouped[('consumption_day', 'min')]
    temp_df_grouped['electricity_low'] = temp_df_grouped[('consumption_night', 'max')] - temp_df_grouped[('consumption_night', 'min')]
    temp_df_grouped['electricity_total'] = temp_df_grouped['electricity_high'] + temp_df_grouped['electricity_low']
    temp_df_grouped['gas'] = temp_df_grouped[('gas_consumption', 'max')] - temp_df_grouped[('gas_consumption', 'min')]
    temp_df_grouped = temp_df_grouped.drop([('consumption_day', 'max'), ('consumption_day', 'min'), ('consumption_night', 'min')], axis=1)
    temp_df_grouped = temp_df_grouped.drop([('consumption_night', 'max'), ('gas_consumption', 'min'), ('gas_consumption', 'max')], axis=1)
    temp_df_grouped = temp_df_grouped.round(rounding_places)
    temp_df_grouped.columns = ["electricity high", "electricity low", "electricity total", "gas m3"]
    if moving_periods is not None:
        temp_df_grouped['moving_av_e'] = temp_df_grouped['electricity total'].rolling(moving_periods).mean()
        temp_df_grouped['moving_av_gas'] = temp_df_grouped['gas m3'].rolling(moving_periods).mean()
    temp_df_grouped.reset_index(inplace=True)
    return temp_df_grouped


app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav("Main",
        ui.h4("Energy and Gas consumption"),
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.output_text_verbatim("modified_date"),
                ui.input_date_range("x", "Date range input", start="2021-11-01")),
            ui.panel_main(
                ui.output_table("grouped_table"),
                ui.row(
                    ui.column(6,ui.div(ui.output_plot("electricity_daily_plot")),),
                    ui.column(6,ui.div(ui.output_plot("gas_daily_plots")),),
                    ),
                ui.row(
                    ui.column(6,ui.div(ui.output_plot("electricity_monthly_plot")),),
                    ui.column(6,ui.div(ui.output_plot("gas_monthly_plots")),),
                )       
            ),
        ),
        ),
        ui.nav("Day profile analyses",
            ui.h4("Day profiles"),
            ui.p("This first set of plots displays the current cumulated consumption of Today (black line) and compares it againts an average day of the different seasons"),
            ui.row(
                ui.output_plot("daily_profile_plots")         
            ),
            ui.h4("How is the average consumption per hour?"),
            ui.row(
                ui.output_plot("boxplots_per_hour")         
            ),
            ui.h4("Is there a difference of consumption per day of the week?"),
            ui.row(
                ui.output_plot("weekday_profile_plots")         
            )
        ),
        ui.nav("Parameters",
            ui.p("Some parameters that can influence app behavior on the Main tab"),
            ui.input_numeric("t", "Number of rolling periods", value=10),
            ui.input_numeric("n", "Number of rows", value=5),
            ui.input_date("today_date", "Override today's date")),
        ui.nav("Documentation", "/home/andres/Documents/meter_reading/post writeup/post.html")
        ),
    )


def server(input, output, session):
    
    # def input_df():
    #     #Read and prepare initial data
    #     mylist =[]
    #     for chunk in pd.read_csv('/home/andres/Documents/meter_reading/db/data.csv', sep=',', chunksize=2000):
    #         mylist.append(chunk)
    #     df = pd.concat(mylist, axis = 0)
    #     del mylist

    #     #add extra time features to dataset
    #     df['timestamp'] = pd.to_datetime(df['timestamp'])
    #     df['date'] = df['timestamp'].dt.date
    #     df['date'] = pd.to_datetime(df['date'])
    #     df['date_object'] = df['timestamp'].dt.date
    #     df['month'] = df['timestamp'].dt.to_period('M')
    #     df['month_number'] = df['timestamp'].dt.month
    #     df['day'] = df['timestamp'].dt.day_name()
    #     df['hour'] = df['timestamp'].dt.hour
    #     df['season'] = df['month_number'].map(season_dict)

    #     #remove extreme point (reason unknown, but best to exclude)
    #     df = df[df['date'] != "2021-12-18"]
    #     return df

    def filtered_df():
        df_temp = df[(df['date_object']>=input.x()[0]) & (df['date_object']<=input.x()[1])]
        return df_temp

    @output
    @render.text
    def modified_date():
        d = os.path.getmtime('/home/andres/Documents/meter_reading/db/data.csv')
        dt_m = datetime.fromtimestamp(d)
        mod_date = "Last modified date: "+ dt_m.strftime('%a %d/%m/%Y %H:%M:%S')
        return mod_date    
    
    @output
    @render.table
    def grouped_table():
        df_temp = filtered_df()
        df_temp = group_per_period(filtered_df(),['date', 'day'], moving_periods=None,rounding_places=2)
        return df_temp.tail(input.n())
        
    @output
    @render.plot()
    def electricity_daily_plot():
        plt.figure(figsize=(4,2.8))
        df_temp_day = group_per_period(filtered_df(),['date', 'day', 'month'], moving_periods=input.t(), rounding_places=2)
        df_temp_day = df_temp_day[["date", "electricity total", "moving_av_e"]]
        df_temp_day = df_temp_day.melt("date", var_name="values", value_name="KWH")
        sns.lineplot(data=df_temp_day, x='date', y="KWH", markers=True, hue="values", palette=['#377eb8', '#e41a1c'])
        plt.title("Daily Electricity consumption")
        plt.grid()
        plt.xticks(rotation=0, size=7)
        plt.tight_layout() 

    @output
    @render.plot()
    def electricity_monthly_plot():
        plt.figure(figsize=(4,2.8))
        df_temp_month = group_per_period(filtered_df(), ['month'], moving_periods=None, rounding_places=0)
        ax = sns.barplot(data=df_temp_month, x='month', y="electricity total", color="#377eb8")
        plt.title("Monthly Electricity consumption")
        ax.bar_label(ax.containers[0], size=8)
        plt.xticks(rotation=30, size=7)
        plt.tight_layout() 
        
    @output
    @render.plot()
    def gas_daily_plots():
        plt.figure(figsize=(4,2.8))
        df_temp_day = group_per_period(filtered_df(),['date', 'day', 'month'], moving_periods=input.t(), rounding_places=2)
        df_temp_day = df_temp_day[["date", "gas m3", "moving_av_gas"]]
        df_temp_day = df_temp_day.melt("date", var_name="values", value_name="M3")
        sns.lineplot(data=df_temp_day, x='date', y="M3", markers=False, hue="values", palette=['#377eb8', '#e41a1c'])
        plt.title("Daily Gas consumption")
        plt.grid()
        plt.xticks(rotation=0, size=7)
        plt.tight_layout()

    @output
    @render.plot()
    def gas_monthly_plots():
        plt.figure(figsize=(4,2.8))
        df_temp_month = group_per_period(filtered_df(), ['month'], moving_periods=None, rounding_places=0)
        ax = sns.barplot(data=df_temp_month, x='month', y="gas m3", color="#377eb8")
        plt.title("Monthly Gas consumption")
        ax.bar_label(ax.containers[0], size=8)
        plt.xticks(rotation=30, size=7)
        plt.tight_layout() 
        
    @output
    @render.plot()
    def boxplot_electricity_per_hour():
        temp_df = group_per_period(filtered_df(),['date', 'day', 'hour'], moving_periods=None, rounding_places=2)
        sns.boxplot(data=temp_df, x="hour", y="electricity total", showfliers=False)

    @output
    @render.plot()
    def boxplot_gas_per_hour():
        temp_df = group_per_period(filtered_df(),['date', 'day', 'hour'], moving_periods=None, rounding_places=2)
        sns.boxplot(data=temp_df, x="hour", y="gas m3", showfliers=False)

    @output
    @render.plot()
    def boxplots_per_hour():
        plt.figure(figsize=(12,4))
        plt.subplot(1,2,1)
        temp_df = group_per_period(filtered_df(),['date', 'day', 'hour'], moving_periods=None, rounding_places=2)
        sns.boxplot(data=temp_df, x="hour", y="electricity total", showfliers=False)
        plt.title("Electricity consumption per Hour")

        plt.subplot(1,2,2)
        temp_df = group_per_period(filtered_df(),['date', 'day', 'hour'], moving_periods=None, rounding_places=2)
        sns.boxplot(data=temp_df, x="hour", y="gas m3", showfliers=False)
        plt.title("Gas consumption per Hour")


    def daily_profile_df():
        day_profile_1 = group_per_period(df, periods = ["date", "hour", "season"], moving_periods=None, rounding_places=3)
        day_profile_2 = day_profile_1.groupby(['season', 'hour'])[['electricity total', 'gas m3']].mean()
        day_profile_2.reset_index(inplace=True)
        day_profile_2 = day_profile_2.pivot(index="hour", columns="season").cumsum()
        day_profile_2.reset_index(inplace=True)
        day_profile_2.columns = [' '.join(col).strip() for col in day_profile_2.columns.values]
        day_profile_electricity = day_profile_2[day_profile_2.columns.drop(list(day_profile_2.filter(regex="gas")))]
        day_profile_electricity = day_profile_electricity.melt(id_vars='hour', value_vars=['electricity total Fall', 'electricity total Spring', 'electricity total Summer', 'electricity total Winter'])
        day_profile_gas = day_profile_2[day_profile_2.columns.drop(list(day_profile_2.filter(regex="electricity")))]
        day_profile_gas = day_profile_gas.melt(id_vars='hour', value_vars=['gas m3 Fall', 'gas m3 Spring', 'gas m3 Summer', 'gas m3 Winter'])
        
        #create today cumsum
        #today_df = df[df['date_object']==date.today()]
        today_df = df[df['date_object']==input.today_date()]
        today_df = group_per_period(today_df,periods=['hour'], moving_periods=None, rounding_places=3)
        today_df = today_df[['electricity total', 'gas m3']].cumsum()
        today_df['hour'] = today_df.index
        electricity_today = today_df.drop(columns=['gas m3'])
        electricity_today['variable'] = "Today"
        electricity_today.columns = ['value', 'hour', 'variable']
        gas_today = today_df.drop(columns=['electricity total'])
        gas_today['variable'] = "Today"
        gas_today.columns = ['value', 'hour', 'variable']

        #append today into seasonal profiles dataframes
        day_profile_electricity = pd.concat([day_profile_electricity, electricity_today])
        day_profile_gas = pd.concat([day_profile_gas, gas_today])
        
        return day_profile_electricity, day_profile_gas

    @output
    @render.plot()
    def daily_profile_plots():
        plt.figure(figsize=(12,4))
        plt.subplot(1,2,1)
        sns.lineplot(daily_profile_df()[0], x="hour", y='value', hue='variable', palette=["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "black"],marker='o')
        plt.title("Electricity Day profile")
        plt.grid()

        plt.subplot(1,2,2)
        sns.lineplot(daily_profile_df()[1], x="hour", y='value', hue='variable', palette=["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "black"], marker='o')
        plt.title("Gas Day profile")
        plt.grid()

    @output
    @render.plot()
    def weekday_profile_plots():
        temp_weekday_df= group_per_period(df, periods = ["date", "day"], moving_periods=None, rounding_places=3)
        plt.figure(figsize=(12,4))
        plt.subplot(1,2,1)
        sns.boxplot(temp_weekday_df, x="day", y='electricity total', showfliers=False, color='g')
        plt.title("Electricity consupmtion profile")

        plt.subplot(1,2,2)
        sns.boxplot(temp_weekday_df, x="day", y='gas m3', showfliers=False, color='g')
        plt.title("Gas consumption profile")


app = App(app_ui, server, debug = True)