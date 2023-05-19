# Visit https://github.com/commonsense/conceptnet5/wiki/API for more information

import requests

def get_conceptnet_data(word,language='zh'):
    """
    Get data from ConceptNet API
    """
    url = f'http://api.conceptnet.io/c/{language}/{word}' 
    obj = requests.get(url).json()
    return obj

print(get_conceptnet_data('狗'))