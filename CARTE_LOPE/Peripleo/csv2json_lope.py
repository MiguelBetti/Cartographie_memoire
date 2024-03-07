# Developed by Elina Leblanc (University of Geneva)
# Lines 60-63: Based on the code of Leodanis Pozo Ramos (https://realpython.com/python-defaultdict/#grouping-items)

import csv
import json
from collections import defaultdict
import re

places_all = []  # List with all places (normalized name)
places_single = []  # Deduplicated list of places
places_count = []  # List of places with their number of occurrences

list_places = []  # List of places with their coordinates, Wikidata id and type
list_places_deduplicated = []
list_pliegos = []  # List of each place with a sublist with information about the document where it appears
list_pliegos_deduplicated = []
list_places_nbTimes = []

with open('../comedia.csv', encoding='utf-8') as f:
    csv_file = csv.reader(f)  # We parse the CSV file
    next(csv_file)  # We skip the first line

    for line in csv_file:
        if line[3] != '':
            # List with only the normalized names
            places_all.append(line[3])
            if line[3] not in places_single:
                places_single.append(line[3])

            id_place = re.split('/', line[0])
            # print(id_place[-1])

            list_places_nbTimes.append([line[3], line[2]])

            # List with information about the place
            # Reproduce the structure of the format JSON Linked Place needed by the application Peripleo
            list_places.append({'@id': id_place[-1], 'uuid': line[0],
                                'type': 'Feature', 'properties': {'title': line[3], 'occurrences': []},
                                'geometry': {'type': 'Point', 'coordinates': [float(line[9]), float(line[8])]},
                                'descriptions': '',
                                'names': [{'toponym': line[3], 'lang': 'es'}],
                                'links': [{'type': 'closeMatch', 'identifier': 'https://pleiades.stoa.org/places/746826'},
                                          {'type': 'closeMatch', 'identifier': 'http://www.geonames.org/350564/'}]
                                })

            # List with information about the document where a place appears
            # Reproduce the structure of the format JSON Linked Place needed by the application Peripleo
            list_pliegos.append([line[3], {'relationType': 'gvp:aat2208_locus-setting_for',
                                 'title': line[1],
                                 'subgenre': line[15],
                                 'genre': line[14],
                                 'date': line[12]}])

# print(list_places_nbTimes)
# We remove the duplicates
for i in range(len(list_places)):
    if list_places[i] not in list_places_deduplicated:
        list_places_deduplicated.append(list_places[i])

for j in range(len(list_pliegos)):
    if list_pliegos[j] not in list_pliegos_deduplicated:
        list_pliegos_deduplicated.append(list_pliegos[j])

# We associate each place with a sublist containing all the document where it appears
# Example: [[Sevilla, [{'relationType': ...}], ...]]
data = defaultdict(list)
for key, value in list_pliegos_deduplicated:
    data[key].append(value)
list_pliegos_pairs = [list(t) for t in data.items()]

number = defaultdict(list)
for k, v in list_places_nbTimes:
    number[k].append(int(v))
list_places_nb = [list(n) for n in number.items()]
print(list_places_nb)

for k in range(len(list_pliegos_pairs)):
    # For each place, we add the list of documents
    if list_places_deduplicated[k]['properties']['title'] in list_pliegos_pairs[k][0]:
        list_places_deduplicated[k]['relations'] = list_pliegos_pairs[k][1]

    # For each place, we add the number of occurrences
    if list_pliegos_pairs[k][0] == list_places_nb[k][0]:
        list_places_deduplicated[k]['properties']['occurrences'] = [{'value': sum(list_places_nb[k][1])}]

# We convert the result in JSON and print them in the console
print(list_places_deduplicated)
jsonStr = json.dumps(list_places_deduplicated, ensure_ascii=False)
# print(jsonStr)

# We save the results in a JSON file
with open('drama.json', 'w', encoding='utf-8') as f:
    json.dump(list_places_deduplicated, f, ensure_ascii=False, indent=4)
