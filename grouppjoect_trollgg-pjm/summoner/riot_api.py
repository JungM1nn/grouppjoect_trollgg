import requests
from urllib.parse import quote

class RiotAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://americas.api.riotgames.com/riot/account/v1/accounts"

    def _make_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}?api_key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()  # 오류 발생 시 예외를 던짐
        return response.json()

    def get_account_by_riot_id(self, riot_id, tag_line):
        encoded_riot_id = quote(riot_id)
        encoded_tag_line = quote(tag_line)
        endpoint = f"by-riot-id/{encoded_riot_id}/{encoded_tag_line}"
        return self._make_request(endpoint)

    def get_summoner_league_info(self, summoner_id):
        url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            league_info = response.json()
            return league_info
        else:
            print("Error:", response.status_code)
            return None

    def get_top_players(self, queue):
        url = f"https://kr.api.riotgames.com/lol/league/v4/{queue}/by-queue/RANKED_SOLO_5x5?api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            league_data = response.json()
            return league_data['entries'], queue  # 플레이어 정보와 해당 큐 정보 반환
        else:
            print("Error:", response.status_code)
            return None, None  # 에러 발생 시 None 반환

    def get_puuid_by_summoner_id(self, summoner_id):
        url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            summoner_data = response.json()
            return summoner_data['puuid']
        else:
            print("Error:", response.status_code)
            return None

    def get_game_name_and_tagline_by_puuid(self, puuid):
        url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            account_data = response.json()
            game_name = account_data['gameName']
            tag_line = account_data['tagLine']
            return f"{game_name}#{tag_line}"
        else:
            print("Error:", response.status_code)
            return None

    def convert_queue(self, queue):
        if queue == 'challengerleagues':
            return 'CHALLENGER'
        elif queue == 'grandmasterleagues':
            return 'GRANDMASTER'
        elif queue == 'masterleagues':
            return 'MASTER'
        else:
            return 'UNKNOWN'
