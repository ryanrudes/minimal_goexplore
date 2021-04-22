class TerminalCondition:
    def __init__(self):
        pass

    def isterminal(self, reward, terminal, info):
        raise NotImplementedError('The terminal condition has not been implemented')

class TerminateOnLifeLoss(TerminalCondition):
    def __init__(self, lives, lives_key='ale.lives'):
        super().__init__()
        self.lives = lives
        self.lives_key = lives_key

    def isterminal(self, reward, terminal, info):
        return terminal | info[self.lives_key] < self.lives

class TerminateOnNegativeReward(TerminalCondition):
    def __init__(self):
        super().__init__()

    def isterminal(self, reward, terminal, info):
        return terminal | reward < 0

class TerminalConditionGroup(TerminalCondition):
    def __init__(self, conditions):
        super().__init__()
        self.conditions = conditions

    def isterminal(self, reward, terminal, info):
        if terminal:
            return True

        for condition in self.conditions:
            if condition.isterminal(reward, terminal, info):
                return True

        return False
