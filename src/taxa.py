from enum import Enum

class Deck(Enum):
    ANIMALS = {'type': 'Animal', 'kingdom': 'Animals', 'taxa': 'Life|Cellular Organisms|Eukaryota|Opisthokonta|Metazoa', 'taxon_rank': ['species']}
    PLANTS = {'type': 'Plant', 'kingdom': 'Plants', 'taxa': 'Life|Cellular Organisms|Eukaryota|Archaeplastida|Chloroplastida', 'taxon_rank': ['genus', 'species']}
    FUNGUS = {'type': 'Fungus', 'kingdom': 'Fungi', 'taxa': 'Life|Cellular Organisms|Eukaryota|Opisthokonta|Nucletmycea|Fungi', 'taxon_rank': ['genus', 'species']}