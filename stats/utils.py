# stats/utils.py

import requests
from urllib.parse import quote

API_KEY = 'RGAPI-ec2d4574-f76b-4b72-8559-3fafa813329d'

def get_puuid(api_key, riot_id, tag_line):
    encoded_riot_id = quote(riot_id)
    encoded_tag_line = quote(tag_line)
    url_puuid = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_riot_id}/{encoded_tag_line}?api_key={api_key}"
    response_puuid = requests.get(url_puuid)

    if response_puuid.status_code == 200:
        data_puuid = response_puuid.json()
        return data_puuid.get('puuid')
    else:
        print("Error:", response_puuid.status_code)
        return None

def get_summoner_id(api_key, puuid):
    url_summoner = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
    response_summoner = requests.get(url_summoner)

    if response_summoner.status_code == 200:
        summoner_data = response_summoner.json()
        return summoner_data.get('id')
    else:
        print("Error:", response_summoner.status_code)
        return None

def get_summoner_league_info(api_key, summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None

def get_top_players(api_key, queue):
    url = f"https://kr.api.riotgames.com/lol/league/v4/{queue}/by-queue/RANKED_SOLO_5x5?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        league_data = response.json()
        return league_data.get('entries', []), queue
    else:
        print("Error:", response.status_code)
        return None, None

def get_puuid_by_summoner_id(api_key, summoner_id):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        summoner_data = response.json()
        return summoner_data.get('puuid')
    else:
        print("Error:", response.status_code)
        return None

def get_game_name_and_tagline_by_puuid(api_key, puuid):
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        account_data = response.json()
        return f"{account_data.get('gameName')}#{account_data.get('tagLine')}"
    else:
        print("Error:", response.status_code)
        return None

def convert_queue(queue):
    if queue == 'challengerleagues':
        return 'CHALLENGER'
    elif queue == 'grandmasterleagues':
        return 'GRANDMASTER'
    elif queue == 'masterleagues':
        return 'MASTER'
    else:
        return 'UNKNOWN'
