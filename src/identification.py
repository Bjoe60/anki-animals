import os
import pandas as pd
from bs4 import BeautifulSoup

def print_all_headers(soup):
    headers = soup.find_all(['h2', 'span'])
    for header in headers:
        if header.get('id'):
            print(repr(header.get('id')), end=', ')

def remove_refs(soup):
    for sup_tag in soup.find_all('sup'):
        if sup_tag.get('id', '').startswith('cite_ref'):
            sup_tag.decompose()
    return str(soup)

def find_description_header(soup):
    headers = soup.find_all(['h2', 'span'])
    for keyword in ['description', 'morphology', 'appearance', 'characteristics', 'identification', 'anatomy']:
        for header in headers:
            if keyword in header.get('id', '').lower():
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
        if sibling.find('img'): # Skip images
            continue
        
        # Stop at the next header or when text is long enough
        if sibling.find(['h2', 'h3']) and descriptions or is_longer_than(descriptions, 2200):
            break
        
        without_refs = remove_refs(sibling)
        descriptions.append(without_refs)

    return "".join(descriptions)


# Gets identification information from each Wikipedia page
def get_identification():
    print('Getting identification information...')
    df_species = pd.read_csv(os.path.join('data', 'species.csv'), usecols=['eolID', 'WikipediaID'])
    df = pd.read_csv(os.path.join('data', 'wikipedia_text', 'media_resource.tab'), sep='\t', usecols=['taxonID', 'CVterm', 'description'])

    # Use rows with full Wikipedia text
    df = df[df['CVterm'] == 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Description']
    
    df = df_species.merge(df, left_on='WikipediaID', right_on='taxonID', how='left')

    df['identification'] = df['description'].apply(extract_section)

    df = df.reindex(columns=['eolID', 'identification'])
    df.to_csv(os.path.join('data', 'species with identification.csv'), index=False)