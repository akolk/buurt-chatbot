import dash_bootstrap_components as dbc
from dash import dcc, html

def render_chat_input():
    chat_input = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Stel een vraag ....", type="text"),
        html.Div(
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Sleep, plaats of ',
                    html.A('selecteer bestand(en)')
                ]),
                #multiple=True,  # Allow multiple files to be uploaded
                style={
                    'width': '100%',
                    'height': '100%',
                    'lineHeight': '38px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '4px',
                    'textAlign': 'center',
                }
            ),
            className="form-control",  # Ensure it behaves like an input field
        ),
        dbc.Button(id="submit", children=">", color="success"),
    ],
    )
    return chat_input
