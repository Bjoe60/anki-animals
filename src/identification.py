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

def replace_line_breaks(text):
    return text.replace('\\n', '<br>') if not pd.isnull(text) else None

def replace_old_links(text):
    if pd.isnull(text):
        return None
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.find_all('a'):
        if a.get('href', '').startswith('http://animaldiversity.ummz.umich.edu/site'):
            a.decompose()
    return str(soup)

# Remove references like (Source 2000)
def remove_adw_amphibia_refs(text):
    return re.sub(r'(<p>)?\s?\([^)]+?\d{4}[^)]*?\)(?(1)\.?<\/p>)', '', text).replace('. .', '.') if not pd.isnull(text) else None

# Remove references like (Ref. source)
def remove_fishbase_refs(text):
    return re.sub(r'\s?\(Ref\..*?\)', '', text) if not pd.isnull(text) else None

# Remove references like [1], [2], etc.
def remove_wiki_refs(soup):
    for sup_tag in soup.find_all('sup'):
        if not sup_tag.decomposed and sup_tag.get('id', '').startswith('cite_ref'):
            # Remove all sup tags next to the current one
            for sibling in sup_tag.find_next_siblings('sup'):
                sibling.decompose()
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

def is_too_long(descriptions):
    return sum(len(desc) for desc in descriptions) > 2200

def add_dots(text):
    if text.endswith('</p>'):
        return re.sub(r'</p>$', r'</p><p>...</p>', text)
    return re.sub(r'\.?\s?(<\/[^>]+>)$', r'...\1', text)

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
        if sibling.name == 'h2' or sibling.find('h2') or \
            (sibling.name == 'h3' or sibling.find('h3')) and descriptions:
            break
        if is_too_long(descriptions):
            # Add '...' to the end if cut off
            descriptions[-1] = add_dots(descriptions[-1])
            break

        descriptions.append(remove_wiki_refs(sibling))

    return "".join(descriptions)

def extract_first_paragraphs(html):
    soup = BeautifulSoup(str(html), 'html.parser')
    paragraphs = []
    for paragraph in soup.find_all('p'):
        if paragraph.find(['img', 'audio', 'iframe']):
            continue
        paragraphs.append(str(paragraph))
        if is_too_long(paragraphs):
            # Add '...' to the end if cut off
            paragraphs[-1] = add_dots(paragraphs[-1])
            break
    
    return "".join(paragraphs)

def clean_html(text):
    if pd.isnull(text):
        return None
    
    # Remove text before the first tag
    text = re.sub(r'^[^<]*<', '<', text)

    soup = BeautifulSoup(text, 'html.parser')
    for tag in ['img', 'video', 'audio', 'iframe']:
        for match in soup.find_all(tag):
            match.decompose()
    return str(soup)

# Add source to the last paragraph of the text
def add_source(text, source):
    if pd.isnull(text):
        return None
    return re.sub(r'(<\/[^>]+>)$', fr' ({source})\1', text)


# Gets identification information from each resource page
def get_identification(deck):
    print('Getting identification information...')
    cols = ['arkiveID', 'adwID', 'fishbaseID', 'wikipediaID', 'amphibiawebID']
    resource_names = ['Arkive', 'Animal Diversity Web', 'FishBase', 'Wikipedia', 'AmphibiaWeb']
    df_species = pd.read_csv(os.path.join('data', 'processed', f'{deck.value['type']} species.csv'), usecols=['eolID'] + cols, dtype=object)
    
    # Select only the rows with the desired section
    def load_and_filter_df(file_path, term, section_column="CVterm", further_info_column=True):
        usecols = ['taxonID', section_column, 'description']
        if further_info_column:
            usecols.append('furtherInformationURL')
        df = pd.read_csv(file_path, sep='\t', usecols=usecols, dtype=object)
        return df[df[section_column] == term]

    df_arkive = load_and_filter_df(os.path.join('data', 'input', 'arkive', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Description', section_column='title', further_info_column=False)
    df_adw = load_and_filter_df(os.path.join('data', 'input', 'animal_diversity_web', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Morphology')
    df_fishbase = load_and_filter_df(os.path.join('data', 'input', 'fishbase', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#DiagnosticDescription')
    df_wikipedia = load_and_filter_df(os.path.join('data', 'input', 'wikipedia', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#Description')
    df_wikipedia_summary = load_and_filter_df(os.path.join('data', 'input', 'wikipedia', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#TaxonBiology')
    df_amphibiaweb = load_and_filter_df(os.path.join('data', 'input', 'amphibia_web', 'media_resource.tab'), 'http://rs.tdwg.org/ontology/voc/SPMInfoItems#GeneralDescription')


    # Merge into one dataframe
    df_merged = df_species
    dfs = [df_arkive, df_adw, df_fishbase, df_wikipedia, df_amphibiaweb]
    for df, suffix in zip(dfs, cols):
        df_merged = df_merged.merge(df, left_on=suffix, right_on='taxonID', how='left', suffixes=('', f'_{suffix}'))
        df_merged = df_merged.rename(columns={'description': f'description_{suffix}', 'furtherInformationURL': f'url_{suffix}'})

    # Clean up the descriptions
    df_merged['description_arkiveID'] = df_merged['description_arkiveID'].apply(remove_arkive_refs).apply(wrap_in_p_tag)
    df_merged['description_adwID'] = df_merged['description_adwID'].apply(remove_traits).apply(remove_adw_amphibia_refs).apply(replace_line_breaks).apply(replace_old_links)
    df_merged['description_fishbaseID'] = df_merged['description_fishbaseID'].apply(remove_fishbase_refs).apply(wrap_in_p_tag)
    df_merged['description_wikipediaID'] = df_merged['description_wikipediaID'].apply(extract_wiki_section)
    df_merged['description_amphibiawebID'] = df_merged['description_amphibiawebID'].apply(extract_first_paragraphs).apply(remove_adw_amphibia_refs)

    # Fill missing Wikipedia descriptions with the summary
    df_merged = df_merged.merge(df_wikipedia_summary, left_on='wikipediaID', right_on='taxonID', how='left', suffixes=('', '_summary'))
    df_merged['description'] = df_merged['description'].apply(clean_html)
    df_merged['description_wikipediaID'] = df_merged['description_wikipediaID'].combine_first(df_merged['description'])


    # Remove oldid from wikipedia urls
    df_merged['url_wikipediaID'] = df_merged['url_wikipediaID'].apply(lambda url: re.sub(r'&oldid=.*', '', url) if not pd.isnull(url) else None)
    
    # Add source urls to the descriptions
    for col, resource_name in zip(cols, resource_names):
        if resource_name == 'Arkive':
            refs = 'Arkive'
        else:
            refs = df_merged[f'url_{col}'].apply(lambda url: f'<a href="{url}">{resource_name}</a>')
        df_merged[f'description_{col}'] = df_merged[f'description_{col}'].combine(refs, add_source)

    # Fill missing descriptions with the order of priority in 'cols'
    df_merged['identification'] = pd.NA
    for col in cols:
        df_merged['identification'] = df_merged['identification'].fillna(df_merged[f'description_{col}'])


    print(f"Taxa with identification info: {(df_merged['identification'] != '').sum()} / {len(df_merged)}")

    df_merged = df_merged.reindex(columns=['eolID', 'identification'])
    df_merged.to_csv(os.path.join('data', 'processed', f'{deck.value['type']} species with identification.csv'), index=False)