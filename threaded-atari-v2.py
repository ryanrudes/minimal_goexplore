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

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        if key != 'score' and hasattr(self, 'times_seen'):
            self.score = self.cellscore()

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
        self.times_seen += 1
        return self.times_seen == 1

    def choose(self):
        self.times_chosen += 1
        self.times_chosen_since_new += 1
        return self.ram, self.reward, self.trajectory

archive = defaultdict(lambda: Cell())
highscore = 0
frames = 0
iterations = 0

best_cell = np.zeros((1, 1, 3))
new_cell = np.zeros((1, 1, 3))

e1 = 0.001
e2 = 0.00001

def explore(id):
    global highscore, frames, iterations, best_cell, new_cell, archive

    env = gym.make("MontezumaRevengeNoFrameskip-v0")
    frame = env.reset()
    score = 0
    action = 0
    trajectory = []
    my_iterations = 0

    sleep(id / 10)

    while True:
        found_new_cell = False
        episode_length = 0

        for i in range(100):
            if np.random.random() > 0.95:
                action = env.action_space.sample()

            for i in range(4):
                frame, reward, terminal, info = env.step(action)
                score += reward
                terminal |= info['ale.lives'] < 6
                if terminal:
                    break

            trajectory.append(action)
            episode_length += 4

            if score > highscore:
                highscore = score
                best_cell = cv2.cvtColor(np.copy(frame), cv2.COLOR_BGR2RGB)

            if terminal:
                frames += episode_length
                break
            else:
                cell = cellfn(frame)
                cellhash = hashfn(cell)
                cell = archive[cellhash]
                first_visit = cell.visit()
                if first_visit or score > cell.reward or score == cell.reward and len(trajectory) < len(cell.trajectory):
                    cell.ram = env.env.clone_full_state()
                    cell.reward = score
                    cell.trajectory = trajectory.copy()
                    cell.times_chosen = 0
                    cell.times_chosen_since_new = 0
                    new_cell = cv2.cvtColor(np.copy(frame), cv2.COLOR_BGR2RGB)
                    if first_visit:
                        found_new_cell = True

        if found_new_cell and my_iterations > 0:
            restore_cell.times_chosen_since_new = 0

        scores = np.array([cell.score for cell in archive.values()])
        hashes = [cellhash for cellhash in archive.keys()]
        probs = scores / scores.sum()
        restore = np.random.choice(hashes, p = probs)
        restore_cell = archive[restore]
        ram, score, trajectory = restore_cell.choose()
        env.env.restore_full_state(ram)
        my_iterations += 1
        iterations += 1

threads = [Thread(target = explore, args = (id,)) for id in range(8)]

for thread in threads:
    thread.start()

while True:
    print ("Iterations: %d, Cells: %d, Frames: %d, Max Reward: %d" % (iterations, len(archive), frames, highscore))
    cv2.imshow("Best Cell", best_cell)
    cv2.imshow("Newest Cell", new_cell)
    cv2.waitKey(1)
    sleep(1)
