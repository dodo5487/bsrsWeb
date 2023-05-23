# Visit https://github.com/commonsense/conceptnet5/wiki/API for more information

import requests

def get_conceptnet_data(word,language='zh'):
    """
    Get data from ConceptNet API
    """
    url = f'http://api.conceptnet.io/c/{language}/{word}' 
    obj = requests.get(url).json()
    return obj

print(type(get_conceptnet_data('狗')["edges"][0]))
# with open("data.json", "w", encoding="utf-8") as f:
#     f.write(str(get_conceptnet_data('狗')["edges"][0]))