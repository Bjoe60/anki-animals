from enum import Enum

class Deck(Enum):
    ANIMALS = {'type': 'Animal', 'taxa': 'Life|Cellular Organisms|Eukaryota|Opisthokonta|Metazoa'}
    PLANTS = {'type': 'Plant', 'taxa': 'Life|Cellular Organisms|Eukaryota|Archaeplastida|Chloroplastida'}
    FUNGUS = {'type': 'Fungus', 'taxa': 'Life|Cellular Organisms|Eukaryota|Opisthokonta|Nucletmycea|Fungi'}