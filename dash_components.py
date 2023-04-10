from dash import dcc
from dash import html

def html_div(id):
    return html.Div(id=id)


def UploadText(id):
    return dcc.Upload(
        id=id,
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
    )