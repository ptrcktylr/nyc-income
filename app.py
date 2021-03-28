import pandas
import json
from bokeh.models import CustomJS, Slider
from bokeh.models import GeoJSONDataSource, CategoricalColorMapper
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row


def get_medians(zipcode, zipcode_df):  # function to calculate median from dataframe
    try:
        median = int(zipcode_df[zipcode]['Number of Returns'].iloc[0]/2)
        for i in range(1, 7):
            if zipcode_df[zipcode]['Number of Returns'].iloc[i] < median:
                median -= zipcode_df[zipcode]['Number of Returns'].iloc[i]
            else:
                return zipcode_df[zipcode]['AGI'].iloc[i]
    except:
        return "No Information"


# color mapping variables
custom_colors = ['#0868ac', '#43a2ca',
                 '#7bccc4', '#a8ddb5', '#ccebc5', '#f0f9e8', '#7a807e']

color_factors = ['$1 under $25,000', '$25,000 under $50,000', '$50,000 under $75,000',
                 '$75,000 under $100,000', '$100,000 under $200,000', '$200,000 or more', 'No Information']

color_mapper = CategoricalColorMapper(
    palette=custom_colors, factors=color_factors)


# neighborhood name to zipcode data
neighborhood_raw = pandas.read_excel("data/neighborhoods.xlsx")

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


def get_income_data(year):  # function to get income data from csv
    year = str(year)
    df = pandas.read_csv(f"data/income_data/formatted_data/{year}_irs_data")
    return df


zip_dfs = {}
all_income_data = {}

for i in range(2011, 2019):
    all_income_data[str(i)] = get_income_data(i)
    zip_dfs[str(i)] = {}

# Map Data

with open('data/nyc_zip_codes.json') as json_file:
    data = json.load(json_file)
    for i in range(len(data['features'])):
        zipcode = data['features'][i]['properties']['postalCode']
        for year, df in all_income_data.items():
            if int(zipcode) in df['Zip Code'].values:
                zip_dfs[year][zipcode] = df.loc[df['Zip Code'].values ==
                                                int(zipcode)]
            try:
                data['features'][i]['properties']['neighborhood'] = zip_codes_neighborhoods[zipcode]
            except:
                data['features'][i]['properties']['neighborhood'] = "None"

            data['features'][i]['properties'][f'{year}_median_income'] = get_medians(
                zipcode, zip_dfs[year]).strip()

        data['features'][i]['properties']['current_median_income'] = data['features'][i]['properties']['2011_median_income']

geo_source = GeoJSONDataSource(geojson=json.dumps(data))


# Tools/Tooltips
TOOLS = ["pan", "box_zoom", "wheel_zoom", "tap", "hover", "reset"]

TOOLTIPS = {}

for year in range(2011, 2019):
    TOOLTIPS[str(year)] = [("Neighborhood", "@neighborhood"),
                           ("Zip Code", "@postalCode"),
                           ("Median Income", f"@{year}_median_income"),
                           ("Latitude, Longitude", "$y, $x")]

# Map
p = figure(title="NYC Median Income Range",
           title_location="above",
           width=900,
           height=760,
           toolbar_location="above",
           tools=TOOLS, 
           active_drag=None,
           tooltips=TOOLTIPS['2011'])

p.grid.grid_line_color = None
p.hover.point_policy = "follow_mouse"

r = p.patches(xs="xs", ys="ys",
              fill_color={'field': 'current_median_income',
                          'transform': color_mapper},
              line_color="black", line_width=1, line_alpha=1, source=geo_source)

# margin
p.min_border_left = 100


# Slider

callback = CustomJS(args=dict(tt=p.hover, tooltip_opts=TOOLTIPS, renderer=r, source=geo_source), code="""
    
    tt[0].tooltips = tooltip_opts[cb_obj.value];

    var data = source.data
    data['current_median_income'] = data[`${cb_obj.value}_median_income`];
    source.change.emit();

""")

slider = Slider(title='Year', start=2011, end=2018,
                step=1, value=2011, margin=(5, 5, 5, 20))
slider.js_on_change('value', callback)

# Legend
for hex_code, factor in zip(custom_colors, color_factors):
    p.square(legend_label=factor, color=hex_code)

p.legend.location = 'top_left'

layout = row(p, slider)
curdoc().add_root(layout)
curdoc().title = "NYC Median Income"
