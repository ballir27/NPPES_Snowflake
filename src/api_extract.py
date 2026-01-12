import os
from dotenv import load_dotenv
import polars as pl
import requests
from urllib.parse import urlencode, quote


from local_logging import get_logger

logger = get_logger("api_extract")

load_dotenv()

census_api_url = os.getenv("census_api_url")
census_api_key = os.getenv("census_api_key")

def zip_pop_from_api():
    base_url = census_api_url
    params = {
        "get": "DP05_0001E",
        "for": "zip code tabulation area:*",
        "key": census_api_key}
    query_string = urlencode(params, quote_via=quote)
    query_string = query_string.replace('%2A', '*')
    query_string = query_string.replace('%3A', ':')
    full_url = f"{base_url}?{query_string}"
    # full_url_for_debugging = "https://api.census.gov/data/2023/acs/acs5/profile?get=DP05_0001E&for=zip%20code%20tabulation%20area:*&key=dc742cafb6c2202034b1be943e5fcf02e2e744a9"

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        data = response.json()
        zip_pop_df = pl.DataFrame(data[1:], schema=data[0])
        zip_pop_df = zip_pop_df.rename({"DP05_0001E": "total_population", "zip code tabulation area": "zip_code"})
        print(zip_pop_df.head())
        logger.info("Zip population data extracted successfully from API")
        return zip_pop_df
    except Exception as e:
        logger.error(f"Error in zip_pop_from_api: {e}")