import pandas as pd
import os

COUNTRY_CODES = {'AD': 'Andorra', 'AE': 'United-Arab-Emirates', 'AF': 'Afghanistan', 'AG': 'Antigua-and-Barbuda', 'AI': 'Anguilla', 'AL': 'Albania', 'AM': 'Armenia', 'AO': 'Angola', 'AQ': 'Antarctica', 'AR': 'Argentina', 'AS': 'American-Samoa', 'AT': 'Austria', 'AU': 'Australia', 'AW': 'Aruba', 'AX': 'Åland-Islands', 'AZ': 'Azerbaijan', 'BA': 'Bosnia-and-Herzegovina', 'BB': 'Barbados', 'BD': 'Bangladesh', 'BE': 'Belgium', 'BF': 'Burkina-Faso', 'BG': 'Bulgaria', 'BH': 'Bahrain', 'BI': 'Burundi', 'BJ': 'Benin', 'BL': 'Saint-Barthélemy', 'BM': 'Bermuda', 'BN': 'Brunei-Darussalam', 'BO': 'Bolivia', 'BQ': 'Bonaire,-Sint-Eustatius-and-Saba', 'BR': 'Brazil', 'BS': 'Bahamas', 'BT': 'Bhutan', 'BV': 'Bouvet-Island', 'BW': 'Botswana', 'BY': 'Belarus', 'BZ': 'Belize', 'CA': 'Canada', 'CC': 'Cocos-(Keeling)-Islands', 'CD': 'Democratic-Republic-of-the-Congo', 'CF': 'Central-African-Republic', 'CG': 'Congo', 'CH': 'Switzerland', 'CI': 'Ivory-Coast', 'CK': 'Cook-Islands', 'CL': 'Chile', 'CM': 'Cameroon', 'CN': 'China', 'CO': 'Colombia', 'CR': 'Costa-Rica', 'CU': 'Cuba', 'CV': 'Cabo-Verde', 'CW': 'Curaçao', 'CX': 'Christmas-Island', 'CY': 'Cyprus', 'CZ': 'Czechia', 'DE': 'Germany', 'DJ': 'Djibouti', 'DK': 'Denmark', 'DM': 'Dominica', 'DO': 'Dominican-Republic', 'DZ': 'Algeria', 'EC': 'Ecuador', 'EE': 'Estonia', 'EG': 'Egypt', 'EH': 'Western-Sahara', 'ER': 'Eritrea', 'ES': 'Spain', 'ET': 'Ethiopia', 'FI': 'Finland', 'FJ': 'Fiji', 'FK': 'Falkland-Islands-(Malvinas)', 'FM': 'Federated-States-of-Micronesia', 'FO': 'Faroe-Islands', 'FR': 'France', 'GA': 'Gabon', 'GB': 'United-Kingdom', 'GD': 'Grenada', 'GE': 'Georgia', 'GF': 'French-Guiana', 'GG': 'Guernsey', 'GH': 'Ghana', 'GI': 'Gibraltar', 'GL': 'Greenland', 'GM': 'Gambia', 'GN': 'Guinea', 'GP': 'Guadeloupe', 'GQ': 'Equatorial-Guinea', 'GR': 'Greece', 'GS': 'South-Georgia-and-the-South-Sandwich-Islands', 'GT': 'Guatemala', 'GU': 'Guam', 'GW': 'Guinea-Bissau', 'GY': 'Guyana', 'HK': 'Hong-Kong', 'HM': 'Heard-Island-and-McDonald-Islands', 'HN': 'Honduras', 'HR': 'Croatia', 'HT': 'Haiti', 'HU': 'Hungary', 'ID': 'Indonesia', 'IE': 'Ireland', 'IL': 'Israel', 'IM': 'Isle-of-Man', 'IN': 'India', 'IO': 'British-Indian-Ocean-Territory', 'IQ': 'Iraq', 'IR': 'Iran', 'IS': 'Iceland', 'IT': 'Italy', 'JE': 'Jersey', 'JM': 'Jamaica', 'JO': 'Jordan', 'JP': 'Japan', 'KE': 'Kenya', 'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KI': 'Kiribati', 'KM': 'Comoros', 'KN': 'Saint-Kitts-and-Nevis', 'KP': 'North-Korea', 'KR': 'South-Korea', 'KW': 'Kuwait', 'KY': 'Cayman-Islands', 'KZ': 'Kazakhstan', 'LA': 'Laos', 'LB': 'Lebanon', 'LC': 'Saint-Lucia', 'LI': 'Liechtenstein', 'LK': 'Sri-Lanka', 'LR': 'Liberia', 'LS': 'Lesotho', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'LY': 'Libya', 'MA': 'Morocco', 'MC': 'Monaco', 'MD': 'Moldova', 'ME': 'Montenegro', 'MF': 'Saint-Martin-(French-part)', 'MG': 'Madagascar', 'MH': 'Marshall-Islands', 'MK': 'North-Macedonia', 'ML': 'Mali', 'MM': 'Myanmar', 'MN': 'Mongolia', 'MO': 'Macao', 'MP': 'Northern-Mariana-Islands', 'MQ': 'Martinique', 'MR': 'Mauritania', 'MS': 'Montserrat', 'MT': 'Malta', 'MU': 'Mauritius', 'MV': 'Maldives', 'MW': 'Malawi', 'MX': 'Mexico', 'MY': 'Malaysia', 'MZ': 'Mozambique', 'NA': 'Namibia', 'NC': 'New-Caledonia', 'NE': 'Niger', 'NF': 'Norfolk-Island', 'NG': 'Nigeria', 'NI': 'Nicaragua', 'NL': 'Netherlands', 'NO': 'Norway', 'NP': 'Nepal', 'NR': 'Nauru', 'NU': 'Niue', 'NZ': 'New-Zealand', 'OM': 'Oman', 'PA': 'Panama', 'PE': 'Peru', 'PF': 'French-Polynesia', 'PG': 'Papua-New-Guinea', 'PH': 'Philippines', 'PK': 'Pakistan', 'PL': 'Poland', 'PM': 'Saint-Pierre-and-Miquelon', 'PN': 'Pitcairn', 'PR': 'Puerto-Rico', 'PS': 'Palestine', 'PT': 'Portugal', 'PW': 'Palau', 'PY': 'Paraguay', 'QA': 'Qatar', 'RE': 'Réunion', 'RO': 'Romania', 'RS': 'Serbia', 'RU': 'Russia', 'RW': 'Rwanda', 'SA': 'Saudi-Arabia', 'SB': 'Solomon-Islands', 'SC': 'Seychelles', 'SD': 'Sudan', 'SE': 'Sweden', 'SG': 'Singapore', 'SH': 'Saint-Helena,-Ascension-and-Tristan-da-Cunha', 'SI': 'Slovenia', 'SJ': 'Svalbard-and-Jan-Mayen', 'SK': 'Slovakia', 'SL': 'Sierra-Leone', 'SM': 'San-Marino', 'SN': 'Senegal', 'SO': 'Somalia', 'SR': 'Suriname', 'SS': 'South-Sudan', 'ST': 'Sao-Tome-and-Principe', 'SV': 'El-Salvador', 'SX': 'Sint-Maarten-(Dutch-part)', 'SY': 'Syria', 'SZ': 'Eswatini', 'TC': 'Turks-and-Caicos-Islands', 'TD': 'Chad', 'TF': 'French-Southern-Territories', 'TG': 'Togo', 'TH': 'Thailand', 'TJ': 'Tajikistan', 'TK': 'Tokelau', 'TL': 'Timor-Leste', 'TM': 'Turkmenistan', 'TN': 'Tunisia', 'TO': 'Tonga', 'TR': 'Turkey', 'TT': 'Trinidad-and-Tobago', 'TV': 'Tuvalu', 'TW': 'Taiwan', 'TZ': 'Tanzania', 'UA': 'Ukraine', 'UG': 'Uganda', 'UM': 'United-States-Minor-Outlying-Islands', 'US': 'United-States-of-America', 'UY': 'Uruguay', 'UZ': 'Uzbekistan', 'VA': 'Holy-See', 'VC': 'Saint-Vincent-and-the-Grenadines', 'VE': 'Venezuela', 'VG': 'Virgin-Islands-(British)', 'VI': 'Virgin-Islands-(U.S.)', 'VN': 'Vietnam', 'VU': 'Vanuatu', 'WF': 'Wallis-and-Futuna', 'WS': 'Samoa', 'XK': 'Kosovo', 'XZ': 'International-Waters', 'YE': 'Yemen', 'YT': 'Mayotte', 'ZA': 'South-Africa', 'ZM': 'Zambia', 'ZW': 'Zimbabwe'}

