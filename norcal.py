'''Trueskill analysis of Norcal results'''
import argparse
from collections import defaultdict
import csv

import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt
import numpy as np
from trueskill import TrueSkill, Rating, rate_1vs1

def parseArgs(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('misspelled', type=str, action='store', help='Path to misspelling mapping CSV')
    parser.add_argument('record', type=str, action='store', help='Path to match record CSV')

    return parser.parse_args(argv)

def loadMisspellings(csv_path):
    mapping = {}
    with open(csv_path, 'r') as f:
        r = csv.reader(f)
        for i, row in enumerate(r):
            if i == 0:
                # header
                continue
            mapping[row[0]] = row[1]
    return mapping

def main():
    TrueSkill(backend='scipy')
    args = parseArgs()
    misspelled = loadMisspellings(args.misspelled)

    # map player name to rating object
    players = defaultdict(Rating)
    with open(args.record, 'r') as f:
        r = csv.reader(f)
        for i, row in enumerate(r):
            if i == 0:
                # header
                continue
            winner, loser, wasDraw = row
            wasDraw = bool(wasDraw)
            winner = misspelled.get(winner, winner).lower()
            loser = misspelled.get(loser, loser).lower()

            w_new, l_new = rate_1vs1(players[winner], players[loser])
            players[winner] = w_new
            players[loser] = l_new

    # for p in sorted(players.items(), key=lambda p: (-p[1].mu, p[1].sigma)):
    for p in sorted(players.items(), key=lambda p: (p[1].mu - (3* p[1].sigma)), reverse=True):
        print(p, p[1].mu - (3 * p[1].sigma))

    ratings = players.values()
    mus = np.asarray([r.mu for r in ratings])
    sigmas = np.asarray([r.sigma for r in ratings])

    coeffs = np.polyfit(mus, sigmas, 2)
    xp = np.linspace(np.min(mus), np.max(mus), 100)
    plt.plot(xp, np.poly1d(coeffs)(xp))
    plt.scatter(mus, sigmas)
    plt.title('NorCal Store Champs 2016 TrueSkill')
    plt.xlabel('Player skill')
    plt.ylabel('Skill confidence')
    plt.savefig('trueskill')

if __name__ == '__main__':
    main()
