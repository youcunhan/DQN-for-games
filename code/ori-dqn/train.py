import time

import cv2
import numpy as np

import directkeys
import factor
from DQN_tensorflow_gpu import DQN
from getkeys import key_check
from grabscreen import grab_screen
from restart import restart


def pause_game(paused):
    keys = key_check()
    if 'T' in keys:
        if paused:
            paused = False
            print('start game')
            time.sleep(1)
        else:
            paused = True
            print('pause game')
            time.sleep(1)
    if paused:
        print('paused')
        while True:
            keys = key_check()
            # pauses game and can get annoying.
            if 'T' in keys:
                if paused:
                    paused = False
                    print('start game')
                    time.sleep(1)
                    break
                else:
                    paused = True
                    time.sleep(1)
    return paused


def take_action(action):
    if action == 0:  # n_choose
        pass
    elif action == 1:  # A
        directkeys.go_left()
    elif action == 2:  # D
        directkeys.go_right()
    elif action == 3:  # J
        directkeys.jump()
    elif action == 4:  # P
        directkeys.rush()
    elif action == 5:  # Z
        directkeys.attack()


def action_judge(boss_blood, next_boss_blood, self_blood, next_self_blood, stop, emergence_break,loc):
    # get action reward
    # emergence_break is used to break down training
    if next_self_blood<1 and self_blood < 1:  # self dead
        if emergence_break < 2:
            reward = -10
            done = 1
            stop = 0
            emergence_break += 1
            #restart()
            return reward, done, stop, emergence_break
        else:   
            reward = -10
            done = 1
            stop = 0
            #emergence_break = 100
            #restart()
            return reward, done, stop, emergence_break
    elif next_boss_blood < 0:  # boss dead
        if emergence_break < 2:
            reward = 50
            done = 0
            stop = 0
            emergence_break += 1
            print('you killed him!')
            #restart()
            return reward, done, stop, emergence_break
        else:
            reward = 50
            done = 0
            stop = 0
            #emergence_break = 100
            #restart()
            return reward, done, stop, emergence_break
    else:
        self_blood_reward = 0
        boss_blood_reward = 0
        loc_reward = 0
        # print(next_self_blood - self_blood)
        # print(next_boss_blood - boss_blood)
        if next_self_blood - self_blood < -1:
            if stop == 0:
                self_blood_reward = -6
                stop = 1
        else:
            self_blood_reward = 0
            stop = 0
        if next_boss_blood - boss_blood <= -5:
            boss_blood_reward = 60
        # print("self_blood_reward:    ",self_blood_reward)
        # print("boss_blood_reward:    ",boss_blood_reward)
        if loc<-95 or loc > -50:
            loc_reward = -20
        reward = self_blood_reward + boss_blood_reward + loc_reward
        done = 0
        emergence_break = 0
        return reward, done, stop, emergence_break


DQN_model_path = "model_gpu"
DQN_log_path = "logs_gpu/"
WIDTH = 96
HEIGHT = 88
window_size = (58 , 70 , 1241 , 769)  # 38,90,680,445.32 57 688 456
# station window_size

# blood_window = (60,91,280,562)
# used to get boss and self blood

action_size = 6
# action[n_choose,left,right,jump,rush,attack]
# j-attack, k-jump, m-defense, r-dodge, n_choose-do nothing

EPISODES = 2000
big_BATCH_SIZE = 16
UPDATE_STEP = 50
# times that evaluate the network
num_step = 0
# used to save log graph
target_step = 0
# used to update target Q network
paused = True
# used to stop training
lower_hsv_r = np.array([8,215,134])
upper_hsv_r = np.array([19,253,255])
lower_hsv_b = np.array([0,0,255])
upper_hsv_b = np.array([109,23,255])

if __name__ == '__main__':
    print("Before DQN")
    agent = DQN(WIDTH, HEIGHT, action_size, DQN_model_path, DQN_log_path)
    print("After DQN")
    Hp = factor.Gamefactors()
    loc_addr= Hp.location_addr()
    boss_addr=Hp.boss_hp_addr()
    self_addr=Hp.self_hp_addr()
    # DQN init
    paused = pause_game(paused)
    # paused at the begin
    emergence_break = 0
    # emergence_break is used to break down training
    for episode in range(EPISODES):
        hsv = cv2.cvtColor(grab_screen(window_size), cv2.COLOR_BGR2HSV)
        # hsv = cv2.cvtColor(grab_screen(), cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, lower_hsv_r, upper_hsv_r)
        mask2 = cv2.inRange(hsv, lower_hsv_b, upper_hsv_b)
        mask = cv2.bitwise_or(mask1, mask2)
        station = cv2.resize(mask, (WIDTH, HEIGHT))
        # change graph to WIDTH * HEIGHT for station input
        boss_blood = Hp.get_value(boss_addr)
        self_blood = Hp.get_value(self_addr)
        if self_blood == 0:
            restart()
            emergence_break = 0
        if boss_blood == 0:
            restart()
            emergence_break = 0
        # count init blood
        target_step = 0
        # used to update target Q network
        done = 0
        total_reward = 0
        stop = 0
        last_time = time.time()
        while True:
            station = np.array(station).reshape(-1, HEIGHT, WIDTH, 1)[0]
            # reshape station for tf input placeholder
            print('loop took {} seconds'.format(time.time() - last_time))
            last_time = time.time()
            target_step += 1
            # get the action by state
            action = agent.Choose_Action(station)
            take_action(action)
            # take station then the station change
            screen_gray = cv2.cvtColor(grab_screen(window_size), cv2.COLOR_BGR2HSV)
            mask1 = cv2.inRange(screen_gray, lower_hsv_r, upper_hsv_r)
            mask2 = cv2.inRange(screen_gray, lower_hsv_b, upper_hsv_b)
            screen_hsv = cv2.bitwise_or(mask1, mask2)
            # collect station gray graph
            # collect blood gray graph for count self and boss blood
            next_station = cv2.resize(screen_hsv, (WIDTH, HEIGHT))
            next_station = np.array(next_station).reshape(-1, HEIGHT, WIDTH, 1)[0]
            next_boss_blood = Hp.get_value(boss_addr)
            next_self_blood = Hp.get_value(self_addr)
            loc=Hp.get_value(loc_addr)
            if loc < -90:
                directkeys.go_rightn()
            elif loc < -50:
                pass
            else:
                directkeys.go_leftn()
            reward, done, stop, emergence_break = action_judge(boss_blood, next_boss_blood,
                                                               self_blood, next_self_blood,
                                                               stop, emergence_break,loc)
            # get action reward
            if emergence_break == 100:
                # emergence break, save model and paused
                print("emergence_break")
                agent.save_model()
                paused = True
            agent.Store_Data(station, action, reward, next_station, done)
            if len(agent.replay_buffer) > big_BATCH_SIZE:
                num_step += 1
                # save loss graph
                # print('train')
                agent.Train_Network(big_BATCH_SIZE, num_step)
            if target_step % UPDATE_STEP == 0:
                agent.Update_Target_Network()
                # update target Q network
            station = next_station
            self_blood = next_self_blood
            boss_blood = next_boss_blood

            total_reward += reward
            paused = pause_game(paused)
            if done == 1:
                break
        if episode % 10 == 0:
            agent.save_model()
            # save model
        print('episode: ', episode, 'Evaluation Average Reward:', total_reward / target_step)
        restart()
