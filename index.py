from dash.dependencies import Input, Output
from dash import dcc, html 

# import pages
from pages.chatbot.chatbot_view import render_chatbot
from pages.chatbot.chatbot_controller import *
from pages.page_not_found import page_not_found

from app import app
import services.config
import os
import uuid

def serve_content():
    """
    :return: html div component
    """
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

app.layout = serve_content()

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    """
    :param pathname: path of the actual page
    :return: page
    """

    if pathname in services.config.url_base_pathname or pathname in services.config.url_base_pathname + 'chatbot':
        return render_chatbot()
    return page_not_found()

if __name__ == '__main__':
    services.config.conversation_id = uuid.uuid4()
    services.config.sparql_endpoint = os.environ.get("SPARQL_ENDPOINT", "https://api.labs.kadaster.nl/datasets/dst/kkg/services/default/sparql")
    services.config.graphql_endpoint = os.environ.get("GRAPHQL_ENDPOINT", "https://labs.kadaster.nl/graphql")
    services.config.url_base_pathname = os.environ.get("BASE_URL", "/")
    services.config.service_endpoint = os.environ.get("QUESTION_ENDPOINT", 'https://labs.kadaster.nl/predict?question=')
    
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8050))

    app.run_server(debug=True, host=HOST, port=PORT)