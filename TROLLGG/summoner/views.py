# summoner/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .forms import SummonerSearchForm
import requests
from urllib.parse import quote
from django.conf import settings
from .riot_api import RiotAPI

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



from django.conf import settings

def home(request):
    if request.method == 'POST':
        form = SummonerSearchForm(request.POST)
        if form.is_valid():
            riot_id = form.cleaned_data['riot_id']
            tag_line = form.cleaned_data['tag_line']
            api_key = settings.RIOT_API_KEY
            puuid = get_puuid(api_key, riot_id, tag_line)  # RiotAPI 클래스 대신에 get_puuid 함수 사용
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
