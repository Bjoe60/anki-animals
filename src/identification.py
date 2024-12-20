import os
import pandas as pd
import re
from bs4 import BeautifulSoup


# Remove references like (1), (2), etc.
def remove_arkive_refs(text):
    if pd.isnull(text):
        return None
    return re.sub(r'\s?\(\d{1,2}\)', '', text)


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


# Gets identification information from each Wikipedia page
def get_identification():
    print('Getting identification information...')
    df_species = pd.read_csv(os.path.join('data', 'species.csv'), usecols=['eolID', 'wikipediaID', 'arkiveID'])
    
    df_arkive = pd.read_csv(os.path.join('data', 'arkive', 'media_resource.tab'), sep='\t', usecols=['taxonID', 'title', 'description'])
    df_arkive = df_arkive[df_arkive['title'] == 'Description']

    df_wikipedia = pd.read_csv(os.path.join('data', 'wikipedia', 'media_resource.tab'), sep='\t', usecols=['taxonID', 'CVterm', 'description'])
    df_wikipedia = df_wikipedia[df_wikipedia['CVterm'] == 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Description']

    # Merge into one dataframe
    df_merged = df_species.merge(df_arkive, left_on='arkiveID', right_on='taxonID', how='left')
    df_merged = df_merged.merge(df_wikipedia, left_on='wikipediaID', right_on='taxonID', how='left', suffixes=('_arkive', '_wikipedia'))
    
    # Clean up the descriptions
    df_merged['description_arkive'] = df_merged['description_arkive'].apply(remove_arkive_refs)
    df_merged['description_wikipedia'] = df_merged['description_wikipedia'].apply(extract_section)

    # Prefer Arkive description over Wikipedia
    df_merged['identification'] = df_merged['description_arkive']
    df_merged['identification'] = df_merged['identification'].fillna(df_merged['description_wikipedia'])

    df_merged = df_merged.reindex(columns=['eolID', 'identification'])
    df_merged.to_csv(os.path.join('data', 'species with identification.csv'), index=False)