from collections import defaultdict, namedtuple
from threading import Thread
from time import sleep
import numpy as np
import cv2
import gym

def cellfn(frame):
    cell = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    cell = cv2.resize(cell, (11, 8), interpolation = cv2.INTER_AREA)
    cell = cell // 32
    return cell

def hashfn(cell):
    return hash(cell.tobytes())

class Weights:
    times_chosen = 0.1
    times_chosen_since_new = 0
    times_seen = 0.3

class Powers:
    times_chosen = 0.5
    times_chosen_since_new = 0.5
    times_seen = 0.5

class Cell(object):
    def __init__(self):
        self.times_chosen = 0
        self.times_chosen_since_new = 0
        self.times_seen = 0

    def cntscore(self, a):
        w = getattr(Weights, a)
        p = getattr(Powers, a)
        v = getattr(self, a)
        return w / (v + e1) ** p + e2

    def cellscore(self):
        return self.cntscore('times_chosen')           +\
               self.cntscore('times_chosen_since_new') +\
               self.cntscore('times_seen')             +\
               1

    def visit(self):
        first_visit = False
        if not self.times_seen:
            first_visit = True
            for cell in archive.values():
                cell.times_chosen_since_new = 0
                cell.score = cell.cellscore()

        self.times_seen += 1
        self.score = self.cellscore()
        return first_visit

    def choose(self):
        self.times_chosen += 1
        self.times_chosen_since_new += 1
        return self.ram, self.reward

archive = defaultdict(lambda: Cell())
highscore = 0
done = False

best_cell = np.zeros((1, 1, 3))
new_cell = np.zeros((1, 1, 3))

e1 = 0.001
e2 = 0.00001

def explore():
    global highscore, best_cell, new_cell

    env = gym.make("MontezumaRevenge-v0")
    frame = env.reset()
    score = 0

    while True:
        while True:
            try:
                action = env.action_space.sample()
                frame, reward, terminal, info = env.step(action)
                score += reward
                terminal |= info['ale.lives'] < 6

                if score > highscore:
                    highscore = score
                    best_cell = np.copy(frame)

                if terminal:
                    break
                else:
                    cell = cellfn(frame)
                    cellhash = hashfn(cell)
                    cell = archive[cellhash]
                    first_visit = cell.visit()
                    if first_visit:
                        cell.ram = env.env.clone_full_state()
                        cell.reward = score
                        new_cell = np.copy(frame)
            except KeyboardInterrupt:
                while True:
                    try:
                        print ("SHUTTING DOWN")
                        env.close()
                        return
                    except:
                        pass

        scores = np.array([cell.score for cell in archive.values()])
        hashes = [cellhash for cellhash in archive.keys()]
        probs = scores / scores.sum()
        restore = np.random.choice(hashes, p = probs)
        cell = archive[restore]
        ram, score = cell.choose()
        env.reset()
        env.env.restore_full_state(ram)

threads = [Thread(target = explore) for id in range(8)]

for thread in threads:
    thread.start()

while True:
    try:
        print ("Cells: %d, Max Reward: %d" % (len(archive), highscore))
        cv2.imshow("Best Cell", best_cell)
        cv2.imshow("Newest Cell", new_cell)
        cv2.waitKey(1)
        sleep(1)
    except KeyboardInterrupt:
        sleep(3)
        exit()
