import pandas as pd
import os
from unidecode import unidecode

# Gets only translations marked as "preferred"
def get_preferred_only(df_translations):
    df_translations = df_translations.dropna(subset=['is_preferred_by_eol'])

    preferred_groups = df_translations[df_translations['is_preferred_by_resource'] == 'preferred'][['page_id', 'language_code']]

    # Merge the original translations with the preferred groups, marking rows that belong to these groups
    df_translations = df_translations.merge(
        preferred_groups.drop_duplicates(), 
        on=['page_id', 'language_code'], 
        how='left', 
        indicator='preferred_exists'
    )

    # Keep only preferred rows if a preferred resource exists in the group; otherwise, keep all
    df_translations = df_translations[
        (df_translations['preferred_exists'] == 'both') & (df_translations['is_preferred_by_resource'] == 'preferred') |
        (df_translations['preferred_exists'] == 'left_only')
    ]
    return df_translations


# Merges multiple translations into a single cell
def merge_translations(df_translations):
    df_translations['vernacular_string'] = df_translations['vernacular_string'].str.title().fillna('')
    
    # Remove duplicates written in almost same way
    df_translations['vernacular_string_lower'] = df_translations['vernacular_string'].str.replace(' ', '').str.replace('-', '').str.replace("’", "'").apply(unidecode)
    df_translations = df_translations.drop_duplicates(subset=['page_id', 'language_code', 'vernacular_string_lower'])

    # Combine the rest of multiple translations into a single cell
    df_translations = df_translations.groupby(['page_id', 'language_code'], as_index=False).agg({
        'vernacular_string': ' / '.join
    })
    return df_translations


# Gets the English translations for the species
def get_translations():
    df = pd.read_csv(os.path.join('data', 'species.csv'))
    df_translations = pd.read_csv(os.path.join('data', 'vernacularnames.csv'), dtype={'page_id': int, 'canonical_form': str, 'vernacular_string': str, 'language_code': str, 'resource_name': str, 'is_preferred_by_resource': str, 'is_preferred_by_eol': str})
    
    df_translations = df_translations[df_translations['language_code'] == 'eng']
    df_translations = get_preferred_only(df_translations)
    df_translations = merge_translations(df_translations)

    df = df.merge(df_translations, left_on='eolID', right_on='page_id', how='left')
    df = df.drop(columns=['page_id'])
    
    df.to_csv(os.path.join('data', 'species with translations.csv'), index=False)