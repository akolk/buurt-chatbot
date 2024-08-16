

def graphql_endpoint(query):
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
        return response.json()
    except Exception as e:
        return {'query': 'Sorry, there was an error contacting the graphql server.'}
