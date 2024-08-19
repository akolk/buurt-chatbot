import dash

from dash import ctx
from dash.dependencies import Input, Output, State, ALL
from app import app
from dash.exceptions import PreventUpdate

from components.textbox import render_textbox
from components.card_ag import makecard_ag
from components.card_text import makecard
from services.graphql import graphql_endpoint, graphql_to_dataframe
from services.sparql import sparql_endpoint, sparql_to_dataframe
from services.endpoint import send_to_endpoint
from services.text import convert_to_superscript
import services.config

import os
import uuid
import requests
import re
import pandas as pd
import json

@app.callback(
    Output(component_id="display-conversation", component_property="children"), 
    Input(component_id="store-conversation", component_property="data")
)
def update_display(chat_history):
    # the chat_history is a string representation of list of json objects. So we need to convert it back to json
    if isinstance(chat_history, str):
        json_data = json.loads(chat_history)
    else:
        json_data = None
        
    return [
        render_textbox(item, box="human") if 'question' in item else render_textbox(item, box="AI")
        for item in json_data
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

    if isinstance(chat_history, str):
        json_data = json.loads(chat_history)

    json_data.append({ 'question': user_input })
    response = send_to_endpoint(user_input)
    json_data.append(response)
    
    chat_history = json.dumps(json_data)
    return chat_history, None

# Callback to handle card expansion and content update
@app.callback(
    Output({"type": "dynamic-card", "index": ALL}, "style"),
    Output({"type": "card-content", "index": ALL}, "children"),
    Input({"type": "dynamic-button", "index": ALL}, "n_clicks"),
    State({"type": "dynamic-card", "index": ALL}, "style")
    #,
    #State("graphql-store", "data")  # Access session data from the store
)
def resize_card_and_update_content(button_clicks, styles):
    if len(button_clicks) < 1:
        raise PreventUpdate
    n_clicks = ctx.triggered[0]["value"]
    if not n_clicks:
        raise PreventUpdate
    button_id = ctx.triggered_id.index
    
    new_styles = []
    new_contents = []

    session_data = {
        0: pd.DataFrame({"x": range(10), "y": [i ** 2 for i in range(10)]}),
        1: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        2: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        3: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        # Add more datasets as needed
    }
    new_styles.append({"width": "500px", "height": "500px", "transition": "all 0.5s"})
    data = session_data[button_id]
    df = pd.DataFrame(data)

    # Example: Show a graph for even index cards and a table for odd index cards
    if n_clicks % 2 == 0:
        fig = px.line(df, x="x", y="y", title=f"Graph for Card {triggered_index + 1}")
        new_contents.append(dcc.Graph(figure=fig, style={"height": "100%"}))
    else:
        new_contents.append(
         dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_table={"height": "100%", "overflowY": "auto"},
            style_cell={"textAlign": "center"},
         )
        )

    return new_styles, new_contents
