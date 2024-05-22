import requests
from urllib.parse import quote

api_key = 'RGAPI-ec2d4574-f76b-4b72-8559-3fafa813329d'  # Riot API 키
riot_id = '매일 졸려여'  # 한글이 포함된 Riot ID
tag_line = 'KR1'  # 한글이 포함된 태그 라인


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


def get_queue_type_description(queue_id):
    queue_descriptions = {
        420: "솔로랭크",
        440: "자유랭크"
        # 필요한 경우 여기에 다른 큐 ID와 설명 추가
    }
    return queue_descriptions.get(queue_id, "알 수 없는 큐 타입")


def get_map_description(map_id):
    map_descriptions = {
        11: "소환사의 협곡"
        # 필요한 경우 여기에 다른 맵 ID와 설명 추가
    }
    return map_descriptions.get(map_id, "알 수 없는 맵")


# PUUID 검색
puuid = get_puuid(api_key, riot_id, tag_line)
if puuid:
    # API 요청 URL
    url = f"https://kr.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{
        puuid}?api_key={api_key}"

    # API 요청 보내기
    response = requests.get(url)

    # 응답 데이터 확인
    if response.status_code == 200:
        game_data = response.json()
        queue_type = game_data['gameQueueConfigId']
        map_id = game_data['mapId']
        queue_description = get_queue_type_description(queue_type)
        map_description = get_map_description(map_id)
        print(f"{queue_description}, {map_description}")

        # 참가자들을 팀별로 분류하고 출력
        participants = game_data['participants']
        blue_team = []
        red_team = []

        for participant in participants:
            team = blue_team if participant['teamId'] == 100 else red_team
            team.append(participant)

        # 블루팀 참가자 출력
        print("\n블루팀")
        for player in blue_team:
            # 각 플레이어의 정보 출력
            summoner_id = player.get('summonerId')
            summoner_league_info = get_summoner_league_info(
                api_key, summoner_id)

            if summoner_league_info:
                for entry in summoner_league_info:
                    # 솔로랭크 정보만 출력
                    if queue_type == 420 and entry['queueType'] == 'RANKED_SOLO_5x5':
                        if 'tier' in entry:  # 랭크 정보가 있는 경우에만 출력
                            tier = entry['tier']
                            division = entry['rank']
                            league_points = entry['leaguePoints']
                            wins = entry['wins']
                            losses = entry['losses']
                            tier_rank = f"{tier} {division}"
                            total_games = wins + losses
                            win_rate = (wins / total_games) * \
                                100 if total_games > 0 else 0
                            print(
                                f"{player['riotId']} - {tier_rank} ({league_points}LP) {win_rate:.0f}% ({total_games}게임)")
                        else:
                            print(f"{player['riotId']} -")
                    # 자유랭크 정보만 출력
                    elif queue_type == 440 and entry['queueType'] == 'RANKED_FLEX_SR':
                        if 'tier' in entry:  # 랭크 정보가 있는 경우에만 출력
                            tier = entry['tier']
                            division = entry['rank']
                            league_points = entry['leaguePoints']
                            wins = entry['wins']
                            losses = entry['losses']
                            tier_rank = f"{tier} {division}"
                            total_games = wins + losses
                            win_rate = (wins / total_games) * \
                                100 if total_games > 0 else 0
                            print(
                                f"{player['riotId']} - {tier_rank} ({league_points}LP) {win_rate:.0f}% ({total_games}게임)")
                        else:
                            print(f"{player['riotId']} -")
            else:
                print(f"{player['riotId']} -")

        # 레드팀 참가자 출력
        print("\n레드팀")
        for player in red_team:
            # 각 플레이어의 정보 출력
            summoner_id = player.get('summonerId')
            summoner_league_info = get_summoner_league_info(
                api_key, summoner_id)

            if summoner_league_info:
                for entry in summoner_league_info:
                    # 솔로랭크 정보만 출력
                    if queue_type == 420 and entry['queueType'] == 'RANKED_SOLO_5x5':
                        if 'tier' in entry:  # 랭크 정보가 있는 경우에만 출력
                            tier = entry['tier']
                            division = entry['rank']
                            league_points = entry['leaguePoints']
                            wins = entry['wins']
                            losses = entry['losses']
                            tier_rank = f"{tier} {division}"
                            total_games = wins + losses
                            win_rate = (wins / total_games) * \
                                100 if total_games > 0 else 0
                            print(
                                f"{player['riotId']} - {tier_rank} ({league_points}LP) {win_rate:.0f}% ({total_games}게임)")
                        else:
                            print(f"{player['riotId']} -")
                    # 자유랭크 정보만 출력
                    elif queue_type == 440 and entry['queueType'] == 'RANKED_FLEX_SR':
                        if 'tier' in entry:  # 랭크 정보가 있는 경우에만 출력
                            tier = entry['tier']
                            division = entry['rank']
                            league_points = entry['leaguePoints']
                            wins = entry['wins']
                            losses = entry['losses']
                            tier_rank = f"{tier} {division}"
                            total_games = wins + losses
                            win_rate = (wins / total_games) * \
                                100 if total_games > 0 else 0
                            print(
                                f"{player['riotId']} - {tier_rank} ({league_points}LP) {win_rate:.0f}% ({total_games}게임)")
                        else:
                            print(f"{player['riotId']} -")
            else:
                print(f"{player['riotId']} -")

    else:
        if response.status_code == 404:
            print(f"'{riot_id}#{tag_line}'님은 현재 게임중이 아닙니다.")
        else:
            print("Error:", response.status_code)
else:
    print("PUUID를 찾을 수 없습니다.")
