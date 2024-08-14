import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import plotly.express as px

# Initialize the Dash app with a Bootstrap theme
url_base_pathname=os.environ.get("BASE_URL", "")

app = dash.Dash(__name__,url_base_pathname=url_base_pathname, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for graphs
df = px.data.iris()

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Input(id='chat-input', type='text', placeholder='Type a message...', className='mb-2'),
            dbc.Button('Send', id='send-button', color='primary', className='mb-2'),
            html.Div(id='chat-output', style={'border': '1px solid #ccc', 'padding': '10px', 'height': '300px', 'overflowY': 'scroll'}),
        ], width=4),
        dbc.Col([
            html.Div(id='canvas-output', style={'position': 'relative', 'height': '400px', 'border': '1px solid #ccc'}),
        ], width=8)
    ])
])

# Endpoint where chat input is sent
QUESTION_ENDPOINT = 'https://example.com/question'

@app.callback(
    Output('chat-output', 'children'),
    Output('canvas-output', 'children'),
    Input('send-button', 'n_clicks'),
    State('chat-input', 'value'),
    State('chat-output', 'children'),
    State('canvas-output', 'children')
)
def update_chat(n_clicks, user_input, chat_history, canvas_content):
    if n_clicks is None or not user_input:
        return chat_history, canvas_content
    
    response = send_to_endpoint(user_input)
    chat_output = chat_history + [html.Div([html.P(f'User: {user_input}'), html.P(f'Bot: {response["answer"]}')])]

    if 'graphql' in response:
        # Generate graph based on GraphQL query (mock example)
        fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')
        new_card = dbc.Card(
            dcc.Graph(figure=fig),
            style={'position': 'absolute', 'top': f'{10}px', 'left': f'{10}px', 'width': '300px'},
            draggable=True
        )
        canvas_content = (canvas_content or []) + [new_card]

    elif 'sparql' in response:
        # Handle SPARQL query response (mock example)
        sparql_result = f"SPARQL Result: {response['sparql']}"
        new_card = dbc.Card(
            html.Div(sparql_result),
            style={'position': 'absolute', 'top': f'{100}px', 'left': f'{10}px', 'width': '300px'},
            draggable=True
        )
        canvas_content = (canvas_content or []) + [new_card]

    elif 'url' in response:
        # Handle URL response (mock example)
        new_card = dbc.Card(
            html.A('Open Link', href=response['url'], target='_blank', className='btn btn-primary'),
            style={'position': 'absolute', 'top': f'{190}px', 'left': f'{10}px', 'width': '300px'},
            draggable=True
        )
        canvas_content = (canvas_content or []) + [new_card]

    return chat_output, canvas_content

def send_to_endpoint(user_input):
    # Send the user input to the external question endpoint
    try:
        response = requests.post(QUESTION_ENDPOINT, json={'question': user_input})
        return response.json()
    except Exception as e:
        return {'answer': 'Sorry, there was an error contacting the server.'}

if __name__ == '__main__':
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8050))

    app.run_server(debug=True, host=HOST, port=PORT)
