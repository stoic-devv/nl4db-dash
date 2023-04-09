import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import time
import pandas as pd

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Upload SQL File (*.sql, *.pg)'
            # 'Drag and Drop or ',
            # html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    
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

def process_data(contents):
    # Placeholder function to simulate data processing
    time.sleep(5)
    df = pd.read_csv(contents)
    return df

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        # Simulate file processing
        #df = process_data(contents)
        return html.Div([
            html.Div('File "{}" has been uploaded and processed.'.format(filename)),
            dcc.Loading(id="loading-1", children=[html.Div(id='loading-output-1')], type="default"),
        ])
    else:
        return html.Div('Please upload a file.')

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
