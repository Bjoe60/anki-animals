from taxa import Deck
from species import get_species
from identification import get_identification
from translations import get_translations
from images import get_images
from countries import get_countries
from combine_data import combine_data

WANTED_DECK = Deck.ANIMALS

def main():
    # get_species(WANTED_DECK)
    # get_identification(WANTED_DECK)
    # get_translations(WANTED_DECK)
    # get_countries(WANTED_DECK)
    # get_images(WANTED_DECK)
    combine_data(WANTED_DECK)


if __name__ == '__main__':
    main()