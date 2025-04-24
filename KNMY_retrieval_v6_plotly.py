#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 13:44:10 2024
@author: mayk
"""
#%% Sources and manuals used:
# https://github.com/EnergieID/KNMI-py
# https://www.knmi.nl/kennis-en-datacentrum/achtergrond/data-ophalen-vanuit-een-script
# https://www.daggegevens.knmi.nl/klimatologie/uurgegevens


#%% Retrieve KNMI data through API
from knmy import knmy
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

start   = '20240101'
end     = '20241231'
variables_selected = ['TEMP']
inseason=False
parse=True

stations_selected1 = [260] # De Bilt
disclaimer, stations1, variables, data_260 = knmy.get_hourly_data(stations=stations_selected1, start=start, end=end,inseason=inseason, variables=variables_selected, parse=parse)

stations_selected2 = [380] # Maastricht
disclaimer, stations2, variables, data_380 = knmy.get_hourly_data(stations=stations_selected2, start=start, end=end,inseason=inseason, variables=variables_selected, parse=parse)



# 1. Read the CSV data without parsing dates
df = data_260
df['TD'] = df['TD'] / 10  # Convert temperature to Celsius
df['T'] = df['T'] / 10  # Convert temperature to Celsius
df['T_260'] = df['T']

df = df.drop('STN', axis=1)
df = df.drop('T10N', axis=1)

#combine two dataframes, where df2.T is put into df.T_380
df2 = data_380
df['T_380'] = df2['T']/10

# 2. Combine 'YYYYMMDD' and 'HH' to create a datetime column
df['datetime'] = df['YYYYMMDD'].astype(str) + (df['HH'].astype(int) - 1).astype(str).str.zfill(2) + '00'  # Subtract 1 from HH, Adding '00' for minutes and seconds
df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d%H%M%S')
df = df.set_index('datetime')
print(df)


# Save data to excel
output_filename = f"KNMI_data_{variables_selected}_{start}_{end}.xlsx"
df.to_excel(output_filename, index=False)
print(f"Data saved to {output_filename}")



# Show all stations information: knmi.stations
# station: 260 = De Bilt, 138 en 380 = Maastricht, 616 = Amsterdam, 250 = Terschelling, 


# print(disclaimer)
# print(stations)
# print(variables)
# print(data)
# print(df.legend)





#%% Plotly HTML plotting
# Create subplots
fig = make_subplots(rows=2, cols=1, subplot_titles=(
    "Hourly Temperature over time",
    f"De Bilt:     Max: {df['T_260'].max():.1f}°C, Min: {df['T_260'].min():.1f}°C, Avg: {df['T_260'].mean():.1f}°C<br>"
    f"Maastricht: Max: {df['T_380'].max():.1f}°C, Min: {df['T_380'].min():.1f}°C, Avg: {df['T_380'].mean():.1f}°C<br><br>"
    f"Temperature Distribution"
))

# Temperature over time plot
fig.add_trace(go.Scatter(x=df.index, y=df["T_260"], mode='lines', name=f"KNMI Temperature at Station: {stations1['name'][260]}"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["T_380"], mode='lines', name=f"KNMI Temperature at Station: {stations2['name'][380]}"), row=1, col=1)

fig.update_xaxes(title_text="Date", row=1, col=1)
fig.update_yaxes(title_text="Temperature", row=1, col=1)


# Histogram plot
data_hist1 = df["T_260"]
fig.add_trace(go.Histogram(x=data_hist1, name=f"KNMI Temperature at Station: {stations1['name'][260]}", autobinx=False, xbins=dict(start=min(data_hist1), end=max(data_hist1), size=2.0), histnorm=''), row=2, col=1)

data_hist2 = df["T_380"]
fig.add_trace(go.Histogram(x=data_hist2, name=f"KNMI Temperature at Station: {stations2['name'][380]}", autobinx=False, xbins=dict(start=min(data_hist2), end=max(data_hist2), size=2.0), histnorm=''), row=2, col=1)

fig.update_xaxes(title_text="Temperature [°C]", row=2, col=1)
fig.update_yaxes(title_text="Ocurrence [hours/year]", row=2, col=1) # , tickformat=".0%"

fig.update_layout(title_text=f"KNMI Station Data, Date Range: {start}-{end}", title_x=0.5)




# Save figure to html
output_filename = f"KNMI_data_{stations1['name'][260]}_{variables_selected}_{start}_{end}.html"
fig.write_html(output_filename)
print(f"Data and plots saved to {output_filename}")
fig.show()