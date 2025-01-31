# anki-animals

Code used to generate [The Animal Deck](https://ankiweb.net/shared/info/934600214), [The Plant Deck](https://ankiweb.net/shared/info/1824327532) and [The Fungus Deck](https://ankiweb.net/shared/info/380167559).

Csv files are generated consecutively for each method in main.py and combined in `combine_data()` to limit running times. Uncomment the methods where something is changed and change which species are gathered in `species.py`.

Note that `get_images()` takes three hours to run with the API call limit, so only run it if you have changed anything in `images.py`.

To update the country information (`GBIF_output.csv`), you will have to become an invited tester for [GBIFs API SQL Downloads](https://techdocs.gbif.org/en/data-use/api-sql-downloads) and follow the instructions on that page.

## Files
These files were too large to upload to GitHub:
- `taxon.tab`: https://opendata.eol.org/dataset/tram-807-808-809-810-dh-v1-1/resource/00adb47b-57ed-4f6b-8f66-83bfdb5120e8
- `full_provider_ids.csv`: https://zenodo.org/records/13751009
- `vernacularnames.csv`: https://opendata.eol.org/dataset/vernacular-names
- `wikipedia`: https://opendata.eol.org/dataset/wikip/resource/8d4b6858-a26b-42fe-8d3a-cc3f7f7020b9
- `arkive`: https://opendata.eol.org/dataset/arkive/resource/d02e7ce4-d239-43e3-b22d-3ee030a50f44
- `animal_diversity_web`: https://opendata.eol.org/dataset/birds_adw/resource/9ba2032a-81cd-4e8c-a70a-6e1b82a8fbda
- `fishbase`: https://opendata.eol.org/dataset/fishbase/resource/c5b89cec-8179-4222-978d-cde2be5adf0c
- `amphibia_web`: https://opendata.eol.org/dataset/amphibiaweb/resource/639efbfb-3b79-49e7-894f-50df4fa25da8
