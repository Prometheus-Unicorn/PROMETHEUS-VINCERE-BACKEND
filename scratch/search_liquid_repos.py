import urllib.request
import json

queries = ['liquid+image+webgl', 'liquid-image', 'liquid+distortion+image']
for q in queries:
    try:
        url = f'https://api.github.com/search/repositories?q={q}&sort=stars&order=desc'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f'=== Query: {q} ===')
            for item in data.get('items', [])[:6]:
                name = item['full_name']
                stars = item['stargazers_count']
                desc = item.get('description', '')
                print(f'{name} ({stars} stars): {desc}')
    except Exception as e:
        print('Error:', e)
