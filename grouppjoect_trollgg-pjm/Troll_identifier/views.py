from django.shortcuts import render
import requests
from urllib.parse import quote
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_puuid(api_key, riot_id, tag_line):
    try:
        encoded_riot_id = quote(str(riot_id))
        encoded_tag_line = quote(str(tag_line))
        url_puuid = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_riot_id}/{encoded_tag_line}?api_key={api_key}"
        response_puuid = requests.get(url_puuid)
        logger.debug(f"PUUID URL: {url_puuid}")
        logger.debug(f"PUUID Response: {response_puuid.status_code} - {response_puuid.json()}")

        if response_puuid.status_code == 200:
            data_puuid = response_puuid.json()
            puuid = data_puuid['puuid']
            return puuid
        else:
            return None
    except Exception as e:
        logger.error(f"Error in get_puuid: {e}")
        return None

def get_summoner_id(api_key, puuid):
    try:
        url_summoner = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
        response_summoner = requests.get(url_summoner)
        logger.debug(f"Summoner ID URL: {url_summoner}")
        logger.debug(f"Summoner ID Response: {response_summoner.status_code} - {response_summoner.json()}")

        if response_summoner.status_code == 200:
            summoner_data = response_summoner.json()
            summoner_id = summoner_data['id']
            return summoner_id
        else:
            return None
    except Exception as e:
        logger.error(f"Error in get_summoner_id: {e}")
        return None

def get_summoner_league_info(api_key, summoner_id):
    try:
        url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}"
        response = requests.get(url)
        logger.debug(f"League Info URL: {url}")
        logger.debug(f"League Info Response: {response.status_code} - {response.json()}")

        if response.status_code == 200:
            league_info = response.json()
            return league_info
        else:
            return None
    except Exception as e:
        logger.error(f"Error in get_summoner_league_info: {e}")
        return None

def get_recent_matchlist(api_key, puuid):
    try:
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?api_key={api_key}'
        response = requests.get(url)
        logger.debug(f"Matchlist URL: {url}")
        logger.debug(f"Matchlist Response: {response.status_code} - {response.json()}")

        if response.status_code == 200:
            matchlist = response.json()
            return matchlist
        else:
            return None
    except Exception as e:
        logger.error(f"Error in get_recent_matchlist: {e}")
        return None

def get_match_details(api_key, match_id):
    try:
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
        response = requests.get(url)
        logger.debug(f"Match Details URL: {url}")
        logger.debug(f"Match Details Response: {response.status_code} - {response.json()}")

        if response.status_code == 200:
            match_details = response.json()
            return match_details
        else:
            return None
    except Exception as e:
        logger.error(f"Error in get_match_details: {e}")
        return None

def calculate_troll_score(participant_stats, team_stats, match_details):
    kda = (participant_stats['kills'] + participant_stats['assists']) / (participant_stats['deaths'] or 1)
    cs = participant_stats['totalMinionsKilled'] + participant_stats.get('neutralMinionsKilled', 0)
    gold = participant_stats['goldEarned']
    damage = participant_stats['totalDamageDealtToChampions']
    vision_score = participant_stats.get('visionScore', 0)
    objective_score = participant_stats.get('dragonKills', 0) + participant_stats.get('baronKills', 0) + participant_stats.get('towerKills', 0)
    
    inappropriate_items = 0
    for item in range(0, 7):
        item_id = participant_stats.get(f'item{item}', 0)
        # 아이템 적합성 평가 로직 추가 필요

    avg_kda = sum([(p['kills'] + p['assists']) / (p['deaths'] or 1) for p in team_stats]) / len(team_stats)
    avg_cs = sum([p['totalMinionsKilled'] + p.get('neutralMinionsKilled', 0) for p in team_stats]) / len(team_stats)
    avg_gold = sum([p['goldEarned'] for p in team_stats]) / len(team_stats)
    avg_damage = sum([p['totalDamageDealtToChampions'] for p in team_stats]) / len(team_stats)
    avg_vision = sum([p.get('visionScore', 0) for p in team_stats]) / len(team_stats)
    avg_objectives = sum([p.get('dragonKills', 0) + p.get('baronKills', 0) + p.get('towerKills', 0) for p in team_stats]) / len(team_stats)

    score = 0
    if kda < avg_kda * 0.5:
        score += 15
    if cs < avg_cs * 0.5:
        score += 10
    if gold < avg_gold * 0.5:
        score += 15
    if damage < avg_damage * 0.5:
        score += 20
    if vision_score < avg_vision * 0.5:
        score += 10
    if objective_score < avg_objectives * 0.5:
        score += 20
    if inappropriate_items > 2:
        score += 20
    
    if participant_stats.get('timeSpentDead', 0) / match_details['info']['gameDuration'] > 0.3:
        score += 20

    return score

def troll_identifier(request):
    if request.method == 'POST':
        riot_id_tagline = request.POST.get('riot_id_tagline')
        if '#' in riot_id_tagline:
            riot_id, tag_line = riot_id_tagline.split('#', 1)
        else:
            message = "올바른 형식의 소환사 이름을 입력하세요. (예: 이름#태그)"
            return render(request, 'troll_result.html', {'message': message})
        
        api_key = settings.RIOT_API_KEY
        try:
            puuid = get_puuid(api_key, riot_id, tag_line)
            if not puuid:
                message = "Puuid를 가져올 수 없습니다."
                return render(request, 'troll_result.html', {'message': message})
            
            summoner_id = get_summoner_id(api_key, puuid)
            if not summoner_id:
                message = "Summoner ID를 가져올 수 없습니다."
                return render(request, 'troll_result.html', {'message': message})
            
            matchlist = get_recent_matchlist(api_key, puuid)
            if not matchlist:
                message = "매치 리스트를 가져올 수 없습니다."
                return render(request, 'troll_result.html', {'message': message})
            
            recent_match_id = matchlist[0]
            match_details = get_match_details(api_key, recent_match_id)
            participant_stats = next(p for p in match_details['info']['participants'] if p['summonerId'] == summoner_id)
            team_stats = [p for p in match_details['info']['participants'] if p['teamId'] == participant_stats['teamId']]
            troll_score = calculate_troll_score(participant_stats, team_stats, match_details)
            league_info = get_summoner_league_info(api_key, summoner_id)

            return render(request, 'troll_result.html', {
                'troll_score': troll_score,
                'summoner': [{
                    'summoner_name': riot_id_tagline,
                    'queue_type': league_info[0]['queueType'],
                    'tier_rank': f"{league_info[0]['tier']} {league_info[0]['rank']}",
                    'league_points': league_info[0]['leaguePoints'],
                    'total_games': league_info[0]['wins'] + league_info[0]['losses'],
                    'wins': league_info[0]['wins'],
                    'losses': league_info[0]['losses'],
                    'win_rate': (league_info[0]['wins'] / (league_info[0]['wins'] + league_info[0]['losses'])) * 100
                }]
            })
        except requests.exceptions.RequestException as e:
            error_message = f"API 요청 중 오류 발생: {e}"
            logger.error(error_message)
            return render(request, 'troll_result.html', {'error_message': error_message})
        except KeyError as e:
            error_message = f"응답 데이터에 필요한 키가 없습니다: {e}"
            logger.error(error_message)
            return render(request, 'troll_result.html', {'error_message': error_message})
    else:
        return render(request, 'troll_identifier_form.html')
