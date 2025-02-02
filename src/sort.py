import pandas as pd
import os

# Sorts the rows of exported deck (to keep order when first downloaded)
# Assuming exported notes as .txt with all options selected

DECK_NAME = 'The Animal Deck'
TAXONOMIC_SORT_COLUMN = 9
AS_INT = False

def extract_rank(tag_string):
    if "genus" in tag_string.split():
        return "genus"
    if "species" in tag_string.split():
        return "species"
    return None

def sort_rows():
    df_header = pd.read_csv(os.path.join('data', 'output', f'{DECK_NAME}.txt'), sep='\t', nrows=6, header=None, dtype=str)
    df = pd.read_csv(os.path.join('data', 'output', f'{DECK_NAME}.txt'), sep='\t', skiprows=6, header=None, dtype={i: int if AS_INT and i == TAXONOMIC_SORT_COLUMN + 3 else str for i in range(75)})

    # Extract tag column from header
    tags_column = int(df_header.iloc[5, 0][13:]) - 1

    # Extract rank and sort
    df["rank"] = df.iloc[:, tags_column].apply(extract_rank)
    df["rank"] = pd.Categorical(df["rank"], categories=["genus", "species"], ordered=True)
    df.sort_values(by=["rank", df.columns[TAXONOMIC_SORT_COLUMN + 3]], inplace=True)
    df.drop(columns=["rank"], inplace=True)

    # Combine with header and save
    df = pd.concat([df_header, df])
    df.to_csv(os.path.join('data', 'output', f'{DECK_NAME} sorted.txt'), sep='\t', index=False, header=False)


if __name__ == '__main__':
    sort_rows()