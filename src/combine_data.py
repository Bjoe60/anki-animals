import pandas as pd
import os
from functools import reduce

def create_csv(df):
    with open(os.path.join('data', 'animals.csv'), 'w', encoding='utf-8', newline='') as f:
        # File header for Anki
        f.write('#separator:Comma\n#html:true\n#notetype:Species\n#deck:Animals\n#tags column:3\n#columns:EOL ID,Scientific,Tags,iNaturalist ID,GBIF ID,English,Afrikaans,Albanian,Arabic,Armenian,Azerbaijani,Belarusian,Bengali,Bulgarian,Catalan,Chinese,Croatian,Czech,Danish,Dutch,Estonian,Finnish,French,Galician,Georgian,German,Greek,Hebrew,Hungarian,Icelandic,Indonesian,Italian,Japanese,Kazakh,Korean,Latvian,Lithuanian,Macedonian,Malay,Maltese,Mongolian,Nepali,Norwegian,Persian,Polish,Portuguese,Romanian,Russian,Serbian,Slovak,Slovenian,Spanish,Swahili,Swedish,Thai,Turkish,Ukrainian,Uzbek,Vietnamese,Countries,Images,extinct,Observations,Wikipedia,Summary\n')
        
        df.to_csv(f, index=False)


def combine_data():
    print("Combining data...")
    df_translations = pd.read_csv(os.path.join('data', 'species with translations.csv'))
    df_countries = pd.read_csv(os.path.join('data', 'species with countries.csv'))
    df_images = pd.read_csv(os.path.join('data', 'species with images.csv'))

    df_merged = reduce(lambda left,right: pd.merge(left,right, on=['eolID', 'canonicalName', 'higherClassification', 'inaturalistID', 'gbifID'], how='left'), [df_translations, df_countries, df_images])
    
    # Prefer the English names from iNaturalist
    df_merged['English'] = df_merged['preferred_common_name'].combine_first(df_merged['English'])
    df_merged.drop(columns=['preferred_common_name'], inplace=True)

    # Create tags
    df_merged['higherClassification'] = df_merged['higherClassification'].str.replace('Life|Cellular Organisms|Eukaryota|Opisthokonta|Metazoa|Bilateria|Deuterostomia|Chordata|Vertebrata|Gnathostomata|Osteichthyes|Sarcopterygii|Tetrapoda|Amniota|Synapsida|Therapsida|Cynodontia|', '').str.replace('|', '::').str.replace(' ', '-')
    df_merged['higherClassification'] = df_merged['country'] + ' ' + df_merged['higherClassification']
    
    create_csv(df_merged)
    print("Done.")