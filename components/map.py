import dash_leaflet as dl
import dash_leaflet.express as dlx

def mapbrt(location):
    return dl.Map(center=location, 
                  zoom=8, 
                  children=[dl.TileLayer(url='https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/standaard/EPSG:3857/{z}/{x}/{y}.png')],
                  style={'width': '100%', 'height': '50vh'}
                 )
