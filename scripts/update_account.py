"""Generate a public-only, dependency-free SVG account record."""
import json, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from html import escape

USER = 'Knownassa'
OUT = Path(__file__).resolve().parents[1] / 'assets' / 'account.svg'

def api(path):
    request = urllib.request.Request('https://api.github.com' + path, headers={
        'Accept': 'application/vnd.github+json', 'User-Agent': 'Knownassa-public-profile',
        'X-GitHub-Api-Version': '2022-11-28',
    })
    # No authentication: only information available to the public is fetched.
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def render(values):
    items = [('ACCOUNT AGE',values[0]),('PUBLIC REPOS',values[1]),('FOLLOWERS',values[2]),('STARS RECEIVED',values[3])]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 112" role="img" aria-label="Public account metrics"><rect width="900" height="112" fill="#242322"/><path d="M0 4H900" stroke="#aa5848" stroke-width="4"/>']
    for i,(label,val) in enumerate(items):
        x=22+i*225
        if i: parts.append(f'<path d="M{x-12} 20V92" stroke="#57534e"/>')
        parts.append(f'<text x="{x}" y="36" fill="#c6bfb3" font-family="monospace" font-size="12" letter-spacing="1">{label}</text><text x="{x}" y="76" fill="#f2ede3" font-family="Georgia,serif" font-size="29">{escape(str(val))}</text>')
    parts.append('</svg>')
    OUT.write_text(''.join(parts)+'\n', encoding='utf-8')

def main():
    profile=api(f'/users/{USER}')
    created=datetime.fromisoformat(profile['created_at'].replace('Z','+00:00'))
    now=datetime.now(timezone.utc)
    years=now.year-created.year-((now.month,now.day)<(created.month,created.day))
    stars=0
    page=1
    while True:
        repos=api(f'/users/{USER}/repos?type=owner&per_page=100&page={page}')
        stars+=sum(r['stargazers_count'] for r in repos if not r['private'])
        if len(repos)<100: break
        page+=1
    render([f'{years} years',profile['public_repos'],profile['followers'],stars])

if __name__=='__main__': main()
