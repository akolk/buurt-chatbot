import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import plotly.express as px
import os

# Initialize the Dash app with a Bootstrap theme
url_base_pathname=os.environ.get("BASE_URL", "")

app = dash.Dash(__name__,url_base_pathname=url_base_pathname, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for graphs
df = px.data.iris()

# Layout of the app
app.layout = dbc.Container([
    dcc.Store(id='store-chat-history', data=[]),
    dcc.Store(id='store-canvas-content', data=[]),
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
    Output('store-chat-history', 'data'),
    Output('store-canvas-content', 'data'),
    Output('chat-output', 'children'),
    Output('canvas-output', 'children'),
    Input('send-button', 'n_clicks'),
    State('chat-input', 'value'),
    State('store-chat-history', 'data'),
    State('store-canvas-content', 'data')
)
def update_chat(n_clicks, user_input, chat_history, canvas_content):
    if n_clicks is None or not user_input:
        return chat_history, canvas_content, [], []

    # Send user input to the external question endpoint
    response = send_to_endpoint(user_input)

    # Update chat history with user input and bot response
    new_message = {'user': user_input, 'bot': response.get('answer', 'Sorry, I don\'t understand.')}
    chat_history.append(new_message)

    # Update chat output in the UI
    chat_output = [html.Div([html.P(f'User: {msg["user"]}'), html.P(f'Bot: {msg["bot"]}')]) for msg in chat_history]

    # Update the canvas content based on the response
    if 'graphql' in response:
        # Generate graph based on GraphQL query (mock example)
        fig = px.scatter(df, x='sepal_width', y='sepal_length', color='species')
        new_card = dbc.Card(
            dcc.Graph(figure=fig),
            style={'position': 'absolute', 'top': f'{10 + len(canvas_content) * 80}px', 'left': f'{10}px', 'width': '300px'},
            draggable=True
        )
        canvas_content.append(new_card)

    elif 'sparql' in response:
        # Handle SPARQL query response (mock example)
        sparql_result = f"SPARQL Result: {response['sparql']}"
        new_card = dbc.Card(
            html.Div(sparql_result),
            style={'position': 'absolute', 'top': f'{10 + len(canvas_content) * 80}px', 'left': f'{10}px', 'width': '300px'},
            draggable=True
        )
        canvas_content.append(new_card)

    elif 'url' in response:
        # Handle URL response (mock example)
        new_card = dbc.Card(
            html.A('Open Link', href=response['url'], target='_blank', className='btn btn-primary'),
            style={'position': 'absolute', 'top': f'{10 + len(canvas_content) * 80}px', 'left': f'{10}px', 'width': '300px'},
            draggable=True
        )
        canvas_content.append(new_card)

    return chat_history, canvas_content, chat_output, canvas_content

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
