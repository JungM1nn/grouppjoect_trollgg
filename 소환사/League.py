import requests

def get_summoner_league_info(api_key, summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        league_info = response.json()
        return league_info
    else:
        print("Error:", response.status_code)

# API 키와 소환사 ID 설정
api_key = 'RGAPI-13b3567c-a7dc-4381-831e-596324cd3a90'
summoner_id = ''

# 소환사 리그 정보 가져오기
summoner_league_info = get_summoner_league_info(api_key, summoner_id)

# 출력
print(summoner_league_info)
