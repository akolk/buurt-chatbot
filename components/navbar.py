import dash_bootstrap_components as dbc

def render_navbar(brand_name:str = "Chatbot", brand_color:str = "#165AA7"):
    navbar = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="#")),
                dbc.NavItem(dbc.NavLink("Over", href="#")),
                dbc.Button("Reset", id="reset-button", color="danger", className="ml-auto")
                ],
            brand=brand_name,
            brand_href="/",
            color=brand_color,
            sticky='top',
            links_left=True,
            dark=True,
            expand=True
        )
    return navbar
