[![Sample from random exploration with Go-Explore](https://img.youtube.com/vi/u_E8dyRb5YE/hqdefault.jpg)](https://www.youtube.com/watch?v=u_E8dyRb5YE&feature=youtu.be)
# Minimal Go-Explore
A Python implementation of the Go-Explore exploration algorithm without domain knowledge.

# Some Inconsistencies
Be aware of the following regarding my implementation:
- The Go-Explore algorithm has many specifics in terms of hyperparameters and tiny, yet important details, and it's likely I messed up at least one of them.
- My implementation is limitted to Atari with no domain-knowledge. I also included a piece of code slightly adapted to run with the `retro` module, which enables use of any ROM game file, but removes the ability to explore from multiple cells at once.
- At least for my Atari implementation with the standard `gym` module, it explores with multiple agents at once, but not in parallel threads. Instead, it simply performs all sampled actions individually, then moves onto the next step.
- My implementation of OrderedDict is ridiculous; I only used it because I realized a big issue with the structure of my prior `dict` object towards the end of the process the would require quite a few fine edits throughout my code. I simply wanted to see whether it worked sooner. I'm not focusing on this repo in the future, but unless you are using parts of my code in your own implementation, this should not be a problem.
- For the above 2 reasons, my implementation could surely be more efficient.

# Some Comments
I'm highly uncertain my implementation would acheive the same as the results presented in the paper due to the high probability of errors in my code. If you find anything you'd like to point out, just raise an issue. I'll update the code if so, but I want be updating this repo otherwise.
However, I tested my Atari implementation on Montezuma's Revenge and Pitfall. I terminated my test on Pitfall because it would take too long to determine if it actually worked (the reward is so sparse). However, with Montezuma's Revenge (with also very sparse reward, but more manageable in terms of time-to-explore before finding reward), it is continuously discovering new cells, rooms, and reward. I tested it for 30 minutes and from the few seconds I watched it render the game, it appeared to have reached a score of 2600, discovered a little over 200 cells, and 5 or 6 rooms. I'm sure it would continue to improve if I ran it for longer (I didnt'y really run it for very long), but as I mentioned, not confident that it would compare to the official Go-Explore implementation.
Aside from some of my final hasty edits, the code is alright.

# Some Benefits
The only reasons I'd think an individual would prefer this over the official implementation is:
- It's far less code
- It renders throughout (at a low frame rate, to not further increase the time it takes to explore by too much)
- It also renders a cell-discovery graph as it explores.
- You can even render all of the simultaneous agents in an evenly-aligned grid of cv2 windows.
- It's easier to visualize — both the code and the rendered visualizations
- It barely uses any RAM. I was able to run Atari on Montezuma's Revenge and Pitfall (each with 16 simultaneous simulations) as well as one on Yoshi's Island, and it used less than 10 GB. If you remove the line that saves the cell pixel values (I did this for comparison), it requires less than 1GB with 16 simultaneous simulations. I didn't fully read through Go-Explore's entire official implementation, but one of the key features to my low RAM usage is that I store SHA256 hashes of each cell, instead of the actual pixel matrix. This works fine because at no point in the algorithm does it actually matter what the actual pixel values of prior discovered cells are. Therefore, I can just store references to the cells in the form of hashes, and determine if the current cell was already discovered by comparing the hashes between it and prior cells' hashes. Again, I'm not sure if the official implementation does something like this as well.

# Installation
The setup for `retro` gym is more lengthy than the standard `gym`. `gym` comes preinstalled with many Atari environments, but `retro` allows you to import any ROM file you'd like. Follow the installation and usage procedures according to these links:
- [`Retro` Main Page (via OpenAI Website)](https://openai.com/blog/gym-retro/) [`Retro` Documentation](https://retro.readthedocs.io/en/latest/getting_started.html)
- [`Gym` Main Page (via OpenAI Website)](https://gym.openai.com/) [`Gym` Documentation](https://gym.openai.com/docs/)
