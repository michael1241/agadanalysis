#! /usr/bin/env python3

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from dateutil import tz
from collections import defaultdict

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
    diffs = map(lambda x: (datetime.fromtimestamp(x[1] / 1000, tz=tz.tzutc()), (x[1] - x[0]) / 1000), waittimes)
    return diffs


points = []
ends = []
set_ends = set()
d_ends = defaultdict(int)

for player in players.values():
    player['starts'].sort()
    player['ends'].sort()
    if len(player['starts']) >= 15:
        points.extend(zipTimeDiffs(player))
    end = datetime.fromtimestamp(player['ends'][-1] // 60000 * 60, tz=tz.tzutc())  # 1min step
    ends.append(end)
    set_ends.add(end)
    d_end = datetime.fromtimestamp(player['ends'][-1] // 6000 * 6, tz=tz.tzutc())  # 6s step
    d_ends[d_end] += 1

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(24, 10), dpi=80)
myFmt = mdates.DateFormatter('%H:%M', tz=tz.tzutc())
ax.xaxis.set_major_formatter(myFmt)
ax.set_ylabel('wait time / s')
ax.set_xlabel('time')
plt.scatter(*zip(*points), s=1, color='gold')
plt.show(block=True)

bins = sorted(set_ends)
bins.append(bins[-1] + timedelta(seconds=60))
myLoc = mdates.MinuteLocator(byminute=range(0, 60, 5))
fig_hist, ax_hist = plt.subplots(figsize=(24, 10), dpi=80)
ax_hist.hist(ends, bins=bins, color='gold')
ax_hist.xaxis.set_major_formatter(myFmt)
ax_hist.xaxis.set_major_locator(myLoc)
ax_hist.set_ylabel('end frequency')
ax_hist.set_xlabel('time')
plt.show(block=True)

fig_end, ax_end = plt.subplots(figsize=(24, 10), dpi=80)
ax_end.xaxis.set_major_formatter(myFmt)
ax_end.set_ylabel('end frequency')
ax_end.set_xlabel('time')
plt.scatter(d_ends.keys(), d_ends.values(), s=1, color='gold')
plt.ylim(bottom=0)
plt.show(block=True)
