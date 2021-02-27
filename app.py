import pandas
from bokeh.models import CustomJS, Slider
from bokeh.io import show
from bokeh.models import GeoJSONDataSource
from bokeh.plotting import figure
from bokeh.layouts import row, column

with open('zip_codes.geojson') as file:
    geo_source = GeoJSONDataSource(geojson=file.read())

TOOLS = "pan,wheel_zoom,reset,hover,save"

p = figure(x_axis_location=None, y_axis_location=None, tooltips=[
    ("Zip Code", "@postalCode"),
])

p.grid.grid_line_color = None
p.hover.point_policy = "follow_mouse"
p.patches(xs="xs", ys="ys", line_color="white",
          line_width=1, line_alpha=0.2, source=geo_source)


show(p)
