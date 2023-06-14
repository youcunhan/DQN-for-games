# -*- coding: utf-8 -*-
import numpy as np
from tensorflow.keras.models import load_model
import tensorflow as tf
import time
import collections
import matplotlib.pyplot as plt

from Model import Model
from DQN import DQN
from Agent import Agent
from ReplayMemory import ReplayMemory


import Tool.Helper
import Tool.Actions
from Tool.Helper import mean, is_end
from Tool.Actions import take_action, restart,take_direction, TackAction
from Tool.WindowsAPI import grab_screen
from Tool.GetHP import Hp_getter
from Tool.UserInput import User
from Tool.FrameBuffer import FrameBuffer

window_size = (0,0,1920,1017)
station_size = (230, 230, 1670, 930)

HP_WIDTH = 768
HP_HEIGHT = 407
WIDTH = 400
HEIGHT = 200
ACTION_DIM = 7
FRAMEBUFFERSIZE = 4
INPUT_SHAPE = (FRAMEBUFFERSIZE, HEIGHT, WIDTH, 3)

MEMORY_SIZE = 200
MEMORY_WARMUP_SIZE = 24
BATCH_SIZE = 10
LEARNING_RATE = 0.00001
GAMMA = 0

action_name = ["Attack", "Attack_Up",
           "Short_Jump", "Mid_Jump", "Skill_Up", 
           "Skill_Down", "Rush", "Cure"]

move_name = ["Move_Left", "Move_Right", "Turn_Left", "Turn_Right"]

DELAY_REWARD = 1

def run_episode(hp, algorithm,agent,act_rmp_correct, move_rmp_correct,PASS_COUNT,paused):
    restart()
    for i in range(8):
        if (len(move_rmp_correct) > MEMORY_WARMUP_SIZE):
            batch_station,batch_actions,batch_reward,batch_next_station,batch_done = move_rmp_correct.sample(BATCH_SIZE)
            algorithm.move_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)   

        if (len(act_rmp_correct) > MEMORY_WARMUP_SIZE):
            batch_station,batch_actions,batch_reward,batch_next_station,batch_done = act_rmp_correct.sample(BATCH_SIZE)
            algorithm.act_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)

    
    step = 0
    done = 0
    total_reward = 0

    # Delay Reward
    DelayMoveReward = collections.deque(maxlen=DELAY_REWARD)
    DelayActReward = collections.deque(maxlen=DELAY_REWARD)
    DelayStation = collections.deque(maxlen=DELAY_REWARD + 1) # 1 more for next_station
    DelayActions = collections.deque(maxlen=DELAY_REWARD)
    DelayDirection = collections.deque(maxlen=DELAY_REWARD)
    
    while True:
        boss_hp_value = hp.get_boss_hp()
        self_hp = hp.get_self_hp()
        if boss_hp_value > 800 and  boss_hp_value <= 900 and self_hp >= 1 and self_hp <= 9:
            break
        

    thread1 = FrameBuffer(1, "FrameBuffer", WIDTH, HEIGHT, maxlen=FRAMEBUFFERSIZE)
    thread1.start()

    last_hornet_y = 0
    while True:
        step += 1
        
        while(len(thread1.buffer) < FRAMEBUFFERSIZE):
            time.sleep(0.1)
        
        stations = thread1.get_buffer()
        boss_hp_value = hp.get_boss_hp()
        self_hp = hp.get_self_hp()
        player_x, player_y = hp.get_play_location()
        hornet_x, hornet_y = hp.get_hornet_location()
        soul = hp.get_souls()

        hornet_skill1 = False
        if last_hornet_y > 32 and last_hornet_y < 32.5 and hornet_y > 32 and hornet_y < 32.5:
            hornet_skill1 = True
        last_hornet_y = hornet_y

        move, action = agent.sample(stations, soul, hornet_x, hornet_y, player_x, hornet_skill1)

        take_direction(move)
        take_action(action)
        
        next_boss_hp_value = hp.get_boss_hp()
        next_self_hp = hp.get_self_hp()
        next_player_x, _ = hp.get_play_location()
        next_hornet_x, _ = hp.get_hornet_location()

        # get reward
        move_reward = Tool.Helper.move_judge(self_hp, next_self_hp, player_x, next_player_x, hornet_x, next_hornet_x, move, hornet_skill1)
        act_reward, done = Tool.Helper.action_judge(boss_hp_value, next_boss_hp_value,self_hp, next_self_hp, next_player_x, next_hornet_x,next_hornet_x, action, hornet_skill1)
        
        DelayMoveReward.append(move_reward)
        DelayActReward.append(act_reward)
        DelayStation.append(stations)
        DelayActions.append(action)
        DelayDirection.append(move)

        if len(DelayStation) >= DELAY_REWARD + 1:
            if DelayMoveReward[0] != 0:
                move_rmp_correct.append((DelayStation[0],DelayDirection[0],DelayMoveReward[0],DelayStation[1],done))
            
        if len(DelayStation) >= DELAY_REWARD + 1:
            if mean(DelayActReward) != 0:
                act_rmp_correct.append((DelayStation[0],DelayActions[0],mean(DelayActReward),DelayStation[1],done))
            
        self_hp = next_self_hp
        boss_hp_value = next_boss_hp_value
        total_reward += act_reward
        paused = Tool.Helper.pause_game(paused)

        if done == 1:
            Tool.Actions.Nothing()
            break
        elif done == 2:
            PASS_COUNT += 1
            Tool.Actions.Nothing()
            time.sleep(3)
            break
        

    thread1.stop()

    for i in range(8):
        if (len(move_rmp_correct) > MEMORY_WARMUP_SIZE):
            batch_station,batch_actions,batch_reward,batch_next_station,batch_done = move_rmp_correct.sample(BATCH_SIZE)
            algorithm.move_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)   

        if (len(act_rmp_correct) > MEMORY_WARMUP_SIZE):
            batch_station,batch_actions,batch_reward,batch_next_station,batch_done = act_rmp_correct.sample(BATCH_SIZE)
            algorithm.act_learn(batch_station,batch_actions,batch_reward,batch_next_station,batch_done)

    return total_reward, step, PASS_COUNT, self_hp


if __name__ == '__main__':

    # In case of out of memory
    config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    sess = tf.compat.v1.Session(config = config)

    
    total_remind_hp = 0

    act_rmp_correct = ReplayMemory(MEMORY_SIZE, file_name='./act_memory')
    move_rmp_correct = ReplayMemory(MEMORY_SIZE,file_name='./move_memory')
    
    model = Model(INPUT_SHAPE, ACTION_DIM)  
    hp = Hp_getter()


    model.load_model()
    algorithm = DQN(model, gamma=GAMMA, learnging_rate=LEARNING_RATE)
    agent = Agent(ACTION_DIM,algorithm,e_greed=0.12,e_greed_decrement=1e-6)

    # paused at the begining
    paused = True
    paused = Tool.Helper.pause_game(paused)

    max_episode = 30000
    # start training
    episode = 0
    PASS_COUNT = 0
    while episode < max_episode:

        episode += 1

        total_reward, total_step, PASS_COUNT, remind_hp = run_episode(hp, algorithm,agent,act_rmp_correct, move_rmp_correct, PASS_COUNT, paused)
        if episode % 10 == 1:
            model.save_mode()
        if episode % 5 == 0:
            move_rmp_correct.save(move_rmp_correct.file_name)
        if episode % 5 == 0:
            act_rmp_correct.save(act_rmp_correct.file_name)
        total_remind_hp += remind_hp
        print("Episode: ", episode, ", pass_count: " , PASS_COUNT, ", hp:", total_remind_hp / episode)

