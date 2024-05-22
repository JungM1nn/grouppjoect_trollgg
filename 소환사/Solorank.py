import requests

API_KEY = 'RGAPI-ec2d4574-f76b-4b72-8559-3fafa813329d'


def get_summoner_league_info(api_key, summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{
        summoner_id}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        league_info = response.json()
        return league_info
    else:
        print("Error:", response.status_code)
        return None


def get_top_players(queue):
    url = f'https://kr.api.riotgames.com/lol/league/v4/{
        queue}/by-queue/RANKED_SOLO_5x5?api_key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        league_data = response.json()
        return league_data['entries'], queue  # 플레이어 정보와 해당 큐 정보 반환
    else:
        print("Error:", response.status_code)
        return None, None  # 에러 발생 시 None 반환


def get_puuid_by_summoner_id(summoner_id):
    url = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/{
        summoner_id}?api_key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        summoner_data = response.json()
        return summoner_data['puuid']
    else:
        print("Error:", response.status_code)
        return None


def get_game_name_and_tagline_by_puuid(puuid):
    url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{
        puuid}?api_key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        account_data = response.json()
        game_name = account_data['gameName']
        tag_line = account_data['tagLine']
        return f"{game_name}#{tag_line}"
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


queues = ['challengerleagues', 'grandmasterleagues', 'masterleagues']
all_players = []

# 각 리그의 우선순위를 정의
league_priority = {'challengerleagues': 3,
                   'grandmasterleagues': 2, 'masterleagues': 1}

for queue in queues:
    top_players, queue_type = get_top_players(queue)  # 큐 정보도 함께 가져옴
    if top_players:
        all_players.extend([(player, queue_type)
                            for player in top_players])  # 큐 정보를 플레이어 정보와 함께 저장

# 정렬 기준을 설정하여 sorted() 함수 사용
sorted_players = sorted(
    all_players, key=lambda x: (league_priority.get(x[1], 0), x[0]['leaguePoints']), reverse=True)[:10]

for idx, (player, queue_type) in enumerate(sorted_players, 1):
    summoner_id = player['summonerId']
    puuid = get_puuid_by_summoner_id(summoner_id)
    if puuid:
        game_name_and_tagline = get_game_name_and_tagline_by_puuid(puuid)
        if game_name_and_tagline:
            converted_queue = convert_queue(queue_type)
            # 소환사 리그 정보 가져오기
            summoner_league_info = get_summoner_league_info(
                API_KEY, summoner_id)
            if summoner_league_info:
                # 필요한 정보만 출력하기
                for entry in summoner_league_info:
                    wins = entry['wins']
                    losses = entry['losses']
                    # 전체 전적 수 계산
                    total_games = wins + losses
                    # 승률 계산
                    win_rate = (wins / total_games) * \
                        100 if total_games > 0 else 0
                    print(f"{idx}위 {game_name_and_tagline} {converted_queue} {
                          player['leaguePoints']}점 {wins}승 {losses}패 {win_rate:.2f}%")
            else:
                print(f"Error: {idx}위 플레이어의 리그 정보를 가져올 수 없습니다.")
        else:
            print(f"Error: {idx}위 플레이어의 게임 닉네임을 가져올 수 없습니다.")
    else:
        print(f"Error: {idx}위 플레이어의 puuid를 가져올 수 없습니다.")
