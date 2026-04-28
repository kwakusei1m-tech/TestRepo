#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv"
)

# Initialise the Dash app
app = dash.Dash(__name__)
app.title = "Automobile Sales Statistics Dashboard"

# ---------------------------------------------------------------------------------
# Create the dropdown menu options (as required)
dropdown_options = [
    {"label": "Yearly Statistics", "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]

# List of years
year_list = [i for i in range(1980, 2024, 1)]
# ---------------------------------------------------------------------------------

# Create the layout of the app
app.layout = html.Div(
    [
        # TASK 2.1: Add title to the dashboard
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 24,
            },
        ),

        # TASK 2.2: Add two dropdown menus
        html.Div(
            [
                html.Label("Select Statistics:"),
                dcc.Dropdown(
                    id="dropdown-statistics",
                    options=dropdown_options,
                    value="Select Statistics",
                    placeholder="Select a report type.",
                    clearable=False,
                ),
            ]
        ),

        html.Div(
            [
                dcc.Dropdown(
                    id="select-year",
                    options=[{"label": i, "value": i} for i in year_list],
                    value="Select-year",
                    placeholder="Select-year",
                    disabled=True,  # start disabled; enabled only for Yearly Statistics
                    clearable=False,
                )
            ]
        ),

        # TASK 2.3: Add a division for output display
        html.Div(
            [
                html.Div(
                    id="output-container",
                    className="chart-grid",
                    style={"display": "flex", "flexWrap": "wrap", "gap": "12px"},
                )
            ]
        ),
    ],
    style={"padding": "18px"},
)

# ---------------------------------------------------------------------------------
# TASK 2.4: Creating Callbacks
# Callback 1: Enable/Disable year dropdown
@app.callback(
    Output(component_id="select-year", component_property="disabled"),
    Input(component_id="dropdown-statistics", component_property="value"),
)
def update_input_container(selected_statistics):
    if selected_statistics == "Yearly Statistics":
        return False
    else:
        return True

# ---------------------------------------------------------------------------------
# Callback 2: Plotting callback - updates output-container with charts
@app.callback(
    Output(component_id="output-container", component_property="children"),
    [
        Input(component_id="dropdown-statistics", component_property="value"),
        Input(component_id="select-year", component_property="value"),
    ],
)
def update_output_container(selected_statistics, input_year):

    # Guard: no report selected yet
    if selected_statistics in (None, "Select Statistics"):
        return [html.Div("Please select a report type.", style={"color": "#503D36"})]

    # -----------------------------
    # Recession Period Statistics
    # -----------------------------
    if selected_statistics == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1]

        # Plot 1: Automobile sales fluctuate over Recession Period (year wise) - line chart
        yearly_rec = recession_data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x="Year",
                y="Automobile_Sales",
                title="Average Automobile Sales fluctuation over Recession Period",
            )
        )

        # Plot 2: Average number of vehicles sold by vehicle type - bar chart
        average_sales = (
            recession_data.groupby("Vehicle_Type")["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title="Average Automobile Sales by Vehicle Type (Recession Period)",
            )
        )

        # Plot 3: Total expenditure share by vehicle type during recessions - pie chart
        exp_rec = (
            recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                names="Vehicle_Type",
                values="Advertising_Expenditure",
                title="Total Advertising Expenditure Share by Vehicle Type (Recession Period)",
            )
        )

        # Plot 4: Effect of unemployment rate on vehicle type and sales - bar chart
        unemp_data = (
            recession_data.groupby(["unemployment_rate", "Vehicle_Type"])["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x="unemployment_rate",
                y="Automobile_Sales",
                color="Vehicle_Type",
                barmode="group",
                labels={
                    "unemployment_rate": "Unemployment Rate",
                    "Automobile_Sales": "Average Automobile Sales",
                },
                title="Effect of Unemployment Rate on Vehicle Type and Sales (Recession Period)",
            )
        )

        return [
            html.Div([R_chart1], style={"flex": "1 1 48%"}),
            html.Div([R_chart2], style={"flex": "1 1 48%"}),
            html.Div([R_chart3], style={"flex": "1 1 48%"}),
            html.Div([R_chart4], style={"flex": "1 1 48%"}),
        ]

    # -----------------------------
    # Yearly Statistics
    # -----------------------------
    elif selected_statistics == "Yearly Statistics":

        # Guard: year not selected yet
        if input_year in (None, "Select-year"):
            return [html.Div("Please select a year to view Yearly Statistics.", style={"color": "#503D36"})]

        yearly_data = data[data["Year"] == input_year]

        # Plot 1: Yearly Automobile sales using line chart for the whole period
        yas = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas,
                x="Year",
                y="Automobile_Sales",
                title="Average Yearly Automobile Sales (1980–2023)",
            )
        )

        # Plot 2: Total Monthly Automobile sales using line chart for selected year
        mas = (
            yearly_data.groupby("Month")["Automobile_Sales"]
            .sum()
            .reset_index()
            .sort_values("Month")
        )
        Y_chart2 = dcc.Graph(
            figure=px.line(
                mas,
                x="Month",
                y="Automobile_Sales",
                title=f"Total Monthly Automobile Sales in {input_year}",
            )
        )

        # Plot 3: Average vehicles sold by vehicle type during the selected year - bar chart
        avr_vdata = (
            yearly_data.groupby("Vehicle_Type")["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title=f"Average Vehicles Sold by Vehicle Type in {input_year}",
            )
        )

        # Plot 4: Total Advertisement Expenditure by vehicle type during selected year - pie chart
        exp_data = (
            yearly_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                names="Vehicle_Type",
                values="Advertising_Expenditure",
                title=f"Total Advertising Expenditure by Vehicle Type in {input_year}",
            )
        )

        return [
            html.Div([Y_chart1], style={"flex": "1 1 48%"}),
            html.Div([Y_chart2], style={"flex": "1 1 48%"}),
            html.Div([Y_chart3], style={"flex": "1 1 48%"}),
            html.Div([Y_chart4], style={"flex": "1 1 48%"}),
        ]

    # Fallback
    return [html.Div("Please select a valid report type.", style={"color": "#503D36"})]


# Run the Dash app
if __name__ == "__main__":
    app.run(debug=True)

