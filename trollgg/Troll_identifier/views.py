# views.py
from django.shortcuts import render
from summoner.forms import SummonerSearchForm
import requests
from urllib.parse import quote
from django.conf import settings

def get_puuid(api_key, riot_id, tag_line):
    encoded_riot_id = quote(riot_id)
    encoded_tag_line = quote(tag_line)
    url_puuid = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_riot_id}/{encoded_tag_line}?api_key={api_key}"
    response_puuid = requests.get(url_puuid)

    if response_puuid.status_code == 200:
        data_puuid = response_puuid.json()
        puuid = data_puuid['puuid']
        return puuid
    else:
        return None

def get_summoner_id(api_key, puuid):
    url_summoner = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
    response_summoner = requests.get(url_summoner)

    if response_summoner.status_code == 200:
        summoner_data = response_summoner.json()
        summoner_id = summoner_data['id']
        return summoner_id
    else:
        return None

def get_summoner_league_info(api_key, summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        league_info = response.json()
        return league_info
    else:
        return None

def home(request):
    if request.method == 'POST':
        form = SummonerSearchForm(request.POST)
        if form.is_valid():
            riot_id_tagline = form.cleaned_data['riot_id_tagline']
            if '#' in riot_id_tagline:
                riot_id, tag_line = riot_id_tagline.split('#', 1)
                api_key = settings.RIOT_API_KEY
                puuid = get_puuid(api_key, riot_id, tag_line)
                if puuid:
                    summoner_id = get_summoner_id(api_key, puuid)
                    if summoner_id:
                        summoner_league_info = get_summoner_league_info(api_key, summoner_id)
                        if summoner_league_info:
                            summoner_info = []
                            for entry in summoner_league_info:
                                queue_type = entry['queueType']
                                tier = entry['tier']
                                division = entry['rank']
                                league_points = entry['leaguePoints']
                                wins = entry['wins']
                                losses = entry['losses']

                                total_games = wins + losses
                                win_rate = (wins / total_games) * 100 if total_games > 0 else 0
                                tier_rank = f"{tier} {division}"

                                if queue_type == 'RANKED_SOLO_5x5':
                                    queue_type = '솔로랭크 5x5'
                                elif queue_type == 'RANKED_FLEX_SR':
                                    queue_type = '자유랭크 5x5'

                                summoner_name = f"{riot_id}#{tag_line}"

                                summoner_info.append({
                                    'summoner_name': summoner_name,
                                    'queue_type': queue_type,
                                    'tier_rank': tier_rank,
                                    'league_points': league_points,
                                    'total_games': total_games,
                                    'wins': wins,
                                    'losses': losses,
                                    'win_rate': win_rate
                                })
                            if summoner_info:
                                return render(request, 'summoner/detail.html', {'summoner': summoner_info})
            error_message = "검색 결과가 없습니다."
            return render(request, 'summoner/error.html', {'error_message': error_message})
    else:
        form = SummonerSearchForm()
    return render(request, 'summoner/home.html', {'form': form})



def get_recent_matchlist(api_key, summoner_id):
    url = f'https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}?api_key={api_key}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    response.raise_for_status()
    return response.json().get('matches', [])

def get_match_details(api_key, match_id):
    url = f'https://kr.api.riotgames.com/lol/match/v4/matches/{match_id}?api_key={api_key}'
    response = requests.get(url, headers={'X-Riot-Token': api_key})
    response.raise_for_status()
    return response.json()

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
    
    if participant_stats.get('timeSpentDead', 0) / match_details['gameDuration'] > 0.3:
        score += 20

    return score

def troll_identifier(request):
    if request.method == 'POST':
        summoner_name = request.POST.get('summoner_name')
        api_key = settings.RIOT_API_KEY
        try:
            summoner_id = get_summoner_id(api_key, summoner_name)
            matchlist = get_recent_matchlist(api_key, summoner_id)
            if not matchlist:
                message = "매치 리스트를 가져올 수 없습니다."
                return render(request, 'troll_result.html', {'message': message})
            recent_match_id = matchlist[0]['gameId']
            match_details = get_match_details(api_key, recent_match_id)
            participant_id = next(p['participantId'] for p in match_details['participantIdentities'] if p['player']['summonerId'] == summoner_id)
            participant_stats = next(p['stats'] for p in match_details['participants'] if p['participantId'] == participant_id)
            team_stats = [p['stats'] for p in match_details['participants'] if p['teamId'] == participant_stats['teamId']]
            troll_score = calculate_troll_score(participant_stats, team_stats, match_details)
            if troll_score >= 50:
                result_message = f"{summoner_name} 님은 트롤일 가능성이 높습니다."
            else:
                result_message = f"{summoner_name} 님은 트롤이 아닙니다."
            return render(request, 'troll_result.html', {'result_message': result_message})
        except requests.exceptions.RequestException as e:
            error_message = f"API 요청 중 오류 발생: {e}"
            return render(request, 'troll_result.html', {'error_message': error_message})
        except KeyError as e:
            error_message = f"응답 데이터에 필요한 키가 없습니다: {e}"
            return render(request, 'troll_result.html', {'error_message': error_message})
    else:
        return render(request, 'troll_identifier_form.html')

