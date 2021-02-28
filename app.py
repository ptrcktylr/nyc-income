import pandas
import json
from bokeh.models import CustomJS, Slider
from bokeh.io import show
from bokeh.models import GeoJSONDataSource
from bokeh.plotting import figure
from bokeh.layouts import row


def get_medians(zipcode, zipcode_df):
    try:
        median = int(zipcode_df[zipcode]['Returns Count'].iloc[0]/2)
        for i in range(1, 7):
            if zipcode_df[zipcode]['Returns Count'].iloc[i] < median:
                median -= zipcode_df[zipcode]['Returns Count'].iloc[i]
            else:
                return zipcode_df[zipcode]['AGI Size'].iloc[i]
    except:
        return "No Information"


COLORMAP = {'$1 under $25,000': '#0868ac',
            '$25,000 under $50,000': '#43a2ca',
            '$50,000 under $75,000': '#7bccc4',
            '$75,000 under $100,000': '#a8ddb5',
            '$100,000 under $200,000': '#ccebc5',
            '$200,000 or more': '#f0f9e8',
            'No Information': '#7a807e', }

neighborhood_raw = pandas.read_excel("neighborhoods.xlsx")

zip_codes_neighborhoods = {}
for idx, zipcodes in enumerate(neighborhood_raw["Zip Codes"]):
    if type(zipcodes) == str:
        for zipcode in zipcodes.split(","):
            zip_codes_neighborhoods[zipcode.strip(
            )] = neighborhood_raw["Neighborhood"][idx]
    else:
        zip_codes_neighborhoods[str(
            zipcodes)] = neighborhood_raw["Neighborhood"][idx]

# IRS Data
raw_df = pandas.read_excel("income_data/11zp33ny.xlsx", header=None)
irs_data = {'Zip Codes': raw_df.iloc[:][0],
            'AGI Size': raw_df.iloc[:][1], 'Returns Count': raw_df.iloc[:][2]}
df = pandas.DataFrame(irs_data)

# Map Data
zip_dfs = {}

with open('nyc_zip_codes.json') as json_file:
    data = json.load(json_file)
    for i in range(len(data['features'])):
        zipcode = data['features'][i]['properties']['postalCode']
        if int(zipcode) in df['Zip Codes']:
            zip_dfs[zipcode] = df.loc[df['Zip Codes'] == int(zipcode)]
        try:
            data['features'][i]['properties']['neighborhood'] = zip_codes_neighborhoods[zipcode]
        except:
            data['features'][i]['properties']['neighborhood'] = "None"

        data['features'][i]['properties']['median_income'] = get_medians(
            zipcode, zip_dfs).strip()
        data['features'][i]['properties']['color'] = COLORMAP[data['features']
                                                              [i]['properties']['median_income']]

geo_source = GeoJSONDataSource(geojson=json.dumps(data))


# Slider


# Tools/Tooltips
TOOLS = ["pan", "box_zoom", "wheel_zoom", "tap", "hover", "reset"]

TOOLTIPS = [("Neighborhood", "@neighborhood"),
            ("Zip Code", "@postalCode"),
            ("Median Income", "@median_income"), ]

# Map
p = figure(title="NYC Median Income Range",
           title_location="above",
           width=900,
           height=760,
           x_axis_location=None,
           y_axis_location=None,
           toolbar_location="above",
           tools=TOOLS, tooltips=TOOLTIPS)

p.grid.grid_line_color = None
p.hover.point_policy = "follow_mouse"
p.patches(xs="xs", ys="ys", color='color', line_color="black",
          line_width=1, line_alpha=1, source=geo_source)
p.min_border_left = 100

# Legend
for key, value in COLORMAP.items():
    p.square(legend_label=key, color=value)

p.legend.location = 'top_left'

show(row(p))
