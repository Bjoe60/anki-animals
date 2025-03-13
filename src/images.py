import pandas as pd
import os
import requests
from ratelimit import limits, sleep_and_retry
import re
from urllib.parse import quote
from tqdm import tqdm

INAT_QUERY_URL = 'https://api.inaturalist.org/v2/taxa/%s?fields=(preferred_common_name:!t,conservation_statuses:(place:!t,status:!t),extinct:!t,observations_count:!t,rank:!t,ancestors:(rank:!t,preferred_common_name:!t,name:!t),taxon_photos:(photo:(attribution:!t,license_code:!t,large_url:!t)))'
CONSERVATION_STATUSES = {'LC': 'Least Concern', 'NT': 'Near Threatened', 'VU': 'Vulnerable', 'EN': 'Endangered', 'CR': 'Critically Endangered', 'EW': 'Extinct in the Wild', 'EX': 'Extinct', 'DD': 'Data Deficient', 'NE': 'Not Evaluated', 'CD': 'Conservation Dependent'}
WANTED_RANKS = {'kingdom', 'class', 'order', 'family'}
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def escape_characters(text):
    return text.replace(';;', quote(';;')).replace('|', quote('|')).replace('\xa0', '&nbsp;')

# Maximum 30 requests per minute
@sleep_and_retry
@limits(calls=30, period=60)
def fetch_inaturalist_data(ids):
    query = INAT_QUERY_URL % ','.join(map(str, ids))
    response = requests.get(query, headers=HEADERS, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    data = response.json()
    
    return data['results']

# Generate images' HTML for Anki
def generate_images_html(photos):
    image_html_list = []
    for photo in photos:
        # Skip copyrighted images with "all rights reserved"
        if not photo["photo"]["license_code"]:
            continue

        if photo["photo"]["license_code"] in {'cc0', 'pd', 'gfdl'}:
            attribution = ''
        else:
            attribution = re.match(r'(?s).*?\(.\) (.*)(?:，|,|،|สงวนลิขสิทธิ์บางประการ).*?CC BY.*?', photo['photo']['attribution'])
            if not attribution:
                print(repr(photo['photo']['attribution']), photo['photo']['license_code'])
            attribution = f'{attribution.group(1).strip('\n')}' if attribution else photo['photo']['attribution']

        image_html_list.append(f'<img src="{photo["photo"]["large_url"]}">|{escape_characters(attribution)}|{escape_characters(photo["photo"]["license_code"])}')

    images_html = ';;'.join(image_html_list)
    return images_html

# Generate tag with common names for taxonomy
def generate_taxonomy(ancestors):
    taxonomy = []
    for ancestor in ancestors:
        if ancestor.get('rank') in WANTED_RANKS:
            # Use scientific name if common name is not available
            name = ancestor.get('preferred_common_name', ancestor.get('name')).title()
            if name == 'Fungi Including Lichens':
                name = 'Fungi'
            taxonomy.append(name)
    
    return '::'.join(taxonomy).replace(' ', '-')

# Finds the global conservation status (place: null)
def get_conservation_status(conservation_statuses):
    for status in conservation_statuses:
        if not status.get('place'):
            return status['status']
    return None

def process_results_to_dataframe(results):
    """Process iNaturalist API results into a structured dictionary for DataFrame updates."""
    records = []
    for result in results:
        if result.get('extinct') == True:
            continue
        
        images_html = generate_images_html(result.get('taxon_photos', []))
        taxonomy_tag = generate_taxonomy(result.get('ancestors', []))
        conservation_status = get_conservation_status(result.get('conservation_statuses', []))
        conservation_status = CONSERVATION_STATUSES.get(conservation_status, '')

        records.append({
            'inaturalistID': result.get('id'),
            'images': images_html,
            'conservation_status': conservation_status,
            'observations_count': result.get('observations_count'),
            'preferred_common_name': result.get('preferred_common_name', ''),
            'taxonomy_tag': taxonomy_tag,
            'rank': result.get('rank', '')
        })
    results_df = pd.DataFrame(records)

    return results_df

# Gets images, conservation status, observation count, English name and taxonomy name from iNaturalist
def get_images(deck):
    print("Getting images...")
    df = pd.read_csv(os.path.join('data', 'processed', f'{deck.value['type']} species.csv'), usecols=['eolID', 'inaturalistID'], dtype={'inaturalistID': int, 'gbifID': int})

    # Get list of ids from iNaturalist in integer format
    ids = df['inaturalistID'].unique()

    # Extract 30 ids at a time and process them in one request
    batch_size = 30
    all_results = []
    with tqdm(total=len(ids), desc="Processing ids") as pbar: # Make a progress bar
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            all_results.extend(fetch_inaturalist_data(batch_ids))
            pbar.update(len(batch_ids))

    results_df = process_results_to_dataframe(all_results)
    # Convert observations_count to object to allow NaNs
    results_df['observations_count'] = results_df['observations_count'].astype('Int64')
    df_images = df.merge(results_df, on='inaturalistID', how='inner', suffixes=('', '_new'))
    df_images.drop(columns=['inaturalistID'], inplace=True)

    df_images.to_csv(os.path.join('data', 'processed', f'{deck.value['type']} species with images.csv'), index=False)