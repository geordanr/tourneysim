'''Simulator'''

import numpy as np

import constants
from player import Bye
from tournament import SwissTournament, PairingError

def main():
    num_iterations = 10000
    num_players = 32

    lost_first_round_skills = np.empty([num_iterations, num_players])
    lost_first_round_skills[:] = np.NAN
    lost_first_round_opp_skills = np.empty([num_iterations, num_players, num_players - 1])
    lost_first_round_opp_skills[:] = np.NAN

    lost_last_round_skills = np.empty([num_iterations, num_players])
    lost_last_round_skills[:] = np.NAN
    lost_last_round_opp_skills = np.empty([num_iterations, num_players, num_players - 1])
    lost_last_round_opp_skills[:] = np.NAN

    for i in range(num_iterations):
        try:
            t = SwissTournament(32).run()
        except PairingError:
            pass
        else:
            for j, player in enumerate(t.players):
                losses = len([r for r in player.record if r is constants.LOSS])
                if losses != 1:
                    continue

                opp_ary = None
                player_ary = None
                if player.record[0] == constants.LOSS:
                    opp_ary = lost_first_round_opp_skills
                    player_ary = lost_first_round_skills
                elif player.record[-1] == constants.LOSS:
                    opp_ary = lost_last_round_opp_skills
                    player_ary = lost_last_round_skills
                if opp_ary is None:
                    continue

                player_ary[i, j] = player.skill

                for k, opponent in enumerate(player.playedAgainst):
                    if opponent is not Bye:
                        opp_ary[i, j, k] = opponent.skill - player.skill

    print('=== Lost last round:')
    print('   Mean player skill: %f' % np.nanmean(lost_last_round_skills))
    print('              Stddev: %f' % np.nanstd(lost_last_round_skills))
    print('Mean opp. skill diff: %f' % np.nanmean(lost_last_round_opp_skills))
    print('              Stddev: %f' % np.nanstd(lost_last_round_opp_skills))

    print()

    print('=== Lost first round:')
    print('   Mean player skill: %f' % np.nanmean(lost_first_round_skills))
    print('              Stddev: %f' % np.nanstd(lost_first_round_skills))
    print('Mean opp. skill diff: %f' % np.nanmean(lost_first_round_opp_skills))
    print('              Stddev: %f' % np.nanstd(lost_first_round_opp_skills))

if __name__ == '__main__':
    main()
