import pandas as pd
import os

def get_images():
	df = pd.read_csv(os.path.join('data', 'species with translations.csv'))
	# Combine all csv files in "media" folder into a single DataFrame, but only the first file has a header
	df_images = pd.concat(
		[
			pd.read_csv(
				os.path.join('data', 'media_manifest', file),
				header=0 if file == 'media_manifest_2.csv' else None,  # Use header only for the first file
				names=[0, 1, 2, 3, 4, 5] if file != 'media_manifest_2.csv' else None,
				dtype={0: int, 1: int, 2: str, 3: str, 4: str, 5: str}
			)
			for file in os.listdir(os.path.join('data', 'media_manifest')) if file.startswith('media_manifest')
		],
		ignore_index=True
	)
	print(len(df_images), 'images loaded')
	
	df_images['images'] = df_images.iloc[:, 3].fillna('') + "|" + df_images.iloc[:, 4].fillna('') + "|" + df_images.iloc[:, 5].fillna('')
	
	grouped = df_images.groupby(df_images.iloc[:, 1])['images'].apply(lambda x: ';;'.join(x.head(10))).reset_index()

	# Merge the grouped data back into the main dataframe
	df = df.merge(grouped, left_on=df.columns[0], right_on=grouped.columns[0], how='left')

	all_rows = len(df)
	df = df.dropna(subset=['images'])
	print(all_rows, 'to', len(df))
	df.to_csv(os.path.join('data', 'species with translations and images.csv'), index=False)