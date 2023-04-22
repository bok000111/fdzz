import requests, webbrowser, os, browser_cookie3
from datetime import datetime, timedelta
from parse import compile
from time import sleep
from bs4 import BeautifulSoup as bs
import asyncio

PROJECT_URL = 'https://projects.intra.42.fr/'
FORMAT = '%Y-%m-%dT%H:%M:%S.000+09:00'
cookies = browser_cookie3.safari(domain_name='.intra.42.fr')

def notify(title, text):
	os.system(f'afplay /System/Library/Sounds/Sosumi.aiff')
	os.system(f"""osascript -e 'display notification "{text}" with title "{title}"'""")

async def get_projects():
    parser = compile('/{slug}/{id}')
    req = requests.get(PROJECT_URL, cookies=cookies)
    try:
        req.raise_for_status()
    except:
        notify('invalid cookie', 'invalid session cookie in safari')
        webbrowser.open(f"https://signin.intra.42.fr/users/sign_in")
        exit(1)
    soup = bs(req.text, 'html.parser')
    need_eval = []
    for project in soup.find_all('a', {'class': 'simple-link col-lg-3 col-sm-4 col-xs-6'}):
        if project.find('small') and project.find('small').text == 'Evaluation needed':
            tmp = parser.parse(project['href']).named
            tmp['name'] = next(filter(len, project.text.split('\n')))
            need_eval.append(tmp)
    return need_eval

async def get_team_id(target):
    req = requests.get(f"{PROJECT_URL}/{target['slug']}/{target['id']}", cookies=cookies)
    try:
        req.raise_for_status()
    except:
        notify('invalid cookie', 'invalid session cookie in safari')
        webbrowser.open(f"https://signin.intra.42.fr/users/sign_in")
        exit(1)
    soup = bs(req.text, 'html.parser')
    team = soup.find('a', class_ = 'btn btn-primary btn-block')
    team_id_parser = compile('/projects/{slug}/slots?team_id={team_id}')
    return team_id_parser.parse(team['href']).named['team_id']

async def find_slot(target, start, end):
    REQUEST_URL = f"https://projects.intra.42.fr/projects/{target['slug']}/slots.json?team_id={target['team_id']}&start={start.strftime(FORMAT)}&end={end.strftime(FORMAT)}"
    MINE_URL = f"https://projects.intra.42.fr/{target['slug']}/mine"

    while True:
        res = requests.get(REQUEST_URL, cookies=cookies)
        try:
            res.raise_for_status()
        except:
            notify('invalid cookie', 'invalid session cookie in safari')
            webbrowser.open(f"https://signin.intra.42.fr/users/sign_in")
            exit(1)
        slots = res.json()
        if len(slots) > 0:
            print(*slots, sep='\n')
            slots = [{'start': f"{x['start'][5:10]}_{x['start'][11:16]}", 'end': f"{x['end'][5:10]}_{x['end'][11:16]}"} for x in slots if x['title'] == 'Available']
            slots.sort(key=lambda x: x['start'])
            notify('availobla slot', f"start: {slots[0]['start']}\nend: {slots[0]['end']}")
            webbrowser.open(f"https://projects.intra.42.fr/projects/{target['slug']}/slots?team_id={target['team_id']}")
            sleep(10)
        else:
            print(f'''Searching {target['slug']} slots for {(datetime.today() - start).seconds} seconds...''')
        if datetime.today() > end:
            exit(0)

async def main():
    future = get_projects()
    while True:
        try:
            offset = int(input('offset: '))
        except:
            print('invalid input')
        else:
            break
    need_eval = await future
    for i, project in enumerate(need_eval):
        print(f"{i}: {project['name']}")
    while True:
        try:
            target = need_eval[int(input('target: '))]
        except:
            print('invalid input')
        else:
            break
    future = get_team_id(target)
    start = datetime.today()
    end = datetime.today() + timedelta(hours=offset)
    target['team_id'] = await future
    await find_slot(target, start, end)

asyncio.run(main())