def merge_rows(df):
    # Remove rows with unknown countries
    df = df[df['countrycode'] != 'ZZ']

    # Translate to country name
    df.loc[:, 'countrycode'] = df['countrycode'].map(COUNTRY_CODES)
    df.loc[:, 'countrycode'] = 'OBS::' + df['countrycode']
    df = df.rename(columns={'countrycode': 'country'})

    # Group by species and calculate total observations
    df['total_observations'] = df.groupby('taxonkey')['observation_count'].transform('sum')

    # Keep only countries with at least 5 observations (since 2000) or if the species is rare globally
    df = df[(df['observation_count'] >= 5) | (df['total_observations'] <= 300)]

    # Concat the countries into a single row
    df = df.groupby('taxonkey')['country'].apply(lambda x: ' '.join(x)).reset_index()
    df = df.rename(columns={'country': 'countries'})

    
    return df

# Get countries where each species has been observed at least 5 times since 2000 (or is rare globally)
def get_countries(deck):
    print("Getting countries...")
    df = pd.read_csv(os.path.join('data', 'processed', f'{deck.value['type']} species.csv'), usecols=['eolID', 'gbifID'])
    df_countries = pd.read_csv(os.path.join('data', 'input', 'GBIF_output.csv'), sep='\t', keep_default_na=False, na_values=[''], dtype={'taxonkey': int, 'countrycode': str, 'observation_count': int})
    
    df_countries = merge_rows(df_countries)

    df = df.merge(df_countries, left_on='gbifID', right_on='taxonkey', how='left')
    df.drop(columns=['taxonkey', 'gbifID'], inplace=True)
    df.to_csv(os.path.join('data', 'processed', f'{deck.value['type']} species with countries.csv'), index=False)