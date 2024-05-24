import requests
from urllib.parse import quote

class RiotAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.status_code)
            return None

    def get_puuid(self, riot_id, tag_line):
        encoded_riot_id = quote(riot_id)
        encoded_tag_line = quote(tag_line)
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_riot_id}/{encoded_tag_line}?api_key={self.api_key}"
        data = self._get(url)
        if data:
            return data.get('puuid')
        return None

    def get_summoner_id(self, puuid):
        url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={self.api_key}"
        data = self._get(url)
        if data:
            return data.get('id')
        return None

    def get_summoner_league_info(self, summoner_id):
        url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={self.api_key}"
        return self._get(url)

    def get_top_players(self, queue):
        url = f"https://kr.api.riotgames.com/lol/league/v4/{queue}/by-queue/RANKED_SOLO_5x5?api_key={self.api_key}"
        response = self._get(url)
        if response:
            return response.get('entries', []), queue
        return None, None

    def get_puuid_by_summoner_id(self, summoner_id):
        url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={self.api_key}"
        data = self._get(url)
        if data:
            return data.get('puuid')
        return None

    def get_game_name_and_tagline_by_puuid(self, puuid):
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={self.api_key}"
        data = self._get(url)
        if data:
            return f"{data.get('gameName')}#{data.get('tagLine')}"
        return None

    @staticmethod
    def convert_queue(queue):
        if queue == 'challengerleagues':
            return 'CHALLENGER'
        elif queue == 'grandmasterleagues':
            return 'GRANDMASTER'
        elif queue == 'masterleagues':
            return 'MASTER'
        else:
            return 'UNKNOWN'
