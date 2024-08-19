from services.graphql import graphql_endpoint, graphql_to_dataframe
from services.sparql import sparql_endpoint, sparql_to_dataframe
import services.config 
import os
import uuid
import requests
import re
import pandas as pd
import json


def process_response(obj)
    if obj['language'] == 'prompt':
        chatresponse = obj['query']
    elif obj['language'] == 'graphql':
        res = graphql_endpoint(obj['query'])
        chatresponse = findchatresponse(res)
    elif obj['language'] == 'sparql': 
        res = sparql_endpoint(obj['query'])
        chatresponse = findchatresponse(res)
    elif obj['language'] == 'url':
        chatresponse = obj['query']
    else:
        chatresponse = None
    
    return chatresponse, obj

