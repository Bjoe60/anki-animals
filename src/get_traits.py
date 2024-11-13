import pandas as pd
import os

WANTED_TERMS = ["extinction status"]

# Create dictionary of URIs to terms
def terms_to_uris(df_terms, terms):
    return {df_terms[df_terms['name'] == term]['uri'].values[0]: term for term in terms}

# Find the value for the species
def measurement_to_value(df_traits, eolID, uri):
    row = df_traits[df_traits['predicate'] == uri]
    if row['value_uri'].values[0]:
        return row['value_uri'].values[0]
    
    print("No value_uri found for", uri)
    return None

def uri_to_term(uri_to_term_dict, df_terms, uri):
    if uri in uri_to_term_dict:
        return uri_to_term_dict[uri]
    value = df_terms[df_terms['uri'] == uri]['name'].values[0].capitalize()
    uri_to_term_dict[uri] = value
    return value

# Fills out traits for the species
def get_traits():
    df = pd.read_csv(os.path.join('data', 'species with translations.csv'))
    df_traits = pd.read_csv(os.path.join('data', 'trait_bank', 'traits.csv'), dtype={'eol_pk': str, 'page_id': int, 'resource_pk': str, 'resource_id': object, 'source': str, 'scientific_name': str, 'predicate': str, 'object_page_id': object, 'value_uri': str, 'normal_measurement': float, 'normal_units_uri': str, 'normal_units': str, 'measurement': float, 'units_uri': str, 'units': str, 'literal': str, 'method': str, 'remarks': str, 'sample_size': object, 'name_en': str, 'citation': str})
    df_terms = pd.read_csv(os.path.join('data', 'trait_bank', 'terms.csv'), dtype=str)
    print("Data loaded")

    # Create empty columns for the wanted terms
    for term in WANTED_TERMS:
        df[term] = None
    
    wanted_terms_uris = terms_to_uris(df_terms, WANTED_TERMS)
    uri_to_term_dict = dict()

    # Fill out the trait columns for every species
    for idx in df.index[:20]:
        for term_uri in wanted_terms_uris:
            value_uri = measurement_to_value(df_traits, df.loc[idx, 'eolID'], term_uri)
            value = uri_to_term(uri_to_term_dict, df_terms, value_uri)
            df.loc[idx, wanted_terms_uris[term_uri]] = value

    df.to_csv(os.path.join('data', 'species with traits.csv'), index=False)

get_traits()