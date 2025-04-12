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
import logging

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
# Custom CSS for sticky note style
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Chatbot Sticky Notes</title>
        {%favicon%}
        {%css%}
        <style>
            /* Sticky note style */
            .sticky-note-card {
                background-color: #FFEB3B;
                width: 250px;
                padding: 10px;
                margin-bottom: 10px;
                box-shadow: 5px 5px 10px rgba(0,0,0,0.2);
                border: 1px solid #d9d9d9;
                font-family: 'Courier New', Courier, monospace;
                transform: rotate(-2deg);
            }
                        /* Sticky note style */
            .sticky-note-card-ai {
                background-color: #FFEB3B;
                width: 250px;
                padding: 10px;
                margin-bottom: 10px;
                box-shadow: 5px 5px 10px rgba(0,0,0,0.2);
                border: 1px solid #d9d9d9;
                font-family: 'Courier New', Courier, monospace;
                transform: rotate(2deg);
            }
            .card-text {
                font-size: 1em;
                color: #333333;
            }
            .chat-output {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    services.config.conversation_id = uuid.uuid4()
    services.config.sparql_endpoint = os.environ.get("SPARQL_ENDPOINT", "https://api.labs.kadaster.nl/datasets/dst/kkg/services/default/sparql")
    services.config.graphql_endpoint = os.environ.get("GRAPHQL_ENDPOINT", "https://labs.kadaster.nl/graphql")
    services.config.url_base_pathname = os.environ.get("BASE_URL", "/")
    services.config.service_endpoint = os.environ.get("QUESTION_ENDPOINT", 'https://labs.kadaster.nl/predict?question=')
    services.config.buttonid = 0
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    services.config.logger = logging.getLogger(services.config.APP_TITLE)

    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8050))

    app.run(debug=True, host=HOST, port=PORT)
