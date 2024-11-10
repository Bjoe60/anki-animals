import pandas as pd
import os

def get_species():
    # Download full taxonomy from https://opendata.eol.org/dataset/tram-807-808-809-810-dh-v1-1/resource/00adb47b-57ed-4f6b-8f66-83bfdb5120e8
    df = pd.read_csv(os.path.join('data', 'taxon.tab'), sep='\t', dtype=str)
    df = df.dropna(subset=['higherClassification'])
    df = df[df['higherClassification'].str.startswith('Life|Cellular Organisms|Eukaryota|Opisthokonta|Metazoa|Bilateria|Deuterostomia|Chordata|Vertebrata|Gnathostomata|Osteichthyes|Sarcopterygii|Tetrapoda|Amniota|Synapsida|Therapsida|Cynodontia|Mammalia')]
    df = df[df['taxonRank'].values == 'species']

    print(len(df))

    df.to_csv(os.path.join('data', 'species.csv'), index=False)