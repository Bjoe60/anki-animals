import os
import pandas as pd
import re
from bs4 import BeautifulSoup

ADW_URL = 'https://animaldiversity.org/accounts/%s/'
WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/%s'

# Remove references like (1), (2), etc.
def remove_arkive_refs(text):
    return re.sub(r'\s?\(\d{1,2}\)', '', text) if not pd.isnull(text) else None

def wrap_in_p_tag(text):
    return f"<p>{text}</p>" if not pd.isnull(text) else None

def remove_traits(text):
    if pd.isnull(text):
        return None
    soup = BeautifulSoup(text, 'html.parser')
    for p in soup.find_all('p'):
        if p.find('strong'):
            p.decompose()
    return str(soup)

def remove_adw_refs(text):
    return re.sub(r'\s?\(.+?,\s\d{4}\)', '', text) if not pd.isnull(text) else None

# Remove references like [1], [2], etc.
def remove_wiki_refs(soup):
    for sup_tag in soup.find_all('sup'):
        if sup_tag.get('id', '').startswith('cite_ref'):
            sup_tag.decompose()
    return str(soup)

# Locate the header for the "Description" section
def find_description_header(soup):
    headers = soup.find_all(['h2', 'span'])
    keywords = ['description', 'morphology', 'appearance', 'characteristics', 'identification', 'anatomy']
    for header in headers:
        if any(keyword in header.get('id', '').lower() for keyword in keywords):
            return header
    return None

def is_longer_than(descriptions, length):
    return sum(len(desc) for desc in descriptions) > length

# Extract the "Description" section from the Wikipedia text
def extract_section(html):
    soup = BeautifulSoup(str(html), 'html.parser')
    description_header = find_description_header(soup)

    if not description_header:
        return None

    descriptions = []

    # Iterate through siblings of the h2 tag until another h2 or h3 is found
    for sibling in description_header.parent.find_next_siblings():
        # Skip unwanted tags
        if any(sibling.find(tag) for tag in ['img', 'video', 'audio', 'table']):
            continue

        # Stop at the next header or when text is long enough
        if sibling.name in {'h2', 'h3'} or sibling.find(['h2', 'h3']) and descriptions or is_longer_than(descriptions, 2200):
            break
        
        descriptions.append(remove_wiki_refs(sibling))

    return "".join(descriptions)

# Add source to the last paragraph of the text
def add_source(text, source):
    if not text:
        return None
    soup = BeautifulSoup(text, 'html.parser')
    last_p = soup.find_all('p')[-1]
    last_p.append(BeautifulSoup(f' ({source})', 'html.parser'))
    return str(soup)

# Gets identification information from each Wikipedia page
def get_identification():
    print('Getting identification information...')
    df_species = pd.read_csv(os.path.join('data', 'species.csv'), usecols=['eolID', 'wikipediaID', 'arkiveID', 'adwID'])
    
    df_arkive = pd.read_csv(os.path.join('data', 'arkive', 'media_resource.tab'), sep='\t', usecols=['taxonID', 'title', 'description'])
    df_arkive = df_arkive[df_arkive['title'] == 'Description']

    df_adw = pd.read_csv(os.path.join('data', 'animal_diversity_web', 'media_resource.tab'), sep='\t', usecols=['taxonID', 'CVterm', 'description'])
    df_adw = df_adw[df_adw['CVterm'] == 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Morphology']

    df_wikipedia = pd.read_csv(os.path.join('data', '81', 'media_resource.tab'), sep='\t', usecols=['taxonID', 'CVterm', 'description'])
    df_wikipedia = df_wikipedia[df_wikipedia['CVterm'] == 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Description']

    # Merge into one dataframe
    df_merged = df_species.merge(df_arkive, left_on='arkiveID', right_on='taxonID', how='left')
    df_merged = df_merged.merge(df_adw, left_on='adwID', right_on='taxonID', how='left', suffixes=('_arkive', ''))
    df_merged = df_merged.merge(df_wikipedia, left_on='wikipediaID', right_on='taxonID', how='left', suffixes=('_adw', '_wikipedia'))

    # Clean up the descriptions
    df_merged['description_arkive'] = df_merged['description_arkive'].apply(remove_arkive_refs).apply(wrap_in_p_tag)
    df_merged['description_adw'] = df_merged['description_adw'].apply(remove_traits).apply(remove_adw_refs)
    df_merged['description_wikipedia'] = df_merged['description_wikipedia'].apply(extract_section)

    # Add source
    df_merged['description_arkive'] = df_merged['description_arkive'].apply(lambda desc: add_source(desc, "Arkive"))

    adw_urls = df_merged['adwID'].apply(lambda adw_id: f'<a href="{ADW_URL % adw_id}">Animal Diversity Web</a>')
    df_merged['description_adw'] = df_merged['description_adw'].combine(adw_urls, add_source)

    wikipedia_urls = df_merged['adwID'].apply(lambda adw_id: f'<a href="{ADW_URL % adw_id}">Wikipedia</a>')
    df_merged['description_wikipedia'] = df_merged['description_wikipedia'].combine(wikipedia_urls, add_source)

    # Prefer Arkive description over ADW over Wikipedia
    df_merged['identification'] = df_merged['description_arkive'].replace('', pd.NA).fillna(df_merged['description_adw']).fillna(df_merged['description_wikipedia'])

    print(f"Species with identification info: {df_merged['identification'].count()} / {len(df_merged)}")

    df_merged = df_merged.reindex(columns=['eolID', 'identification'])
    df_merged.to_csv(os.path.join('data', 'species with identification.csv'), index=False)