import dash_bootstrap_components as dbc
from dash import Dash
import os
import services.config

services.config.APP_TITLE = "Buurt Chatbot"

app = Dash(__name__,
            title=services.config.APP_TITLE,
            update_title='Laden ....',
            suppress_callback_exceptions=True,
            external_stylesheets=[dbc.themes.FLATLY])
