import requests
from urllib.parse import quote

# Riot API 키
API_KEY = 'RGAPI-ec2d4574-f76b-4b72-8559-3fafa813329d'

# Riot ID와 태그 라인
riot_id = 'WhyHealOnShen'
tag_line = 'Mid'


def get_puuid(riot_id, tag_line):
    # Riot ID와 태그 라인을 URL 인코딩
    encoded_riot_id = quote(riot_id)
    encoded_tag_line = quote(tag_line)

    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{
        encoded_riot_id}/{encoded_tag_line}?api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        return data['puuid']
    else:
        print("Error fetching PUUID:", data)
        return None


def get_match_ids(puuid, start, count):
    url = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{
        puuid}/ids'
    params = {
        'start': start,
        'count': count
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching match IDs:", response.json())
        return []


def main():
    # PUUID 얻기
    puuid = get_puuid(riot_id, tag_line)
    if not puuid:
        return

    count = 10
    start = 0

    while True:
        match_ids = get_match_ids(puuid, start, count)
        if match_ids:
            for match_id in match_ids:
                print(match_id)
            start += len(match_ids)
            if len(match_ids) < count:
                print("No more matches left.")
                break
        else:
            print("No more matches found.")
            break

        user_input = input(
            "Enter 'more' to see more matches, or 'exit' to quit: ").strip().lower()
        if user_input != 'more':
            break


if __name__ == "__main__":
    main()
