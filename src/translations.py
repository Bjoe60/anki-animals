import pandas as pd
import os
from unidecode import unidecode
from string import capwords

LANGUAGES = [
    ('English', ['eng']),
    ('Arabic', ['ara']),
    ('Azerbaijani', ['aze']),
    ('Bulgarian', ['bul']),
    ('Catalan', ['cat']),
    ('Croatian', ['hrv']),
    ('Czech', ['cze']),
    ('Danish', ['dan']),
    ('Dutch', ['dut']),
    ('Estonian', ['est']),
    ('Finnish', ['fin']),
    ('French', ['fre']),
    ('German', ['ger']),
    ('Hebrew', ['heb']),
    ('Hungarian', ['hun']),
    ('Indonesian', ['ind']),
    ('Italian', ['ita']),
    ('Japanese', ['jpn']),
    ('Lithuanian', ['lit']),
    ('Malay', ['may']),
    ('Norwegian', ['nor', 'nob']),
    ('Persian', ['per']),
    ('Polish', ['pol']),
    ('Portuguese', ['por']),
    ('Russian', ['rus']),
    ('Serbian', ['srp']),
    ('Slovak', ['slo']),
    ('Spanish', ['spa', 'sp']),
    ('Swedish', ['swe']),
    ('Thai', ['tha']),
    ('Turkish', ['tur']),
    ('Ukrainian', ['ukr']),
    ('Vietnamese', ['vie']),
]

# Get only translations marked as "preferred"
def get_preferred_only(df_translations):
    df_translations = df_translations.dropna(subset=['is_preferred_by_eol'])
    df_translations = df_translations.drop_duplicates(subset=['page_id', 'is_preferred_by_eol'])

    preferred_groups = df_translations[df_translations['is_preferred_by_resource'] == 'preferred']['page_id']
    preferred_groups = preferred_groups.drop_duplicates()

    # Merge the original translations with the preferred groups, marking rows that belong to these groups
    df_translations = df_translations.merge(preferred_groups, on='page_id', how='left', indicator='preferred_exists')

    # Keep only preferred rows if they are preferred by resource too, otherwise, keep all
    df_translations = df_translations[(df_translations['preferred_exists'] == 'both') & (df_translations['is_preferred_by_resource'] == 'preferred') | (df_translations['preferred_exists'] == 'left_only')]
    return df_translations


# Merges multiple translations into a single cell
def merge_translations(df_translations):
    # Capitalize the first letter of each word
    df_translations['vernacular_string'] = df_translations['vernacular_string'].fillna('').apply(capwords)
    
    # Remove duplicates written in almost same way
    df_translations['vernacular_string_lower'] = df_translations['vernacular_string'].str.replace(' ', '').str.replace('-', '').str.replace("’", "'").str.lower().str.replace('common ', '').apply(unidecode)
    df_translations = df_translations.drop_duplicates(subset=['page_id', 'language_code', 'vernacular_string_lower'])

    # Combine the rest of multiple translations into a single cell
    df_translations = df_translations.groupby(['page_id', 'language_code'], as_index=False).agg({
        'vernacular_string': ' / '.join
    })
    return df_translations


# Gets the English translations for the species
def get_translations():
    print("Getting translations...")
    df = pd.read_csv(os.path.join('data', 'species.csv'), usecols=['eolID'])
    df_translations = pd.read_csv(os.path.join('data', 'vernacularnames.csv'), dtype={'page_id': int, 'canonical_form': str, 'vernacular_string': str, 'language_code': str, 'resource_name': str, 'is_preferred_by_resource': str, 'is_preferred_by_eol': str})

    # Fill out translations for additional languages
    for language, codes in LANGUAGES:
        df_translations_lang = df_translations[df_translations['language_code'].isin(codes)]
        df_translations_lang = get_preferred_only(df_translations_lang)
        df_translations_lang = merge_translations(df_translations_lang)
        
        # Merge and rename the vernacular_string column to the language name
        df = df.merge(df_translations_lang[['page_id', 'vernacular_string']], left_on='eolID', right_on='page_id', how='left')
        df.rename(columns={f'vernacular_string': language}, inplace=True)
        df.drop(columns=['page_id'], inplace=True)

    # Save the updated DataFrame to a file
    df.to_csv(os.path.join('data', 'species with translations.csv'), index=False)

def print_number_of_translations():
    df = pd.read_csv(os.path.join('data', 'species with translations.csv'))
    for language, _ in LANGUAGES:
        if df[language].count() < 600:
            print(f"Species with {language} translation: {df[language].count()} / {len(df)}")