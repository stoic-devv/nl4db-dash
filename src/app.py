import base64
import io
import time

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import logging

import utils.dash_components as drc
from widgets.correlation import correlation_heatmap
from utils.pandas_sql import get_df_from_tablename
from utils.process_sql import create_app_db, del_app_db, execute_sql_stream, get_tables_from_app_db

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
app = dash.Dash(__name__)

def user_input():
    return [# Upload area
    drc.UploadText(id='upload-data'),
    #drc.html_div(id='output-data-upload'),
    
    html.Div([
        html.Label('Select a table:'),
        dcc.Dropdown(
                id="table-selector",
                # options=[{"label": i, "value": i} for i in admit_list],
                # value=admit_list[:],
                multi=True,
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
    html.Div(id='loading-output-1')]

app.layout = html.Div(
    id="app-container",
    children=[

    # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("plotly_logo.png"))],
        ),
    
    # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=user_input()
    ),
    # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            # children=[
            #     html.Div(id='output-form')
            # ]
        ),
    dcc.Store(id='sql_processing_state')
])

def parse_contents(contents, filename):
    
    # Placeholder function to simulate data processing
    _, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'sql' in filename:
            # Assume that the user uploaded a CSV file
            execute_sql_stream(decoded)
        else:
            app.logger.error('Invalid file format')
            return html.Div([
            'Invalid file format'
        ])

    except Exception as e:
        app.logger.error(e)
        return html.Div([
            'There was an error processing this file.'
        ])

@app.callback(Output('table-selector', 'options'),
              Output('table-selector', 'disabled'),
              Input('sql_processing_state', 'data'))
def populate_tables_selector(is_processed):
    tables = [{'label': 'x', 'value': 'y'}]
    if is_processed:
        tables = get_tables_from_app_db()
        return [{'label': x, 'value':x} for x in tables], False
    return tables, True

# uploads file and execute sql
@app.callback(Output('loading-output-1', 'children'),
              Output('sql_processing_state', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    # backend processing
    if list_of_contents is not None:
        children = [
            parse_contents(list_of_contents, list_of_names)]
        return children, True
    return [], False

# # 
# @app.callback(Output('output-data-upload', 'children'),
#               Input('upload-data', 'contents'))
# def update_output(contents):
#     if contents is not None:

#         return html.Div('Processing completed.')
#     else:
#         return html.Div('')

@app.callback(Output('attribute-input', 'disabled'),
              Output('submit-button', 'disabled'),
              Input('sql_processing_state', 'data'))
def enable_form(is_processed):
    if is_processed:
        return False, False
    else:
        return True, True

@app.callback(Output('right-column', 'children'),
              Input('submit-button', 'n_clicks'),
              State('table-selector', 'value'),
              State('attribute-input', 'value'))
def submit_form(n_clicks, table_names, attribute_name):
    if n_clicks is not None:
        return [generate_correlation_heatmap(table_names, attribute_name)]
    else:
        return html.Div('')

def generate_correlation_heatmap(table_names, attr):
    tables = [get_df_from_tablename(table) for table in table_names]
    return dcc.Graph(
        id='correlation-heatmap',
        figure= correlation_heatmap(tables, attr),
        style={'width': '90vh', 'height': '90vh'}
    )


if __name__ == '__main__':

    try:
        # ToDo: abstract init
        create_app_db()
        # run app server
        app.run_server(debug=True, port=8050)
    except Exception as e:
        # handle the exception
        logging.error(e)
    finally:
        del_app_db()