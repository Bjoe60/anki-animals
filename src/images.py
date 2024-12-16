import pandas as pd
import os
import requests
from ratelimit import limits, sleep_and_retry
import re

SAMPLE_TEST = True
INAT_QUERY_URL = 'https://api.inaturalist.org/v2/taxa/%s?fields=(preferred_common_name:!t,conservation_statuses:(place:!t,status:!t),extinct:!t,observations_count:!t,wikipedia_summary:!t,taxon_photos:(photo:(attribution:!t,license_code:!t,large_url:!t)))'
CONSERVATION_STATUSES = {'LC': 'Least Concern', 'NT': 'Near Threatened', 'VU': 'Vulnerable', 'EN': 'Endangered', 'CR': 'Critically Endangered', 'EW': 'Extinct in the Wild', 'EX': 'Extinct', 'DD': 'Data Deficient', 'NE': 'Not Evaluated', 'CD': 'Conservation Dependent'}

# Maximum 60 requests per minute
@sleep_and_retry
@limits(calls=60, period=60)
def fetch_inaturalist_data(ids):
    query = INAT_QUERY_URL % ids
    response = requests.get(query)
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    data = response.json()
    
    return data['results']

# Generate images' HTML for Anki
def generate_images_html(photos):
    image_html_list = []
    for photo in photos:
        # Only include images without all rights reserved
        if photo["photo"]["license_code"]:
            attribution = re.match(r'.*\(c\) (.+), some rights reserved.*', photo['photo']['attribution'])
            attribution = f'{attribution.group(1)}' if attribution else '' # If no attribution, it is in the public domain
            image_html_list.append(f'<img src="{photo["photo"]["large_url"]}">|{attribution}|{photo["photo"]["license_code"]}')
    images_html = ';;'.join(image_html_list)
    images_html = images_html.replace("'", '&#39;') # Avoid issues in Anki
    return images_html

# Finds the global conservation status (place: null)
def get_conservation_status(conservation_statuses):
    for status in conservation_statuses:
        if not status.get('place'):
            return status['status']
    return None

def process_results_to_dataframe(results, original_df):
    """Process iNaturalist API results into a structured dictionary for DataFrame updates."""
    records = []
    for result in results:
        if result.get('extinct') == True:
            continue
        
        images_html = generate_images_html(result.get('taxon_photos', []))
        conservation_status = get_conservation_status(result.get('conservation_statuses', []))
        conservation_status = CONSERVATION_STATUSES[conservation_status]

        records.append({
            'inaturalistID': result.get('id'),
            'images': images_html,
            'conservation_status': conservation_status,
            'observations_count': result.get('observations_count'),
            'wikipedia_summary': result.get('wikipedia_summary'),
            'preferred_common_name': result.get('preferred_common_name', '')
        })
    results_df = pd.DataFrame(records)

    return results_df


def get_images():
    print("Getting images...")
    df = pd.read_csv(os.path.join('data', 'species.csv'), dtype={'inaturalistID': int, 'gbifID': int})

    # Get list of ids from iNaturalist in integer format
    ids = df['inaturalistID'].unique()
    if SAMPLE_TEST:
        ids = ids[:30]

    # Extract the first 30 ids and make them into a string
    batch_size = 30
    all_results = []
    for i in range(0, len(ids), batch_size):
        if i % (batch_size * 60) == 0:
            print(f"Processing {i+1} of {len(ids)}")
        batch_ids = ','.join(map(str, ids[i:i + batch_size]))
        all_results.extend(fetch_inaturalist_data(batch_ids))

    results_df = process_results_to_dataframe(all_results, df)
    # Convert observations_count to object to allow NaNs
    results_df['observations_count'] = results_df['observations_count'].astype('Int64')
    df_images = df.merge(results_df, on='inaturalistID', how='left', suffixes=('', '_new'))

    df_images.to_csv(os.path.join('data', 'species with images.csv'), index=False)