import os
import uuid
import requests
import re
import pandas
import services.config

def sparql_endpoint(query):
    headers ={
                'Content-Type': 'application/sparql-query',
                'accept': 'application/sparql-results+json'
            }
    
    try:
        response = requests.post(services.config.sparql_endpoint, data=query, headers=headers)
        return response.json()
    except Exception as e:
        return {'query': 'Sorry, there was an error contacting the sparql server.'}

def sparql_to_dataframe(json_data):
    if json_data is None:
        return pd.DataFrame()

    # Extract the variables from the head of the JSON response
    variables = json_data['head']['vars']

    # Extract the results from the JSON response
    results = json_data['results']['bindings']

    # Prepare a list to hold the rows of the DataFrame
    data = []

    # Iterate through the results and extract each variable's value
    for result in results:
        row = {}
        for var in variables:
            row[var] = result[var]['value'] if var in result else None
        data.append(row)

    # Convert the list of rows into a DataFrame
    df = pd.DataFrame(data, columns=variables)
    return df
