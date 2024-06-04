from django.shortcuts import render
from .forms import SummonerSearchForm
import requests
from urllib.parse import quote
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_api_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"An error occurred: {err}")
    return None

def get_puuid(api_key, riot_id, tag_line):
    encoded_riot_id = quote(riot_id)
    encoded_tag_line = quote(tag_line)
    url_puuid = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_riot_id}/{encoded_tag_line}?api_key={api_key}"
    return get_api_response(url_puuid)

def get_summoner_id(api_key, puuid):
    url_summoner = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
    return get_api_response(url_summoner)

def get_summoner_league_info(api_key, summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}"
    return get_api_response(url)

def home(request):
    error_message = None
    if request.method == 'POST':
        form = SummonerSearchForm(request.POST)
        if form.is_valid():
            riot_id_tagline = form.cleaned_data['riot_id_tagline']
            if '#' in riot_id_tagline:
                riot_id, tag_line = riot_id_tagline.split('#', 1)
                api_key = settings.RIOT_API_KEY
                puuid_response = get_puuid(api_key, riot_id, tag_line)
                if puuid_response and 'puuid' in puuid_response:
                    puuid = puuid_response['puuid']
                    summoner_response = get_summoner_id(api_key, puuid)
                    if summoner_response and 'id' in summoner_response:
                        summoner_id = summoner_response['id']
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
                    else:
                        error_message = "소환사를 찾을 수 없습니다."
                else:
                    error_message = "PUUID를 찾을 수 없습니다. # 뒤를 다시 확인해주세요."
            else:
                error_message = "잘못된 형식의 소환사 이름입니다."
        else:
            error_message = "폼이 유효하지 않습니다."
    else:
        form = SummonerSearchForm()
    
    if error_message:
        return render(request, 'summoner/error.html', {'error_message': error_message})
    
    return render(request, 'summoner/home.html', {'form': form})

def summoner(request):
    # 소환사 검색 결과를 처리하는 로직을 추가
    return render(request, 'summoner/summoner.html')
