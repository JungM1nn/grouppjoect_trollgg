import matplotlib.pyplot as plt
from django.shortcuts import render
from django.http import HttpResponse
from .utils import RiotAPI

API_KEY = 'RGAPI-df48d957-9865-4eab-b605-1a5abd4e08bd'
riot_api = RiotAPI(API_KEY)

def summoner_info(request):
    riot_id = 'WhyHealOnShen'
    tag_line = 'Mid'
    puuid = riot_api.get_puuid(riot_id, tag_line)
    if puuid:
        summoner_id = riot_api.get_summoner_id(puuid)
        if summoner_id:
            league_info = riot_api.get_summoner_league_info(summoner_id)
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
        top_players, queue_type = riot_api.get_top_players(queue)
        if top_players:
            all_players.extend([(player, queue_type) for player in top_players])
    sorted_players = sorted(
        all_players, key=lambda x: (league_priority.get(x[1], 0), x[0]['leaguePoints']), reverse=True)[:10]
    context = {'sorted_players': []}
    for idx, (player, queue_type) in enumerate(sorted_players, 1):
        summoner_id = player['summonerId']
        puuid = riot_api.get_puuid_by_summoner_id(summoner_id)
        if puuid:
            game_name_and_tagline = riot_api.get_game_name_and_tagline_by_puuid(puuid)
            if game_name_and_tagline:
                converted_queue = RiotAPI.convert_queue(queue_type)
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

def home(request):
    return HttpResponse("Welcome to TROLL.GG!")

# 티어 그래프

def plot_tier_graph(summoner_name, league_info):
    tiers = []
    points = []

    for entry in league_info:
        tier = entry['tier']
        points.append(entry['leaguePoints'])
        tiers.append(f"{tier} {entry['rank']}")

    plt.figure(figsize=(10, 6))
    plt.bar(tiers, points, color='blue')
    plt.xlabel('Tiers')
    plt.ylabel('League Points')
    plt.title(f'League Points by Tier for {summoner_name}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 그래프 이미지를 메모리에 저장하고 이를 HttpResponse로 반환
    import io
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def summoner_tier_graph(request, summoner_name):
    puuid = riot_api.get_puuid(summoner_name, 'YOUR_TAGLINE')
    if puuid:
        summoner_id = riot_api.get_summoner_id(puuid)
        if summoner_id:
            league_info = riot_api.get_summoner_league_info(summoner_id)
            if league_info:
                buf = plot_tier_graph(summoner_name, league_info)
                return HttpResponse(buf, content_type='image/png')
    return HttpResponse("Error retrieving summoner tier information")
