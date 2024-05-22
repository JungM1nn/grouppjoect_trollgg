import requests
from urllib.parse import quote

api_key = 'RGAPI-ec2d4574-f76b-4b72-8559-3fafa813329d'
riot_id = '이상호93'  # 또는 한글이 포함된 Riot ID
tag_line = '1109'  # 또는 한글이 포함된 태그 라인

# Riot ID와 태그 라인을 인코딩
encoded_riot_id = quote(riot_id)
encoded_tag_line = quote(tag_line)

url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{
    encoded_riot_id}/{encoded_tag_line}?api_key={api_key}"

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    puuid = data['puuid']
    print("PUUID:", puuid)
else:
    print("Error:", data)