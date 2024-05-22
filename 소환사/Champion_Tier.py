import requests
import json
RIOT_API_KEY = 'RGAPI-cda58d9d-08ae-4c22-933e-880b9e5e76b9'
REGION = 'na1'  # 예시로 북미 서버를 사용합니다.
DATA_DRAGON_VERSION = '13.6.1'  # 최신 버전 확인 필요
# Data Dragon URL
data_dragon_url = f'http://ddragon.leagueoflegends.com/cdn/{DATA_DRAGON_VERSION}/data/en_US/champion.json'
# 챔피언 기본 정보 가져오기
response = requests.get(data_dragon_url)
champion_data = response.json()['data']
# 챔피언 ID와 이름 매핑
champion_id_to_name = {int(champ['key']): champ['id'] for champ in champion_data.values()}
# 최근 매치 ID 가져오기
def get_recent_matches(puuid, count=20):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}'
    headers = {'X-Riot-Token': 'RGAPI-cda58d9d-08ae-4c22-933e-880b9e5e76b9'}
    response = requests.get(url, headers=headers)
    return response.json()
# 매치 상세 정보 가져오기
def get_match_details(match_id):
    url = f'https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    headers = {'X-Riot-Token': 'RGAPI-cda58d9d-08ae-4c22-933e-880b9e5e76b9'}
    response = requests.get(url, headers=headers)
    return response.json()
# 특정 소환사의 PUUID 가져오기
def get_summoner_puuid(summoner_name):
    url = f'https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
    headers = {'X-Riot-Token': 'RGAPI-cda58d9d-08ae-4c22-933e-880b9e5e76b9'}
    response = requests.get(url, headers=headers)
    return response.json()['puuid']
# 승률 계산
def calculate_win_rate(matches):
    champion_stats = {}
    for match_id in matches:
        match_details = get_match_details(match_id)
        for participant in match_details['info']['participants']:
            champ_id = participant['championId']
            win = participant['win']
            if champ_id not in champion_stats:
                champion_stats[champ_id] = {'wins': 0, 'games': 0}
            champion_stats[champ_id]['games'] += 1
            if win:
                champion_stats[champ_id]['wins'] += 1
    win_rates = {champion_id_to_name[champ_id]: stats['wins'] / stats['games'] * 100
                 for champ_id, stats in champion_stats.items()}
    return win_rates
# 티어 분류
def classify_tiers(win_rates):
    tiers = {'S': [], 'A': [], 'B': [], 'C': [], 'D': []}
    for champ, win_rate in win_rates.items():
        if win_rate >= 55:
            tiers['S'].append(champ)
        elif win_rate >= 52:
            tiers['A'].append(champ)
        elif win_rate >= 50:
            tiers['B'].append(champ)
        elif win_rate >= 47:
            tiers['C'].append(champ)
        else:
            tiers['D'].append(champ)
    return tiers
# 주요 함수 실행 예제
summoner_name = 'example_summoner'
puuid = get_summoner_puuid(summoner_name)
recent_matches = get_recent_matches(puuid)
win_rates = calculate_win_rate(recent_matches)
tiers = classify_tiers(win_rates)
# 티어 등급표 출력
for tier, champs in tiers.items():
    print(f'{tier} Tier: {", ".join(champs)}')