'''Tournament'''
from collections import defaultdict
import itertools
import logging
import math
import random
# import time

from player import Player, Bye

logging.basicConfig()

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)

class Tournament(object):
    performance_sigma = 0.7

    def __init__(self, num_players, num_rounds):
        self.num_players = num_players
        self.num_rounds = num_rounds
        self.players = []
        self.elimination = False
        self.elim_bracket = []

        for i in range(self.num_players):
            self.players.append(Player.makeRandomPlayer('Player %d' % (i + 1)))

    def run(self):
        for r in range(self.num_rounds):
            log.debug('<<< Round %d of %d', r + 1, self.num_rounds)
            for pairing in self.determinePairings(r):
                pairing[0].play(pairing[1], scale=self.performance_sigma, elimination=self.elimination, elim_rank=len(self.elim_bracket) * 2)
            log.debug('>>> End of round %d of %d', r + 1, self.num_rounds)

        return self

    def showRankings(self):
        for player in self.ranked:
            print(player)

        return self

    def cut(self, n):
        return self.ranked[:n]

    @property
    def ranked(self):
        return sorted(self.players, key=lambda p: (-p.elimRank, p.tournamentPoints, p.mov), reverse=True)

    def determinePairings(self, r):
        '''
            :param r: Round to do pairings in
            :type r: int
            :returns: List of pairings
            :rtype: list(tuple(Player, Player))
        '''
        raise NotImplementedError('Base class')

class RandomTournament(Tournament):
    def determinePairings(self, r):
        # Try randomly pairing until we succeed
        pairs = list(self.players)
        if len(pairs) % 2 != 0:
            pairs.append(Bye)
        for _ in range(len(self.players) ** 2):
            random.shuffle(pairs)
            if validatePairings(pairs):
                break
        else:
            raise PairingError(self.players)

        return zip(pairs[::2], pairs[1::2])

class SwissTournament(Tournament):
    def __init__(self, num_players):
        if num_players < 9:
            num_rounds = 3
        elif num_players < 25:
            num_rounds = 4
        elif num_players < 41:
            num_rounds = 5
        elif num_players < 289:
            num_rounds = 6
        elif num_players < 513:
            num_rounds = 7
        else:
            num_rounds = 8

        super(SwissTournament, self).__init__(num_players, num_rounds)

    def determinePairings(self, r):
        if r == 0:
            # first round, random pair
            pairs = list(self.players)
            if len(pairs) % 2 != 0:
                pairs.append(Bye)
            random.shuffle(pairs)
            return zip(pairs[::2], pairs[1::2])

        else:
            for _ in range(1000):
                pairs = []

                # group by tournament points
                points_to_players = defaultdict(list)
                for player in self.players:
                    points_to_players[player.tournamentPoints].append(player)

                pair_down = None
                for points in sorted(points_to_players.keys(), reverse=True):
                    players = points_to_players[points]
                    if pair_down is not None:
                        # choose randomly from this tier to pair with the paired down player
                        rando = random.choice(players)
                        players.remove(rando)
                        pairs.extend([pair_down, rando])
                        pair_down = None

                    # if odd number, pair down a random player
                    if len(players) % 2 != 0:
                        pair_down = random.choice(players)
                        players.remove(pair_down)

                    # pair randomly within this tier
                    random.shuffle(players)
                    pairs.extend(players)

                if pair_down is not None:
                    pairs.extend([pair_down, Bye])

                if validatePairings(pairs):
                    return zip(pairs[::2], pairs[1::2])

            raise PairingError(self.players)

class SingleEliminationTournament(Tournament):
    def __init__(self, players):
        '''
            :param players: List of players in the bracket, sorted in descending order (top seed is index 0)
        '''
        players = list(players)
        if len(players) % 2 != 0:
            players.append(Bye)
        super(SingleEliminationTournament, self).__init__(0, math.ceil(math.log(len(players), 2)))
        self.players = players
        self._makeBracket(list(itertools.chain.from_iterable(zip(players, [Bye]*len(players)))))

    def determinePairings(self, r):
        self.elimination = True
        self._makeBracket([[p for p in player if not p.knockedOut and p is not Bye][0] for player in self.elim_bracket])
        return self.elim_bracket

    def _makeBracket(self, players):
        size = math.ceil(math.log(len(players), 2))
        if len(players) != size:
            # Give byes to the top players
            players += [Bye] * (size - len(players))
        self.elim_bracket = list(zip(players[:int(len(players)/2)], reversed(players[int(len(players)/2):])))

def validatePairings(pairs):
    assert len(pairs) % 2 == 0

    for p1, p2 in zip(pairs[::2], pairs[1::2]):
        if p1 in p2.playedAgainst or p2 in p1.playedAgainst:
            return False

    return True

class PairingError(Exception):
    def __init__(self, players):
        super(PairingError, self).__init__('Pairing error')
        self.players = players

def main():
    # RandomTournament(11, 3).run().showRankings()
    SingleEliminationTournament(SwissTournament(16).run().showRankings().cut(8)).run().showRankings()

    # num_iter = 1000
    # failures = 0
    # t0 = time.time()
    # for _ in range(num_iter):
    #     try:
    #         SwissTournament(64, 6, 8).run()
    #     except:
    #         failures += 1
    # print('%2.2f ms (%d failures)' % (1000 * (time.time() - t0) / num_iter, failures))

if __name__ == '__main__':
    main()
