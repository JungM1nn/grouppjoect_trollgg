import requests
from urllib.parse import quote

# API 키와 소환사 정보 설정
api_key = 'RGAPI-ec2d4574-f76b-4b72-8559-3fafa813329d'
riot_id = 'WhyHealOnShen'
tag_line = 'Mid'


def get_puuid(api_key, riot_id, tag_line):
    encoded_riot_id = quote(riot_id)
    encoded_tag_line = quote(tag_line)
    url_puuid = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{
        encoded_riot_id}/{encoded_tag_line}?api_key={api_key}"
    response_puuid = requests.get(url_puuid)

    if response_puuid.status_code == 200:
        data_puuid = response_puuid.json()
        puuid = data_puuid['puuid']
        return puuid
    else:
        print("Error:", response_puuid.status_code)


def get_summoner_id(api_key, puuid):
    url_summoner = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{
        puuid}?api_key={api_key}"
    response_summoner = requests.get(url_summoner)

    if response_summoner.status_code == 200:
        summoner_data = response_summoner.json()
        summoner_id = summoner_data['id']
        return summoner_id
    else:
        print("Error:", response_summoner.status_code)


def get_summoner_league_info(api_key, summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{
        summoner_id}?api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        league_info = response.json()
        return league_info
    else:
        print("Error:", response.status_code)


# PUUID 검색
puuid = get_puuid(api_key, riot_id, tag_line)
if puuid:
    # 소환사 ID 검색
    summoner_id = get_summoner_id(api_key, puuid)
    if summoner_id:
        # 소환사 리그 정보 가져오기
        summoner_league_info = get_summoner_league_info(api_key, summoner_id)
        if summoner_league_info:
            # 필요한 정보만 출력하기
            if summoner_league_info:
                for entry in summoner_league_info:
                    queue_type = entry['queueType']
                    tier = entry['tier']
                    division = entry['rank']
                    league_points = entry['leaguePoints']
                    wins = entry['wins']
                    losses = entry['losses']

                    # 전체 전적 수 계산
                    total_games = wins + losses

                    # 승률 계산
                    win_rate = (wins / total_games) * \
                        100 if total_games > 0 else 0

                    # Tier와 Rank 합치기
                    tier_rank = f"{tier} {division}"

                    # 큐 타입 이름 변경
                    if queue_type == 'RANKED_SOLO_5x5':
                        queue_type = '솔로랭크 5x5'
                    if queue_type == 'RANKED_FLEX_SR':
                        queue_type = '자유랭크 5x5'

                    # 소환사 이름 출력
                    summoner_name = f"{riot_id}#{tag_line}"

                    print(f"소환사 이름: {summoner_name}")  # 소환사 이름 출력
                    print(f"리그: {queue_type}")
                    print(f"등급: {tier_rank}")  # Tier와 Rank 합친 문자열 출력
                    print(f"리그 포인트: {league_points}")
                    print(f"{total_games}전 {wins}승 {losses}패 {win_rate:.2f}%")
                    print("-" * 20)
        else:
            print("소환사 리그 정보를 가져올 수 없습니다.")
    else:
        print("소환사를 찾을 수 없습니다.")
else:
    print("PUUID를 찾을 수 없습니다.")
