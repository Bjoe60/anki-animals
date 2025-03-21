import pandas as pd
import os

BIRD_TAXA = 'Life|Cellular Organisms|Eukaryota|Opisthokonta|Metazoa|Bilateria|Deuterostomia|Chordata|Vertebrata|Gnathostomata|Osteichthyes|Sarcopterygii|Tetrapoda|Amniota|Reptilia|Diapsida|Archosauromorpha|Archosauria|Dinosauria|Saurischia|Theropoda|Tetanurae|Coelurosauria|Maniraptoriformes|Maniraptora|Aves'

# Gets a list of mammals with scientific names and resource IDs
def get_taxa(deck):
	print("Getting taxa...")
	df = pd.read_csv(os.path.join('data', 'input', 'taxon.tab'), sep='\t', usecols=['eolID', 'canonicalName', 'higherClassification', 'taxonRank'], dtype={'eolID': object, 'taxonRank': str, 'canonicalName': str, 'higherClassification': str})
	df = df.dropna(subset=['higherClassification'])
	df = df[df['higherClassification'].str.startswith(deck.value['taxa'])]
	# Exclude birds as they have their own separate deck (only relevant for animals)
	df = df[~df['higherClassification'].str.startswith(BIRD_TAXA)]
	df = df[df['taxonRank'].isin(deck.value['taxon_rank'])]
	df = df.drop(columns=['higherClassification', 'taxonRank'])

	print(len(df), 'taxa')

	# Get iNaturalist IDs
	df_ids = pd.read_csv(os.path.join('data', 'input', 'full_provider_ids.csv'), usecols=['resource_pk', 'resource_id', 'page_id'], dtype={'resource_pk': str, 'resource_id': int, 'page_id': object})

	# Add an ID column to the dataframe
	def merge_provider_ids(df, resource_id, id_column, how='left'):
		df_provider = df_ids[df_ids['resource_id'] == resource_id]
		df_provider = df_provider.drop_duplicates(subset=['page_id'], keep='last')
		df = df.merge(df_provider, left_on='eolID', right_on='page_id', how=how)
		df.drop(columns=['resource_id', 'page_id'], inplace=True)
		df.rename(columns={'resource_pk': id_column}, inplace=True)
		return df

	# Get IDs to different resources
	df = merge_provider_ids(df, 1177, 'inaturalistID', 'inner')
	df = merge_provider_ids(df, 1178, 'gbifID', 'inner')
	df = merge_provider_ids(df, 617, 'wikipediaID')
	df = merge_provider_ids(df, 775, 'arkiveID')
	df = merge_provider_ids(df, 560, 'adwID')
	df = merge_provider_ids(df, 395, 'fishbaseID')
	df = merge_provider_ids(df, 564, 'amphibiawebID')

	print(len(df), 'taxa with IDs')

	df.to_csv(os.path.join('data', 'processed', f'{deck.value['type']} species.csv'), index=False)