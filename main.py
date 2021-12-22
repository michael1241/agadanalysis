#! /usr/bin/env python3

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# https://lichess.org/api/tournament/qzRBGPLN/games?moves=false for games file
# curl https://lichess.org/api/tournament/qzRBGPLN/games?moves=false -H "Authorization: Bearer <token>" -H "Accept: application/x-ndjson" > games.json


with open('games.json', 'r') as f:
    games = [json.loads(line) for line in f.readlines()]

players = {}

for game in games:
    black = game['players']['black']['user']['id']
    white = game['players']['white']['user']['id']
    for player in (black, white):
        if player not in players:
            players[player] = {'starts': [game['createdAt']], 'ends': [game['lastMoveAt']]}
        else:
            players[player]['starts'].append(game['createdAt'])
            players[player]['ends'].append(game['lastMoveAt'])


def zipTimeDiffs(player):
    waittimes = zip(player['ends'][:-1], player['starts'][1:])
    diffs = map(lambda x: (datetime.fromtimestamp(x[1] / 1000), (x[1] - x[0]) / 1000), waittimes)
    return diffs


points = []

for player in players.values():
    if len(player['starts']) < 15:
        continue
    player['starts'].sort()
    player['ends'].sort()
    points.extend(zipTimeDiffs(player))

plt.style.use('dark_background')
fig, ax = plt.subplots()
myFmt = mdates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(myFmt)
ax.set_ylabel('wait time / s')
ax.set_xlabel('time')
plt.scatter(*zip(*points), s=1, color='gold')
plt.show()
