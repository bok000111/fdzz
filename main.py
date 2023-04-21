import requests, webbrowser, os, browser_cookie3
from datetime import datetime, timedelta
from parse import compile
from time import sleep

def notify(title, text):
	os.system(f'afplay /System/Library/Sounds/Sosumi.aiff')
	os.system(f"""osascript -e 'display notification "{text}" with title "{title}"'""")

if __name__ != "__main__":
	exit(0)

slot_parser = compile('https://projects.intra.42.fr/projects/{}/slots?team_id={}')
while True:
	try:
		slug, team_id = slot_parser.parse(input('slot url: '))
	except:
		print('https://projects.intra.42.fr/projects/{slug}/slots?team_id={team_id}')
	else:
		break
while True:
	try:
		offset = int(input('offset: '))
	except:
		print('invalid input')
	else:
		break
cookies = browser_cookie3.safari(domain_name='.intra.42.fr')
start = datetime.today()
end = datetime.today() + timedelta(hours=offset)

FORMAT = '%Y-%m-%dT%H:%M:%S.000+09:00'
REQUEST_URL = f"https://projects.intra.42.fr/projects/{slug}/slots.json?team_id={team_id}&start={start.strftime(FORMAT)}&end={end.strftime(FORMAT)}"

while True:
	res = requests.get(REQUEST_URL, cookies=cookies)
	try:
		res.raise_for_status()
	except:
		notify('invalid cookie', 'no session cookie in safari')
		webbrowser.open(f"https://signin.intra.42.fr/users/sign_in")
		input()
	slots = res.json()
	if len(slots) > 0:
		slots = [{'start': f"{x['start'][5:10]}_{x['start'][11:16]}", 'end': f"{x['end'][5:10]}_{x['end'][11:16]}"} for x in slots if x['title'] == 'Available']
		slots.sort(key=lambda x: x['start'])
		notify('availobla slot', f"start: {slots[0]['start']}\nend: {slots[0]['end']}")
		webbrowser.open(f"https://projects.intra.42.fr/projects/{slug}/slots?team_id={team_id}")
		sleep(10)
	else:
		print(f'''Searching {slug} slots for {(datetime.today() - start).seconds} seconds...''')
	if datetime.today() > end:
		exit(0)
