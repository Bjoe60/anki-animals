import pandas as pd
import os
import requests

INAT_QUERY_URL = 'https://api.inaturalist.org/v2/taxa/%s?fields=(preferred_common_name:!t,extinct:!t,observations_count:!t,wikipedia_url:!t,wikipedia_summary:!t,taxon_photos:(photo:(attribution:!t,license_code:!t,large_url:!t)))'

def fetch_inaturalist_data(ids):
	query = INAT_QUERY_URL % ids
	response = requests.get(query)
	
	if response.status_code != 200:
		raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
	
	data = response.json()
	if 'results' not in data:
		raise Exception(f"Unexpected API response format: {data}")
	
	return data['results']

def process_results_to_dataframe(results):
	"""Process iNaturalist API results into a structured dictionary for DataFrame updates."""
	records = []
	for result in results:
		images_html = ';;'.join(
			f'<img src="{photo["photo"]["large_url"]}">|{photo["photo"]["attribution"]}|{photo["photo"]["license_code"]}'
			for photo in result['taxon_photos']
		)
		records.append({
			'inaturalistID': result['id'],
			'images': images_html,
			'extinct': result['extinct'],
			'observations_count': result['observations_count'],
			'wikipedia_url': result.get('wikipedia_url'),
			'wikipedia_summary': result.get('wikipedia_summary'),
		})
	return pd.DataFrame(records)


def get_images():
	df = pd.read_csv(os.path.join('data', 'species with translations.csv'), dtype={'eolID': int, 'canonicalName': str, 'higherClassification': str, 'inaturalistID': int, 'language_code': str, 'vernacular_string': str})
	df.reindex(columns=['eolID', 'canonicalName', 'higherClassification', 'inaturalistID', 'language_code', 'vernacular_string', 'images', 'extinct', 'observations_count', 'wikipedia_url', 'wikipedia_summary'])

	# Get list of ids from iNaturalist
	ids = df['inaturalistID'].unique()
	# Extract the first 30 ids and make them into a string
	batch_size = 30
	all_results = []
	for i in range(0, len(ids), batch_size):
		batch_ids = ','.join(map(str, ids[i:i + batch_size]))
		all_results.extend(fetch_inaturalist_data(batch_ids))

	results_df = process_results_to_dataframe(all_results)
	df_images = df.merge(results_df, on='inaturalistID', how='left')

	df_images.to_csv(os.path.join('data', 'species with translations and images.csv'), index=False)

get_images()