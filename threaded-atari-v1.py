import gym
from hashlib import sha256
import cv2
import numpy as np
import logging
import time
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-id", default = "MontezumaRevenge-v0", help = "Enter an OpenAI Gym Environment ID (MontezumaRevenge-v0 or Pitfall-v0)", type = str)
parser.add_argument("-threads", default = 8, help = "Enter the number of concurrent threads for exploration", type = int)
args = parser.parse_args()

if args.id == "MontezumaRevenge-v0":
    downsampled_width = 11
    downsampled_height = 8
    downsampled_pixel_range = 8
    times_chosen_weight =  0.1
    times_chosen_since_new_weight = 0
    times_seen_weight = 0.3
    times_chosen_power = 0.5
    times_chosen_since_new_power = 0.5
    times_seen_power = 0.5
    epsilon_1 = 0.001
    epsilon_2 = 0.00001
elif args.id == "Pitfall-v0":
    downsampled_width = 11
    downsampled_height = 8
    downsampled_pixel_range = 8
    times_chosen_weight = 1
    times_chosen_since_new_weight = 1
    times_seen_weight = 0
    times_chosen_power = 0.5
    times_chosen_since_new_power = 0.5
    times_seen_power = 0.5
    epsilon_1 = 0.001
    epsilon_2 = 0.00001
else:
    raise NotImplementedError()

logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s: %(message)s",
                    datefmt = "%Y-%m-%d %H:%M:%S")

def cellulize(state):
    cell = cv2.cvtColor(state, cv2.COLOR_RGB2GRAY)
    cell = cv2.resize(cell, (downsampled_height, downsampled_width))
    cell = np.uint8(cell // (255 / downsampled_pixel_range))
    return cell

def encrypt(cell):
    return sha256(cell).hexdigest()

class Cell:
    def __init__(self, hash, restore):
        self.hash = hash
        self.restore = restore

        self.times_chosen = 0
        self.times_chosen_since_new = 0
        self.times_seen = 1

    def score(self):
        return times_chosen_weight * (1 / (self.times_chosen + epsilon_1)) ** times_chosen_power + epsilon_2 +\
                times_chosen_since_new_weight * (1 / (self.times_chosen_since_new + epsilon_1)) ** times_chosen_since_new_power + epsilon_2 +\
                times_seen_weight * (1 / (self.times_seen + epsilon_1)) ** times_seen_power + epsilon_2 + 1

def found(cells, hash):
    for i, cell in enumerate(cells):
        if cell.hash == hash:
            return i

    return -1

env = gym.make(args.id)
cells = [Cell(encrypt(cellulize(env.reset())), env.env.clone_full_state())]
env.close()

n = 1
episodes = 0
frames = 0
max_episode_reward = 0

def worker():
    global cells, n, episodes, frames, max_episode_reward

    env = gym.make(args.id)
    env.reset()
    terminal = False

    while True:
        episode_reward = 0
        visits = []
        while not terminal:
            action = env.action_space.sample()
            state, reward, terminal, info = env.step(action)
            episode_reward += reward
            terminal = terminal or info['ale.lives'] < 6
            cell = cellulize(state)
            hash = encrypt(cell)

            idx = found(cells, hash)
            if not idx in visits:
                visits.append(len(cells) if idx == -1 else idx)

            if idx != -1:
                cells[idx].times_seen += 1
            else:
                cells.append(Cell(hash, env.env.clone_full_state()))

                for i in visits:
                    cells[i].times_chosen_since_new = 0

            frames += 1

        max_episode_reward = max(max_episode_reward, episode_reward)
        scores = np.array([cell.score() for cell in cells])
        probs = scores / scores.sum()
        idx = np.random.choice(len(cells), p = probs)
        env.reset()
        env.env.restore_full_state(cells[idx].restore)
        cells[idx].times_chosen += 1
        cells[idx].times_chosen_since_new += 1
        terminal = False
        episodes += 1
        logging.info("Episode: %s, Frame: %s, Cells discovered: %s, Maximum reward: %s" % (episodes, frames, len(cells), max_episode_reward))

threads = [threading.Thread(target = worker) for i in range(args.threads)]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
