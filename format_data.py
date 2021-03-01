import pandas
import json

# Format IRS Data

nyc_zip_codes = []
with open('nyc_zip_codes.json') as json_file:
    data = json.load(json_file)
    for i in range(len(data['features'])):
        nyc_zip_codes.append(
            int(data['features'][i]['properties']['postalCode']))


def excel_to_csv(year):
    year = str(year)
    raw_df = pandas.read_excel(
        f"income_data/raw_data/{year[-2:]}zp33ny.xlsx", header=None)
    new_df = pandas.DataFrame(columns=["Zip Code", "AGI", "Number of Returns"])
    for zipcode, agi, num_returns in zip(raw_df[0], raw_df[1], raw_df[2]):
        if zipcode in nyc_zip_codes:
            new_df = new_df.append({"Zip Code": str(
                zipcode), "AGI": agi, "Number of Returns": str(num_returns)}, ignore_index=True)
    new_df.to_csv(f"income_data/formatted_data/{year}_irs_data", index=False)


for i in range(2011, 2019):
    excel_to_csv(i)
