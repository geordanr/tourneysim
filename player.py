'''Tournament player'''
import hashlib
import logging
import random

import numpy as np

import constants

logging.basicConfig()

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)

class Player(object):
    def __init__(self, skill, name=None):
        '''
            :param skill: Number of sigma, positive or negative, from average
        '''
        self.skill = skill
        self.mov = 0
        self.playedAgainst = set()
        self.record = []
        self.knockedOut = False
        self.elimRank = 999
        if name is None:
            self.name = hashlib.md5(str(id(self)).encode('utf8')).hexdigest()[:8]
        else:
            self.name = name

    def __str__(self):
        return '<Player "%s" skill=%2.2f rank=%d points=%d mov=%d>' % (self.name, self.skill, self.elimRank, self.tournamentPoints, self.mov)

    @classmethod
    def makeRandomPlayer(cls, name=None):
        return cls(np.random.normal(), name=name)

    @property
    def tournamentPoints(self):
        return sum(self.record)

    def play(self, other, scale=None, elimination=False, elim_rank=None):
        '''Play a game against the other player and record the results in both.'''
        if not elimination and (self in other.playedAgainst or other in self.playedAgainst):
            if other is Bye:
                raise ValueError("Already had a bye")
            else:
                raise ValueError("Already played against %s" % other)

        self.playedAgainst.add(other)
        other.playedAgainst.add(self)

        if other is Bye:
            log.debug('%s has a bye', self)
            self.mov += constants.BYE_MOV
            self.record.append(constants.FULL_WIN)
            return

        winner = _determineMatchWinner(self, other, scale)
        loser = other if self is winner else self
        winner_points, loser_points = _determineMatchPoints()

        diff = winner_points - loser_points

        winner.mov += 100 + diff
        loser.mov += 100 - diff

        if winner_points != loser_points:
            loser.record.append(constants.LOSS)
            if elimination:
                loser.knockedOut = True
                loser.elimRank = elim_rank
                winner.elimRank = elim_rank / 2
            if winner_points - loser_points >= constants.MOD_WIN_DIFF:
                winner.record.append(constants.FULL_WIN)
            else:
                loser.record.append(constants.MODIFIED_WIN)
        else:
            if elimination:
                # randomly choose who had init
                players = [self, other]
                random.shuffle(players)
                players[0].knockedOut = True
                players[0].elimRank = elim_rank
                players[1].record.append(constants.FULL_WIN)
                players[1].elimRank = elim_rank / 2
            else:
                self.record.append(constants.DRAW)

        log.debug('%s defeats %s: score %d - %d', winner, loser, winner_points, loser_points)
        if elimination:
            log.debug('...%s is knocked out!', loser)

class ByePlayer(Player):
    def __init__(self):
        super(ByePlayer, self).__init__(float('-Inf'))

    def __str__(self):
        return '<Bye>'

    def play(self, other, scale=None, elimination=False, elim_rank=None):
        if other is Bye:
            return
        self.playedAgainst.add(other)
        other.playedAgainst.add(self)
        other.mov += constants.BYE_MOV
        other.record.append(constants.FULL_WIN)

Bye = ByePlayer()

def _determineMatchWinner(p1, p2, scale=None):
    if scale is None:
        scale = 0.7
    p1_performance = np.random.normal(p1.skill, scale=scale)
    p2_performance = np.random.normal(p2.skill, scale=scale)

    if p1_performance > p2_performance:
        return p1
    else:
        return p2

def _determineMatchPoints():
    '''
        :returns: tuple(winner points, loser points)
    '''
    return tuple(sorted([
        max(10, min(100, np.random.normal(constants.WINNER_POINTS_AVG, constants.WINNER_POINTS_STD))),
        max(0, min(100, np.random.normal(constants.LOSER_POINTS_AVG, constants.LOSER_POINTS_STD))),
    ], reverse=True))
