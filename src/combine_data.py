import pandas as pd
import os
from functools import reduce
from string import capwords
from species import DECK_NAME

UNWANTED_IMGS = {'<img src="https://www.inaturalist.org/assets/copyright-infringement-large.png">'}
COLUMNS = ['Scientific', 'EOL ID', 'iNaturalist ID', 'GBIF ID', 'Conservation status', 'Observations', 'Taxonomic sort', 'Observations sort', 'Identification', 'Images', 'Tags', 'English', 'Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Azerbaijani', 'Belarusian', 'Bengali', 'Bulgarian', 'Catalan', 'Chinese', 'Croatian', 'Czech', 'Danish', 'Dutch', 'Estonian', 'Finnish', 'French', 'Galician', 'Georgian', 'German', 'Greek', 'Hebrew', 'Hungarian', 'Icelandic', 'Indonesian', 'Italian', 'Japanese', 'Kazakh', 'Korean', 'Latvian', 'Lithuanian', 'Macedonian', 'Malay', 'Maltese', 'Mongolian', 'Nepali', 'Norwegian', 'Persian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Serbian', 'Slovak', 'Slovenian', 'Spanish', 'Swahili', 'Swedish', 'Thai', 'Turkish', 'Ukrainian', 'Uzbek', 'Vietnamese']

# Create sortable string of numbers with leading zeros using current order
def create_sort_string(df, name):
    df[name] = df.reset_index(drop=True).index.map(lambda i: f"{i:06d}")


def create_csv(df):
    with open(os.path.join('data', f'{DECK_NAME}.csv'), 'w', encoding='utf-8', newline='') as f:
        # File header for Anki
        f.write(f'#separator:Comma\n#html:true\n#notetype:Species\n#deck:{DECK_NAME}\n#tags column:{COLUMNS.index("Tags") + 1}\n#columns:{",".join(COLUMNS)}\n')
        
        df.to_csv(f, index=False, header=False)


def remove_unwanted_imgs(df):
    df['images'] = df['images'].apply(lambda x: ';;'.join(
            [img for img in x.split(';;') if img.split('|')[0] not in UNWANTED_IMGS]
        ) if isinstance(x, str) else x)


def combine_data():
    print("Combining data...")
    all_dfs = [pd.read_csv(os.path.join('data', file), low_memory=False) for file in ['species.csv', 'species with identification.csv', 'species with translations.csv', 'species with countries.csv', 'species with images.csv']]

    # Merge dataframes into one
    df = reduce(lambda left, right: pd.merge(left, right, on='eolID', how='left'), all_dfs)
    
    remove_unwanted_imgs(df)

    # Prefer the English names from iNaturalist
    df['English'] = df['preferred_common_name'].combine_first(df['English'])
    df['English'] = df['English'].fillna('').apply(capwords)

    # Remove empty cards
    print(f"Removing {df['images'].isnull().sum()} species with no images")
    df.dropna(subset=['images'], inplace=True)

    # Create tags
    df['countries'] = df['countries'].fillna('')
    df['taxonomy_tag'] = df['countries'] + ' ' + df['taxonomy_tag']

    # Create strings to sort by in Anki
    df['observations_count'] = df['observations_count'].astype('Int64')
    create_sort_string(df, 'Taxonomic sort')
    
    df.sort_values(by=['observations_count', 'Taxonomic sort'], ascending=[False, True], inplace=True)
    create_sort_string(df, 'Observations sort')
    
    df.sort_values(by='Taxonomic sort', inplace=True)

    # Rename and reorder columns
    df.rename(columns={'canonicalName': 'Scientific', 'eolID': 'EOL ID', 'inaturalistID': 'iNaturalist ID', 'gbifID': 'GBIF ID', 'identification': 'Identification', 'conservation_status': 'Conservation status', 'images': 'Images', 'observations_count': 'Observations', 'taxonomy_tag': 'Tags'}, inplace=True)
    df = df.reindex(columns=COLUMNS)
    

    create_csv(df)
    print("Done.")