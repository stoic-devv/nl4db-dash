import base64

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto
import dash_mantine_components as dmc

import pandas as pd

import logging

import utils.dash_components as drc
from utils.pandas_sql import get_df_from_tablename, get_table_columns
from utils.process_sql import create_app_db, del_app_db, execute_sql_stream, get_tables_from_app_db

from widgets.correlation import correlation_heatmap
from widgets.association_rules import get_multi_ar

import warnings

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
warnings.filterwarnings('ignore', category=UserWarning)


app = dash.Dash(__name__)
app.logger.propagate = True
app.logger.setLevel(logging.DEBUG)

def user_input():
    return [# Upload area
    drc.UploadText(id='upload-data'),
    #drc.html_div(id='output-data-upload'),
    
    html.Div([
        dmc.MultiSelect(
                id="table-selector",
                label="Select table(s)"
            ),
        dmc.MultiSelect(
            label = "Sensitive Attribute",
            id="sensitive-attr",
            placeholder="Select Sensitive/Protected Attributes",
            style={"width": 400, "marginBottom": 10}
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
            children=[html.Img(src=app.get_asset_url("uic-circmark-black.PNG"), style={'height': '50px', 'width': '50px'})],
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
    dcc.Store(id='sql_processing_state'),
    dcc.Store(id='selected_table_dfs')
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

# populates table selection dropdown with tables from the schema
@app.callback(Output('table-selector', 'data'),
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
def process_sql_file(list_of_contents, list_of_names):
    # backend processing
    if list_of_contents is not None:
        children = [
            parse_contents(list_of_contents, list_of_names)]
        return children, True
    return [], False


@app.callback(Output('sensitive-attr', 'data'),
              Input('selected_table_dfs', 'data'))
def populate_attrs(table_dicts):
    # https://community.plotly.com/t/dropdown-sub-category-list/65593
    data = []
    
    # tables not selected
    if not table_dicts:
        return []

    for name,dat in table_dicts.items():
        df = pd.DataFrame.from_records(dat)
        for col in df.columns:
            data.append({"value":col, "label": col, "group": name})
    """
        data=[
                {"value": "sub-1", "label": "Sub Category 1", "group": "Main Category"},
                {"value": "sub-3", "label": "Sub Category 3",  "group": "Secondary Category"},
                {"value": "sub-2", "label": "Sub Category 2", "group": "Main Category"},
                {"value": "sub-4", "label": "Sub Category 4", "group": "Secondary Category"},
            ],
    """

    return data

# stores the selected tables as dataframes available as shared data for components
@app.callback(Output('selected_table_dfs', 'data'),
              Input('selected_table_dfs', 'data'),
              Input('table-selector', 'value'))
def store_selected_tables_as_df(table_dicts, table_names):
    if table_names:
        #app.logger.info(table_names)
        table_dicts.update({table_names[-1]: 
        get_df_from_tablename(table_names[-1]).to_dict('records')})
        return table_dicts
    return {}

@app.callback(Output('sensitive-attr', 'disabled'),
              Output('submit-button', 'disabled'),
              Input('sql_processing_state', 'data'))
def enable_form(is_processed):
    if is_processed:
        return False, False
    else:
        return True, True

@app.callback(Output('right-column', 'children'),
              Input('submit-button', 'n_clicks'),
              Input('selected_table_dfs', 'data'),
              State('sensitive-attr', 'value'))
def submit_form(n_clicks, selected_tables_dict, sensitive_attr):
    if n_clicks is not None:
        return [generate_correlation_heatmap(selected_tables_dict, sensitive_attr),
        generate_association_rules(selected_tables_dict, sensitive_attr)]
    else:
        return html.Div('')

# ToDo: current implementation only for one sensitive attr
def generate_correlation_heatmap(tables_dict, attr):
    tables = [pd.DataFrame.from_records(v) for _,v in tables_dict.items()]
    app.logger.info(attr[-1])
    return dcc.Graph(
        id='correlation-heatmap',
        figure= correlation_heatmap(tables, attr[-1]),
        style={'width': '600px', 'height': '500px'}
    )

# ToDo: get for all selected tables
def generate_association_rules(tables_dict, attr):
    tables = [pd.DataFrame.from_records(v) for k,v in tables_dict.items()]
    return html.Div([cyto.Cytoscape(
        id='cytoscape',
        elements=get_multi_ar(tables[0]),
        style={'width': '400px', 'height': '500px'}
    )])


if __name__ == '__main__':

    try:
        # ToDo: abstract init
        create_app_db()
        # run app server
        app.run_server(debug=True, port=8050)
    except Exception as e:
        # handle the exception
        app.logger.error(e)
    finally:
        del_app_db()