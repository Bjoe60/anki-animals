import pandas as pd
import os

# Gets a list of mammals with scientific names and EOL IDs
def get_species():
	print("Getting species...")
	df = pd.read_csv(os.path.join('data', 'taxon.tab'), sep='\t', dtype={'eolID': object, 'taxonID': str, 'acceptedNameUsageID': str, 'parentNameUsageID': str, 'datasetID': str, 'Landmark': object, 'source': str, 'furtherInformationURL': str, 'scientificName': str, 'taxonRank': str, 'taxonomicStatus': str, 'canonicalName': str, 'authority': str, 'higherClassification': str})
	df = df.dropna(subset=['higherClassification'])
	df = df[df['higherClassification'].str.startswith('Life|Cellular Organisms|Eukaryota|Opisthokonta|Metazoa|Bilateria|Deuterostomia|Chordata|Vertebrata|Gnathostomata|Osteichthyes|Sarcopterygii|Tetrapoda|Amniota|Synapsida|Therapsida|Cynodontia|Mammalia')]
	df = df[df['taxonRank'].values == 'species']
	df = df.reindex(columns=['eolID', 'canonicalName', 'higherClassification'])

	print(len(df))

	# Get iNaturalist IDs
	df_ids = pd.read_csv(os.path.join('data', 'full_provider_ids.csv'), dtype={'node_id': int, 'resource_pk': str, 'resource_id': int, 'page_id': object, 'preferred_canonical_for_page': str})
	df_inaturalist = df_ids[df_ids['resource_id'] == 1177]
	df = df.merge(df_inaturalist, left_on='eolID', right_on='page_id', how='left')
	df.drop(columns=['node_id', 'resource_id', 'page_id', 'preferred_canonical_for_page'], inplace=True)
	df.rename(columns={'resource_pk': 'inaturalistID'}, inplace=True)
	df.dropna(subset=['inaturalistID'], inplace=True)

	# Get GBIF IDs
	df_gbif = df_ids[df_ids['resource_id'] == 1178]
	df = df.merge(df_gbif, left_on='eolID', right_on='page_id', how='left')
	df.drop(columns=['node_id', 'resource_id', 'page_id', 'preferred_canonical_for_page'], inplace=True)
	df.rename(columns={'resource_pk': 'gbifID'}, inplace=True)
	df.dropna(subset=['gbifID'], inplace=True)

	df.to_csv(os.path.join('data', 'species.csv'), index=False)