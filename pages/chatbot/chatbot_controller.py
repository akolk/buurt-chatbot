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
    Output('store-buttons', 'data'),
    Output({'type': 'dynamic-button', 'index': dash.dependencies.ALL}, 'children'),
    Output({'type': 'dynamic-button', 'index': dash.dependencies.ALL}, 'style'),
    Input({'type': 'dynamic-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State('store-buttons', 'data'),
    State({'type': 'dynamic-button', 'index': dash.dependencies.ALL}, 'children'),
    State({'type': 'dynamic-button', 'index': dash.dependencies.ALL}, 'style'),
    prevent_initial_call=True
)
def resize_card_and_update_content(button_clicks, button_data, current_contents, current_styles):
    ctx = dash.callback_context
    services.config.logger.info("triggered : " + str(ctx.triggered) + " ctx.triggered_id.index = " + str(ctx.triggered_id.index) + " button_data: "+ str(button_data))

    #if not ctx.triggered or not button_data:
    if not ctx.triggered:
        return dash.no_update

    if all(x is None for x in button_clicks):
        return dash.no_update

    services.config.logger.info("button clicks: "+ str(button_clicks))

    button_id = ctx.triggered_id.index
    services.config.logger.info("button id: "+ str(button_id))
    services.config.logger.info("styles #: "+ str(len(current_styles)))
    services.config.logger.info("styles : "+ str(current_styles))
    services.config.logger.info("orginal_content : " + str(current_contents))

    #triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    #triggered_index = int(triggered_id.split('-')[-1])
    services.config.logger.info(f"{triggered_id}  {triggered_index}");
    
    session_data = {
        0: pd.DataFrame({"x": range(10), "y": [i ** 2   for i in range(10)]}),
        1: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        2: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
        3: pd.DataFrame({"x": range(10), "y": [i ** 1.5 for i in range(10)]}),
    }

    if button_id not in button_data:
        button_data[button_id] = {
            'clicks': 0,
            'original_content': current_contents[button_id],
            'original_style': current_styles[button_id],
    }
    services.config.logger.info("button data : " + str(button_data))
    data = session_data[0]
    df = pd.DataFrame(data)
    
    for i, n in enumerate(button_clicks):
        services.config.logger.info("(i,n) : (" + str(i) + "," + str(n) + ") button_id = "+str(button_id))
        # Example: Show a graph for even index cards and a table for odd index cards
        if i == button_id and n % 3 == 2:
           fig = px.line(df, x="x", y="y", title=f"Graph for Card {button_id}")
           current_contents[button_id] = [dcc.Graph(figure=fig, style={"height": "100%"})]
           current_styles[button_id] = {"width": "500px", "height": "500px", "transition": "all 0.5s"}
        elif i == button_id and n % 3 == 1:
           # store the orginal children somewhere 
           current_contents[button_id] = [html.Div(f"Hier komt wat anders voor {button_id}.")]
           current_styles[button_id] = {"width": "500px", "height": "500px", "transition": "all 0.5s"}
        elif i == button_id and n % 3 == 0:
           services.config.logger.info("reset content: "+ str( button_data[button_id]['original_content']))
           current_contents[button_id] = button_data[button_id]['original_content']
           current_styles[button_id] = button_data[button_id]['original_style']

    return button_data, current_contents, current_styles
