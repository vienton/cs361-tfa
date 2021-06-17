import requests, json
import constants

def get_encrypted(title):
    # Get encrypted title
    payload = {'Text':title, 'Key':'42'}
    res = requests.post(constants.encrypt_url, params=payload)
    title = json.loads(res.text)['Secret']
    return title