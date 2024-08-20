from services.graphql import graphql_endpoint, graphql_to_dataframe
from services.sparql import sparql_endpoint, sparql_to_dataframe
import services.config 
import os
import uuid
import requests
import re
import pandas as pd
import json


def process_response(obj):
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

def find_all_by_key(obj, key_to_find):
    services.config.logger.info('find_all_by_key: '+ key_to_find + "   " + str(obj) )
    if not obj:
        return []
    
    result = []
    for key, value in obj.items():
        if key == key_to_find or key.startswith(key_to_find + '_'):
            result.append(value)
        elif isinstance(value, dict):
            result.extend(find_all_by_key(value, key_to_find))
    services.config.logger.info('find_all_by_key: found ' + str(result) )
    return result


def findchatresponse(data):
    answer_chatbot = [{'chatbotanswer': item} for item in find_all_by_key(data, 'chatbotanswer')]

