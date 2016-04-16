'''Random pairing simulation'''
import math

import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt
import numpy as np

from tournament import RandomTournament, PairingError

def main():
    RandomTournament.performance_sigma = 2

    num_iterations = 1000
    num_players = 64

    tournament_points = np.empty([num_iterations, num_players])
    tournament_points[:] = np.NAN

    for i in range(num_iterations):
        try:
            t = RandomTournament(num_players, math.ceil(math.log(num_players, 2))).run()
        except PairingError:
            pass
        else:
            for j, player in enumerate(sorted(t.players, key=lambda p: p.skill, reverse=True)):
                tournament_points[i, j] = player.tournamentPoints

    means = np.nanmean(tournament_points, axis=0)
    error = 2 * np.nanstd(tournament_points, axis=0)

    plt.errorbar(range(num_players), means, yerr=error)
    plt.title('Random Pairing, sigma=%f' % RandomTournament.performance_sigma)
    plt.xlabel('Player (sorted by skill)')
    plt.ylabel('Tournament points')
    plt.savefig('random_%s' % str(RandomTournament.performance_sigma).replace('.', '_'))

if __name__ == '__main__':
    main()
