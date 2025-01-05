import os
import pandas as pd
import re
from bs4 import BeautifulSoup

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

def remove_adw_amphibia_refs(text):
    return re.sub(r'\s?\(.+?\d{4}\)', '', text) if not pd.isnull(text) else None

def remove_fishbase_refs(text):
    return re.sub(r'\s?\(Ref\..*?\)', '', text) if not pd.isnull(text) else None

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
def extract_wiki_section(html):
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

def extract_first_paragraphs(html):
    soup = BeautifulSoup(str(html), 'html.parser')
    paragraphs = []
    for paragraph in soup.find_all('p'):
        if paragraph.find(['img', 'audio', 'a', 'iframe']):
            continue
        paragraphs.append(str(paragraph))
        if is_longer_than(paragraphs, 2200):
            break
    
    return "".join(paragraphs)

# Add source to the last paragraph of the text
def add_source(text, source):
    if not text:
        return None
    soup = BeautifulSoup(text, 'html.parser')
    for tag in ['p', 'ul', 'div', 'dl']:
        elems = soup.find_all(tag)
        if elems:
            break
    if not elems:
        return None
    elems[-1].append(BeautifulSoup(f' ({source})', 'html.parser'))
    return str(soup)


# Gets identification information from each resource page
def get_identification():
    print('Getting identification information...')
    cols = ['arkiveID', 'adwID', 'fishbaseID', 'wikipediaID', 'amphibiawebID']
    resource_names = ['Arkive', 'Animal Diversity Web', 'FishBase', 'Wikipedia', 'AmphibiaWeb']
    df_species = pd.read_csv(os.path.join('data', 'species.csv'), usecols=['eolID'] + cols, dtype=object)
    
    # Select only the rows with the desired section
    def load_and_filter_df(file_path, term, section_column="CVterm", further_info_column=True):
        usecols = ['taxonID', section_column, 'description']
        if further_info_column:
            usecols.append('furtherInformationURL')
        df = pd.read_csv(file_path, sep='\t', usecols=usecols, dtype=object)
        return df[df[section_column] == term]

    df_arkive = load_and_filter_df(os.path.join('data', 'arkive', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Description', section_column='title', further_info_column=False)
    df_adw = load_and_filter_df(os.path.join('data', 'animal_diversity_web', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Morphology')
    df_fishbase = load_and_filter_df(os.path.join('data', 'fishbase', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#DiagnosticDescription')
    df_wikipedia = load_and_filter_df(os.path.join('data', 'wikipedia', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Description')
    df_amphibiaweb = load_and_filter_df(os.path.join('data', 'amphibia_web', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#GeneralDescription')


    # Merge into one dataframe
    df_merged = df_species
    dfs = [df_arkive, df_adw, df_fishbase, df_wikipedia, df_amphibiaweb]
    for df, suffix in zip(dfs, cols):
        df_merged = df_merged.merge(df, left_on=suffix, right_on='taxonID', how='left', suffixes=('', f'_{suffix}'))
        df_merged = df_merged.rename(columns={'description': f'description_{suffix}', 'furtherInformationURL': f'url_{suffix}'})
    

    # Clean up the descriptions
    df_merged['description_arkiveID'] = df_merged['description_arkiveID'].apply(remove_arkive_refs).apply(wrap_in_p_tag)
    df_merged['description_adwID'] = df_merged['description_adwID'].apply(remove_traits).apply(remove_adw_amphibia_refs)
    df_merged['description_fishbaseID'] = df_merged['description_fishbaseID'].apply(remove_fishbase_refs).apply(wrap_in_p_tag)
    df_merged['description_wikipediaID'] = df_merged['description_wikipediaID'].apply(extract_wiki_section)
    df_merged['description_amphibiawebID'] = df_merged['description_amphibiawebID'].apply(extract_first_paragraphs).apply(remove_adw_amphibia_refs)

    # Remove oldid from wikipedia urls
    df_merged['url_wikipediaID'] = df_merged['url_wikipediaID'].apply(lambda url: re.sub(r'&oldid=.*', '', url) if not pd.isnull(url) else None)
    
    # Add source urls to the descriptions
    for col, resource_name in zip(cols, resource_names):
        if resource_name == 'Arkive':
            refs = 'Arkive'
        else:
            refs = df_merged[f'url_{col}'].apply(lambda url: f'<a href="{url}">{resource_name}</a>')
        df_merged[f'description_{col}'] = df_merged[f'description_{col}'].combine(refs, add_source)

    # Fill missing descriptions with the order of priority in cols
    df_merged['identification'] = pd.NA
    for col in cols:
        df_merged['identification'] = df_merged['identification'].fillna(df_merged[f'description_{col}'])


    print(f"Species with identification info: {df_merged['identification'].count()} / {len(df_merged)}")

    df_merged = df_merged.reindex(columns=['eolID', 'identification'])
    df_merged.to_csv(os.path.join('data', 'species with identification.csv'), index=False)