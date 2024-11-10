import pandas as pd
import os

# Gets a list of mammals with scientific names and EOL IDs
def get_species():
    # Download full taxonomy from https://opendata.eol.org/dataset/tram-807-808-809-810-dh-v1-1/resource/00adb47b-57ed-4f6b-8f66-83bfdb5120e8
    df = pd.read_csv(os.path.join('data', 'taxon.tab'), sep='\t', dtype={'eolID': object, 'taxonID': str, 'acceptedNameUsageID': str, 'parentNameUsageID': str, 'datasetID': str, 'Landmark': object, 'source': str, 'furtherInformationURL': str, 'scientificName': str, 'taxonRank': str, 'taxonomicStatus': str, 'canonicalName': str, 'authority': str, 'higherClassification': str})
    df = df.dropna(subset=['higherClassification'])
    df = df[df['higherClassification'].str.startswith('Life|Cellular Organisms|Eukaryota|Opisthokonta|Metazoa|Bilateria|Deuterostomia|Chordata|Vertebrata|Gnathostomata|Osteichthyes|Sarcopterygii|Tetrapoda|Amniota|Synapsida|Therapsida|Cynodontia|Mammalia')]
    df = df[df['taxonRank'].values == 'species']
    df = df.reindex(columns=['eolID', 'canonicalName', 'higherClassification'])

    print(len(df))

    df.to_csv(os.path.join('data', 'species.csv'), index=False)