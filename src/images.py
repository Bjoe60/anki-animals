import pandas as pd
import os
import requests
from ratelimit import limits, sleep_and_retry

INAT_QUERY_URL = 'https://api.inaturalist.org/v2/taxa/%s?fields=(preferred_common_name:!t,extinct:!t,observations_count:!t,wikipedia_url:!t,wikipedia_summary:!t,taxon_photos:(photo:(attribution:!t,license_code:!t,large_url:!t)))'

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

def process_results_to_dataframe(results, original_df):
    """Process iNaturalist API results into a structured dictionary for DataFrame updates."""
    records = []
    for result in results:
        if result['extinct'] == True:
            print(f"Skipping extinct species: {result['id'], result['preferred_common_name']}")
            continue
        images_html = ';;'.join(
            f'<img src="{photo["photo"]["large_url"]}">|{photo["photo"]["attribution"]}|{photo["photo"]["license_code"]}'
            for photo in result['taxon_photos']
        )
        images_html = images_html.replace("'", '`') # Avoid issues in Anki
        records.append({
            'inaturalistID': result['id'],
            'images': images_html,
            'extinct': result['extinct'],
            'observations_count': result['observations_count'],
            'wikipedia_url': result.get('wikipedia_url'),
            'wikipedia_summary': result.get('wikipedia_summary'),
            'preferred_common_name': result.get('preferred_common_name', '')
        })
    results_df = pd.DataFrame(records)

    return results_df

def get_images():
    print("Getting images...")
    df = pd.read_csv(os.path.join('data', 'species.csv'), dtype={'inaturalistID': int, 'gbifID': int})

    # Get list of ids from iNaturalist in integer format
    ids = df['inaturalistID'].unique()[:30]

    # Extract the first 30 ids and make them into a string
    batch_size = 30
    all_results = []
    for i in range(0, len(ids), batch_size):
        batch_ids = ','.join(map(str, ids[i:i + batch_size]))
        all_results.extend(fetch_inaturalist_data(batch_ids))

    results_df = process_results_to_dataframe(all_results, df)
    # Convert observations_count to object to allow NaNs
    results_df['observations_count'] = results_df['observations_count'].astype('Int64')
    df_images = df.merge(results_df, on='inaturalistID', how='left', suffixes=('', '_new'))

    df_images.to_csv(os.path.join('data', 'species with images.csv'), index=False)