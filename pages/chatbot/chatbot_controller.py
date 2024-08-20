import dash

from dash import ctx, html, dcc
from dash.dependencies import Input, Output, State, ALL
from app import app
from dash.exceptions import PreventUpdate
import plotly.express as px

from components.textbox import render_textbox
from components.card_ag import makecard_ag
from components.card_text import makecard
from services.graphql import graphql_endpoint, graphql_to_dataframe
from services.sparql import sparql_endpoint, sparql_to_dataframe
from services.endpoint import send_to_endpoint
from services.text import convert_to_superscript
from services.process_response import process_response
import services.config

import os
import uuid
import requests
import re
import pandas as pd
import json

@app.callback(
    Output('input-box', 'value'),
    Input('reset-button', 'n_clicks')
)
def reset_input(n_clicks):
    services.config.conversation_id = uuid.uuid4();
    dcc.Store(id="store-conversation", data=[])

    if n_clicks:
        return ''

    return dash.no_update

@app.callback(
    Output(component_id="display-conversation", component_property="children"), 
    Input(component_id="store-conversation", component_property="data")
)
def update_display(chat_history):
        
    return [
        render_textbox(item, box="human") if 'question' in item else render_textbox(item, box="AI")
        for item in chat_history
    ]

@app.callback(
    Output(component_id="user-input", component_property="value"),
    Input(component_id="submit", component_property="n_clicks"), 
    Input(component_id="user-input", component_property="n_submit"),
)
def clear_input(n_clicks, n_submit):
    return ""

@app.callback(
    Output(component_id="store-conversation", component_property="data"), 
    Output(component_id="loading-component", component_property="children"),
    Input(component_id="submit", component_property="n_clicks"), 
    Input(component_id="user-input", component_property="n_submit"),
    State(component_id="user-input", component_property="value"), 
    State(component_id="store-conversation", component_property="data"),
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    chat_history.append({ 'question': user_input })

    response = send_to_endpoint(user_input)

    chatbotresponse, compleet = process_response(response)
    chat_history.append({
                         'buttonidx': services.config.buttonidx, 
                         'answer': compleet,
                         'chatbotresponse': chatbotresponse
                        })
    services.config.buttonidx = services.config.buttonidx + 1

    return chat_history, None

# Callback to handle card expansion and content update
@app.callback(
    Output({"type": "dynamic-card", "index": ALL}, "style"),
    Output({"type": "card-content", "index": ALL}, "children"),
    Output({"type": "original-content-store", "index": ALL}, "data"),
    Input({"type": "dynamic-button", "index": ALL}, "n_clicks"),
    State({"type": "dynamic-card", "index": ALL}, "style"),
    State({"type": "original-content-store", "index": ALL}, "data"),
    #,
    #State("graphql-store", "data")  # Access session data from the store
)
def resize_card_and_update_content(button_clicks, styles, original_content):
    services.config.logger.info("button clicks: "+ str(button_clicks))

    if len(button_clicks) < 1:
        raise PreventUpdate
    n_clicks = ctx.triggered[0]["value"]
    if not n_clicks:
        raise PreventUpdate

    button_id = ctx.triggered_id.index
    services.config.logger.info("button id: "+ str(button_id))
    services.config.logger.info("styles #: "+ str(len(styles)))
    services.config.logger.info("styles : "+ str(styles))
    services.config.logger.info("orginal_content : " + str(len(original_content)))

    new_styles = []
    new_contents = []
    orginal_content = []

    session_data = {
        0: pd.DataFrame({"x": range(10), "y": [i ** 2   for i in range(10)]}),
        1: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        2: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        3: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        # Add more datasets as needed
    }
        
    data = session_data[0]
    df = pd.DataFrame(data)

    #new_styles.append({"width": "500px", "height": "500px", "transition": "all 0.5s"})
    #styles[button_id] = {"width": "500px", "height": "500px", "transition": "all 0.5s"}
    
    for i, n in enumerate(button_clicks):

        # Example: Show a graph for even index cards and a table for odd index cards
        if n != None and n % 3 == 2:
           fig = px.line(df, x="x", y="y", title=f"Graph for Card {button_id}")
           new_contents.append(dcc.Graph(figure=fig, style={"height": "100%"}))
           new_styles.append({"width": "500px", "height": "500px", "transition": "all 0.5s"})
        #orginal_content[button_id] = dcc.Graph(figure=fig, style={"height": "100%"})
        elif n != None and n % 3 == 1:
           # store the orginal children somewhere 
           
           new_contents.append(
              html.Div(f"Hier komt wat anders voor {button_id}.") 
           )
           new_styles.append({"width": "500px", "height": "500px", "transition": "all 0.5s"})
           #orginal_content[button_id] = html.Div(f"Hier komt wat anders voor {button_id}.") 
        elif n is None or n % 3 == 0:
           new_styles.append({"width": "100%", "height": "100%", "transition": "all 0.5s"})
           new_contents.append(original_content[i])

    return new_styles, new_contents, original_content
