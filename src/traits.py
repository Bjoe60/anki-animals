import pandas as pd
import os

WANTED_TERMS = ["conservation status"]

# Create a dictionary of URI terms to term names
def prepare_uri_to_term_dict(df_terms, terms):
    return {df_terms.loc[df_terms['name'] == term, 'uri'].values[0]: term for term in terms}

# Create a dictionary of (page_id, predicate) to value_uri for quick lookup
def prepare_traits_dict(df_traits, wanted_uris):
    traits_dict = {(row['page_id'], row['predicate']): row['value_uri'] for _, row in df_traits.iterrows() if row['predicate'] in wanted_uris}
    return traits_dict

# Create a dictionary to map URI values to their value names for fast access
def prepare_terms_dict(df_terms):
    return pd.Series(df_terms['name'].str.capitalize().values, index=df_terms['uri']).to_dict()

def get_traits():
    print("Getting traits...")
    df = pd.read_csv(os.path.join('data', 'species.csv'))
    df_traits = pd.read_csv(os.path.join('data', 'trait_bank', 'traits.csv'), dtype={'eol_pk': str, 'page_id': int, 'resource_pk': str, 'resource_id': object, 'source': str, 'scientific_name': str, 'predicate': str, 'object_page_id': object, 'value_uri': str, 'normal_measurement': object, 'normal_units_uri': str, 'normal_units': str, 'measurement': object, 'units_uri': str, 'units': str, 'literal': str, 'method': str, 'remarks': str, 'sample_size': object, 'name_en': str, 'citation': str})
    print(len(df_traits))

    df_terms = pd.read_csv(os.path.join('data', 'trait_bank', 'terms.csv'), dtype=str)

    print("Preprocessing...")
    wanted_uris_terms = prepare_uri_to_term_dict(df_terms, WANTED_TERMS)
    traits_dict = prepare_traits_dict(df_traits, wanted_uris_terms.keys())
    terms_dict = prepare_terms_dict(df_terms)

    # Make new column for each WANTED_TERMS in df
    for term in WANTED_TERMS:
        df[term] = None

    print("Processing traits...")

    # Populate each wanted term for each species using vectorized operations
    for idx, row in df.iterrows():
        for term_uri, term_name in wanted_uris_terms.items():
            value_uri = traits_dict.get((row['eolID'], term_uri))
            if value_uri:
                df.at[idx, term_name] = terms_dict.get(value_uri)
    
    # Save the modified DataFrame
    df.to_csv(os.path.join('data', 'species with traits.csv'), index=False)