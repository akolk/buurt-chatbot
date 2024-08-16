import os
import uuid
import requests
import re
import pandas

def graphql_endpoint(query):
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
        return response.json()
    except Exception as e:
        return {'query': 'Sorry, there was an error contacting the graphql server.'}

def find_key(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):
                result = find_key(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_key(item, target_key)
            if result is not None:
                return result
    return None

def flatten_json(json_data, parent_key='', sep='_'):
    """
    A helper function to flatten a nested JSON object into a single level.
    """
    items = []
    for k, v in json_data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_json(item, f"{new_key}{sep}{i}", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def graphql_to_dataframe(json_data):
    """
    Convert the JSON data to a DataFrame. 
    This function flattens the JSON and converts it to a DataFrame.
    """
    if 'data' not in json_data:
        print("No 'data' key in the JSON response.")
        return pd.DataFrame()

    data = json_data['data']

    # Assuming data is a dictionary of lists or nested dictionaries
    if isinstance(data, dict):
        flat_data = []
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    flat_data.append(flatten_json(item))
            else:
                flat_data.append(flatten_json(value))

        # Convert the list of flat dictionaries to a DataFrame
        df = pd.DataFrame(flat_data)
    else:
        df = pd.DataFrame([flatten_json(data)])

    return df
