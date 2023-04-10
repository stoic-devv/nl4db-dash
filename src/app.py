import base64
import io
import time

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import pandas as pd

import dash_components as drc


app = dash.Dash(__name__)

app.layout = html.Div([
    drc.UploadText(id='upload-data'),
    drc.html_div(id='output-data-upload'),
    
    html.Div([
        html.Label('Select a table:'),
        dcc.Dropdown(
            id='table-selector',
            options=[{'label': 'Table 1', 'value': 'table1'},
                     {'label': 'Table 2', 'value': 'table2'},
                     {'label': 'Table 3', 'value': 'table3'}],
            value=None,
            disabled=True
        ),
        html.Label('Enter a sensitive attribute:'),
        dcc.Input(
            id='attribute-input',
            type='text',
            placeholder='Sensitive attribute',
            disabled=True
        ),
        html.Button('Submit', id='submit-button', disabled=True)
    ], style={'display': 'inline-block', 'margin': '10px'}),
    html.Div(id='output-form'),
    html.Div(id='loading-output-1')
])

def parse_contents(contents, filename):
    
    # Placeholder function to simulate data processing
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'sql' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(content_string))
        elif 'sql' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        print(df.head())
        return df

    except Exception as e:
        print('Error: ' + e)
        return html.Div([
            'There was an error processing this file.'
        ])

# @app.callback(Output('output-data-upload', 'children'),
#               Input('upload-data', 'contents'),
#               State('upload-data', 'filename'))
# def update_output(contents, filename):
#     if contents is not None:
#         # Simulate file processing
#         df = parse_contents(contents, filename)
#         return html.Div([
#             html.Div('File "{}" has been uploaded and processed.'.format(filename)),
#             dcc.Loading(id="loading-1", children=[html.Div(id='loading-output-1')], type="default"),
#         ])
#     else:
#         return html.Div('Please upload a file.')

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(list_of_contents, list_of_names)]
        return children

@app.callback(Output('loading-output-1', 'children'),
              Input('upload-data', 'contents'))
def update_output(contents):
    if contents is not None:
        # Simulate backend processing
        time.sleep(5)
        return html.Div('Processing completed.')
    else:
        return html.Div('')

@app.callback(Output('table-selector', 'disabled'),
              Output('attribute-input', 'disabled'),
              Output('submit-button', 'disabled'),
              Input('loading-output-1', 'children'))
def enable_form(loading_output):
    if loading_output == 'Processing completed.':
        return True, True, True
    else:
        return True, True, True

@app.callback(Output('output-form', 'children'),
              Input('submit-button', 'n_clicks'),
              State('table-selector', 'value'),
              State('attribute-input', 'value'))
def submit_form(n_clicks, table_name, attribute_name):
    if n_clicks is not None:
        # Placeholder function to simulate form submission
        time.sleep(2)
        return html.Div('Form submitted with table "{}" and attribute "{}".'.format(table_name, attribute_name))
    else:
        return html.Div('')

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
