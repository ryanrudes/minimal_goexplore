# Minimal Go-Explore
A Python implementation of the Go-Explore exploration algorithm without domain knowledge.

<a href="https://ibb.co/RH7NtFC"><img src="https://i.ibb.co/0JQK17f/rooms.png" alt="rooms" border="0"></a><br /><a target='_blank' href='https://imgbb.com/'></a><br />

A Go-Explore agent discovers many rooms in Montezuma's Revenge even when run for just an hour on a single home CPU.

![Alt Text](https://media.giphy.com/media/vVGCKu6SX9Y7T11RCj/giphy.gif)

Two agents exploring via Go-Explore, returning according to a different metric.

<a href="https://ibb.co/Q6HKckk"><img src="https://i.ibb.co/VvCqNxx/all-shots.jpg" alt="all-shots" border="0"></a>

The many different cells found in various `gym` environments.

# Some Inconsistencies/Comments
Be aware of the following regarding my implementation:
- The Go-Explore algorithm has many specifics in terms of hyperparameters and tiny, yet important details, and it's likely I messed up at least one of them.
- My implementation is limitted to Atari with no domain-knowledge. I also included a piece of code slightly adapted to run with the `retro` module, which enables use of any ROM game file, but removes the ability to explore from multiple cells at once.
- At least for my Atari implementation with the standard `gym` module, it explores with multiple agents at once, but not in parallel threads. Instead, it simply performs all sampled actions individually, then moves onto the next step.
- My implementation of OrderedDict is ridiculous; I only used it because I realized a big issue with the structure of my prior `dict` object towards the end of the process the would require quite a few fine edits throughout my code. I simply wanted to see whether it worked sooner. I'm not focusing on this repo in the future, but unless you are using parts of my code in your own implementation, this should not be a problem.
- For the above 2 reasons, my implementation could surely be more efficient.
- Aside from some of my final hasty edits, the code is alright.

# Some Benefits
The only reasons I'd think an individual would prefer this over the official implementation is:
- It's far less code
- It renders throughout (at a low frame rate, to not further increase the time it takes to explore by too much)
- It also renders a cell-discovery graph as it explores.
- You can even render all of the simultaneous agents in an evenly-aligned grid of cv2 windows.
- It's easier to visualize — both the code and the rendered visualizations
- It barely uses any RAM. I didn't fully read through Go-Explore's entire official implementation, but one of the key features to my low RAM usage is that I store SHA256 hashes of each cell, instead of the actual pixel matrix. This works fine because at no point in the algorithm does it actually matter what the actual pixel values of prior discovered cells are. Therefore, I can just store references to the cells in the form of hashes, and determine if the current cell was already discovered by comparing the hashes between it and prior cells' hashes. Again, I'm not sure if the official implementation does something like this as well.

# Installation
The setup for `retro` gym is more lengthy than the standard `gym`. `gym` comes preinstalled with many Atari environments, but `retro` allows you to import any ROM file you'd like. Follow the installation and usage procedures according to these links:
- [`Retro` Main Page (via OpenAI Website)](https://openai.com/blog/gym-retro/) [`Retro` Documentation](https://retro.readthedocs.io/en/latest/getting_started.html)
- [`Gym` Main Page (via OpenAI Website)](https://gym.openai.com/) [`Gym` Documentation](https://gym.openai.com/docs/)

* Try `threaded-atari.py` instead of `atari.py`, it's far faster when using multithreading

# Demonstration
[![Sample from random exploration with Go-Explore](https://img.youtube.com/vi/u_E8dyRb5YE/hqdefault.jpg)](https://www.youtube.com/watch?v=u_E8dyRb5YE&feature=youtu.be)

Click the image above to redirect to a 2-minute YouTube video. It shows a rendering of three environments with a random agent exploring, then returning to previously-discovered states according to the procedure of Go-Explore. These are obviously **not** samples of a trained agent, rather merely the random exploration agent after a bit of exploration.

# Results
- I was able to discover 18 unique rooms in Montezuma's Revenge, and 23 different rooms (some repeat in the game). Here's the unique ones:

<a href="https://ibb.co/MVRxDwV"><img src="https://i.ibb.co/hWKJRQW/ims.png" alt="ims" border="0"></a>

- I maxed out the Q\*bert scoreboard... twice (this would continue as it ran more).

<a href="https://ibb.co/w0cWBkt"><img src="https://i.ibb.co/r7d6Fj9/qbert-ims.png" alt="qbert-ims" border="0"></a>
<a href="https://imgbb.com/"><img src="https://i.ibb.co/30fCMqw/qbert-im.png" alt="qbert-im" border="0"></a>

- I maxed out the scoreboard of Pinball in approx. 2 minutes on my CPU.

<a href="https://imgbb.com/"><img src="https://i.ibb.co/ZgSFx2P/Screen-Shot-2020-10-02-at-2-58-33-PM.png" alt="Screen-Shot-2020-10-02-at-2-58-33-PM" border="0"></a>

- I beat the first three levels of Breakout in about the same amount of time

<a href="https://imgbb.com/"><img src="https://i.ibb.co/jkL2v07/Screen-Shot-2020-10-02-at-5-20-18-PM.png" alt="Screen-Shot-2020-10-02-at-5-20-18-PM" border="0"></a>

- It can theoretically beat PacMan indefinetely, so I'll just show up to about the fifth or sixth level:

<a href="https://imgbb.com/"><img src="https://i.ibb.co/HCwgxnZ/Screen-Shot-2020-10-02-at-5-20-20-PM.png" alt="Screen-Shot-2020-10-02-at-5-20-20-PM" border="0"></a>

**EDIT (March 16, 2021)**
Looking back, there were far more efficient ways to accomplish this. Here are some ways in that I would write it differently in hindsight:
* For one, Python's built-in hash is far better for this purpose than anything from `hashlib`. This is because Python's `hash()` function is fast and can hash the bytes of a numpy array using `hash(ndarray.tobytes())`
* Some code refactoring made it much easier to read
* I realized that I partially messed up the cell function (it's supposed to be reduced to 8 possible values, I accidentally made it 32)
* I found that there is a very little difference between using Go Explore's special return heuristic versus merely returning to previously experienced cells at random. This makes for an easier code sample by far which produces similar results (although this claim might not hold for later stages, where the special heuristic might enable the algorithm to be far superior to a random return policy, which might get stuck exploring a large number of mostly irrelevant cells).

Taking these points into account, here's a very simple and far shorter (50 lines) code sample that performs similarly to the one provided in the repo earlier:

```python
from random import choice
import numpy as np
import cv2
import gym

def cellfn(observation):
    cell = cv2.cvtColor(observation, cv2.COLOR_RGB2GRAY)
    cell = cv2.resize(cell, (11, 8), interpolation = cv2.INTER_AREA)
    cell = cell // 32
    return cell

def hashfn(observation):
    return hash(observation.tobytes())

def add(observation):
    global archive
    cell = cellfn(observation)
    hashed = hashfn(cell)
    if not hashed in archive:
        ram = env.env.clone_full_state()
        hashes.append(hashed)
        archive[hashed] = ram

hashes = []
archive = dict()

env = gym.make("MontezumaRevenge-v0")
episodes = 0

observation = env.reset()
add(observation)

while True:
    terminal = False

    while not terminal:
        action = env.action_space.sample()
        observation, reward, terminal, info = env.step(action)
        terminal |= info['ale.lives'] < 6
        if episodes % 10 == 0:
            env.render()
        if not terminal:
            add(observation)

    hashed = choice(hashes)
    ram = archive[hashed]

    env.reset()
    env.env.restore_full_state(ram)
    episodes += 1

    print ("Episode: %d, Cells discovered: %d" % (episodes, len(hashes)))

```
