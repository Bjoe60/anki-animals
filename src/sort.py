import pandas as pd
import os

# Sorts the rows of exported deck (to keep order when first downloaded)
# Assuming exported notes as .txt with all options selected

DECK_NAME = 'The Animal Deck'
TAXONOMIC_SORT_COLUMN = 9
NUMERICAL_COLUMNS = [2, 6, 7, 8, 9, 10]

def sort_rows():
    df_header = pd.read_csv(os.path.join('data', f'{DECK_NAME}.txt'), sep='\t', nrows=6, header=None, dtype=str)
    df = pd.read_csv(os.path.join('data', f'{DECK_NAME}.txt'), sep='\t', skiprows=6, header=None, dtype=str)
    df.sort_values(by=df.columns[TAXONOMIC_SORT_COLUMN + 3], inplace=True)
    df = pd.concat([df_header, df])
    df.to_csv(os.path.join('data', f'{DECK_NAME} sorted.txt'), sep='\t', index=False, header=False)

if __name__ == '__main__':
    sort_rows()