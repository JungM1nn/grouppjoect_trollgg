# stats/views.py

from django.shortcuts import render
from .utils import (
    get_puuid, get_summoner_id, get_summoner_league_info,
    get_top_players, get_puuid_by_summoner_id,
    get_game_name_and_tagline_by_puuid, convert_queue
)

API_KEY = 'RGAPI-ec2d4574-f76b-4b72-8559-3fafa813329d'

def summoner_info(request):
    riot_id = 'WhyHealOnShen'
    tag_line = 'Mid'
    puuid = get_puuid(API_KEY, riot_id, tag_line)
    if puuid:
        summoner_id = get_summoner_id(API_KEY, puuid)
        if summoner_id:
            league_info = get_summoner_league_info(API_KEY, summoner_id)
            context = {
                'summoner_name': f"{riot_id}#{tag_line}",
                'league_info': league_info
            }
            return render(request, 'stats/summoner_info.html', context)
    return render(request, 'stats/error.html')

def top_players(request):
    queues = ['challengerleagues', 'grandmasterleagues', 'masterleagues']
    all_players = []
    league_priority = {'challengerleagues': 3, 'grandmasterleagues': 2, 'masterleagues': 1}

    for queue in queues:
        top_players, queue_type = get_top_players(API_KEY, queue)
        if top_players:
            all_players.extend([(player, queue_type) for player in top_players])

    sorted_players = sorted(
        all_players, key=lambda x: (league_priority.get(x[1], 0), x[0]['leaguePoints']), reverse=True)[:10]

    context = {'sorted_players': []}
    for idx, (player, queue_type) in enumerate(sorted_players, 1):
        summoner_id = player['summonerId']
        puuid = get_puuid_by_summoner_id(API_KEY, summoner_id)
        if puuid:
            game_name_and_tagline = get_game_name_and_tagline_by_puuid(API_KEY, puuid)
            if game_name_and_tagline:
                converted_queue = convert_queue(queue_type)
                context['sorted_players'].append({
                    'rank': idx,
                    'game_name_and_tagline': game_name_and_tagline,
                    'queue': converted_queue,
                    'league_points': player['leaguePoints'],
                    'wins': player['wins'],
                    'losses': player['losses'],
                    'win_rate': (player['wins'] / (player['wins'] + player['losses'])) * 100 if (player['wins'] + player['losses']) > 0 else 0
                })

    return render(request, 'stats/top_players.html', context)


from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to TROLL.GG!")
