from dash import html

def page_not_found():
    return html.Div([
        html.H1('404'),
        html.H2('Pagina niet gevonden'),
        html.H2('Oeps, foutje bedankt!')
    ])
