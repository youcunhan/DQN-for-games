# -*- coding: utf-8 -*-
import numpy as np
import tensorflow as tf

MOVE_LEFT = 0
MOVE_RIGHT = 1
TURN_LEFT = 2
TURN_RIGHT = 3

ATTACK = 0
ATTACK_UP = 1
SHORT_JUMP = 2
MID_JUMP = 3
SKILL_UP = 4
SKILL_DOWN = 5
RUSH = 6
CURE = 7


class Agent:
    def __init__(self,act_dim,algorithm,e_greed=0.1,e_greed_decrement=0):
        self.act_dim = act_dim
        self.algorithm = algorithm
        self.e_greed = e_greed
        self.e_greed_decrement = e_greed_decrement


    def sample(self, station, soul, boss_x, boss_y, player_x, skill):

        pred_move, pred_act = self.algorithm.model.predict(station)
        # print(pred_move)
        # print(self.e_greed)
        pred_move = pred_move.numpy()
        pred_act = pred_act.numpy()
        sample = np.random.rand()
        if sample < self.e_greed:

            move = self.better_move(boss_x, player_x, skill)
        else:
            move = np.argmax(pred_move)
        self.e_greed = max(0.03, self.e_greed - self.e_greed_decrement)
        sample = np.random.rand()
        if sample < self.e_greed:
            act = self.better_action(soul, boss_x, boss_y, player_x, skill)
        else:
            act = np.argmax(pred_act)
            if soul < 33:
                if act == 4 or act == 5:
                    pred_act[0][4] = -30
                    pred_act[0][5] = -30
            act = np.argmax(pred_act)

        self.e_greed = max(
            0.03, self.e_greed - self.e_greed_decrement)
        return move, act

    def better_move(self, boss_x, player_x, skill):
        dis = abs(player_x - boss_x)
        dire = player_x - boss_x
        if skill:
            # run away while distance < 6
            if dis < 6:
                if dire > 0:
                    return MOVE_RIGHT
                else:
                    return MOVE_LEFT
            # do not do long move while distance > 6
            else:
                if dire > 0:
                    return TURN_LEFT
                else:
                    return TURN_RIGHT

        if dis < 2.5:
            if dire > 0:
                return MOVE_RIGHT
            else:
                return MOVE_LEFT
        elif dis < 5:
            if dire > 0:
                return TURN_LEFT
            else:
                return TURN_RIGHT
        else:
            if dire > 0:
                return MOVE_LEFT
            else:
                return MOVE_RIGHT


    def better_action(self,soul, boss_x, boss_y, player_x, skill):
        dis = abs(player_x - boss_x)
        if skill:
            if dis < 3:
                return RUSH
            else:
                return ATTACK

        if boss_y > 34 and dis < 5 and soul >= 33:
            return SKILL_UP

        if dis < 1.5:   # rush when distance < 1.5
            return RUSH

        elif dis < 5:
            if boss_y > 32:
                return RUSH
            else:
                act = np.random.randint(self.act_dim)
                if soul < 33:
                    while act == SKILL_UP or act == SKILL_DOWN:
                        act = np.random.randint(self.act_dim)
                return act

        elif dis < 12:
            act = np.random.randint(2)
            return SHORT_JUMP + act   # Shortjump or midjump randomly
        else:
            return RUSH

