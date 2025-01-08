# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash import callback
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

dd_options = []
dd_options.append({'label':'All Sites', 'value':'All'})
for sitename in spacex_df['Launch Site'].unique():
    dd_options.append({'label':sitename, 'value':sitename})

#print(dd_options)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options=dd_options, value='All'),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=min_payload, max=max_payload, step=1000, value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(input_launch_site):
    subset_df = spacex_df[['Launch Site', 'class']]
    if input_launch_site == 'All':
        filtered_df = subset_df[subset_df['class'] == 1].groupby('Launch Site').sum().reset_index()
        piechart = px.pie(filtered_df, names='Launch Site',values='class')
        piechart.update_layout(title={'text': 'Percentage of successful launches by Launch Site', 'x': 0.5, 'xanchor': 'center'})
    else:
        selected_df = subset_df[subset_df['Launch Site'] == input_launch_site]
        filtered_df = selected_df.groupby('class').count().reset_index()
        filtered_df.rename(columns={'Launch Site':'Launch Result'}, inplace=True)
        filtered_df['class'].replace({0:'Failure', 1:'Success'}, inplace=True)
        #legend = {'0':'Failure', '1':'Success'}
        piechart = px.pie(filtered_df, names='class',values='Launch Result')
        chart_title = 'Distribution of Launch Results for site %s' % input_launch_site
        piechart.update_layout(title={'text': chart_title, 'x': 0.5, 'xanchor': 'center'})
    
    return(piechart)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def update_scatter_chart(input_launch_site, input_range):
    min = float(input_range[0])
    max = float(input_range[1])
    subset_df = spacex_df[(spacex_df['Payload Mass (kg)'] > min) & (spacex_df['Payload Mass (kg)'] < max)]
    if input_launch_site == 'All':
        chart_title = 'Distribution of Launch Results for Payload Mass (kg) between %.1f & %.1f' % (min, max)
        scatter = px.scatter(data_frame=subset_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        scatter.update_layout(title={'text': chart_title, 'x': 0.5, 'xanchor': 'center'})
    else:
        chart_title = 'Distribution of Launch Results for site %s and Payload Mass (kg) between %.1f & %.1f' % (input_launch_site, min, max)
        filtered_df = subset_df[subset_df['Launch Site'] == input_launch_site]
        scatter = px.scatter(data_frame=filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
        scatter.update_layout(title={'text': chart_title, 'x': 0.5, 'xanchor': 'center'})

    return(scatter)

# Run the app
if __name__ == '__main__':
    app.run_server()
