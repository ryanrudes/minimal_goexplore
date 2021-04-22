from collections import deque
import numpy as np
import cv2
import gym

from .termination import *

class SpecialWrapper(gym.Wrapper):
    metadata = {'render.modes': ['human', 'rgb_array', 'encoding']}

    def __init__(self, env, terminal_condition):
        super(SpecialWrapper, self).__init__(env)
        self.terminal_condition = terminal_condition

    def reset(self):
        return self.env.reset()

    def step(self, action):
        observation, reward, terminal, info = self.env.step(action)
        if not terminal:
            terminal = self.terminal_condition.isterminal(reward, terminal, info)
        return observation, reward, terminal, info

    def render(self, mode='human', **kwargs):
        if mode == 'encoding':
            if not 'encoder' in kwargs:
                raise TypeError('Expected an encoder model `encoder`')
            if not 'observation' in kwargs:
                raise TypeError('Expected previous observation `observation`')

            encoder = kwargs['encoder']
            observation = kwargs['observation']
            encoding = encoder.predict(np.expand_dims(observation, axis = 0))[0]
            encoding = (encoding - encoding.min()) / (encoding.max() - encoding.min())
            image = np.repeat(np.expand_dims(encoding, axis = -1), 3, axis = -1)
            image = np.uint8(image * 255)
            image = cv2.resize(image, (210, 210), interpolation = cv2.INTER_AREA)
            image = np.concatenate((observation, image), axis = 1)

            if self.viewer is None:
                from gym.envs.classic_control.rendering import SimpleImageViewer
                self.viewer = SimpleImageViewer()

            self.viewer.imshow(image)
        else:
            return self.env.render(mode, **kwargs)

class FrameStack(gym.Wrapper):
    def __init__(self, env, size, mergefn=np.max):
        super(FrameStack, self).__init__(env)
        self.size = size
        self.mergefn = mergefn
        self.buffer = deque(maxlen = self.size)

    def observe(self):
        return self.mergefn(self.buffer, axis = 0)

    def reset(self):
        self.buffer.clear()
        self.buffer.append(self.env.reset())
        return self.observe()

    def step(self, action):
        observation, reward, terminal, info = self.env.step(action)
        self.buffer.append(observation)
        return self.observe(), reward, terminal, info

class GymSpecialWrapper(SpecialWrapper):
    def __init__(self, env_id, terminal_condition):
        super(GymSpecialWrapper, self).__init__(gym.make(env_id + 'Deterministic-v4'), terminal_condition)

# Environment Wrappers
MontezumaRevenge = lambda: GymSpecialWrapper('MontezumaRevenge', TerminateOnLifeLoss(6))
SpaceInvaders    = lambda: GymSpecialWrapper('SpaceInvaders',    TerminateOnLifeLoss(3))
VideoPinball     = lambda: GymSpecialWrapper('VideoPinball',     TerminateOnLifeLoss(3))
Breakout         = lambda: GymSpecialWrapper('Breakout',         TerminateOnLifeLoss(3))
Qbert            = lambda: GymSpecialWrapper('Qbert',            TerminateOnLifeLoss(4))

Pong             = lambda: GymSpecialWrapper('Pong', TerminateOnNegativeReward())

Pitfall          = lambda: GymSpecialWrapper('Pitfall', TerminalConditionGroup([
                                                            TerminateOnNegativeReward(),
                                                            TerminateOnLifeLoss(3)
                                                        ]))
