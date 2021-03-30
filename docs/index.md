## Explanation of the Go Explore algorithm

* Go Explore is an exploration algorithm designed to enable learning in a sparse-reward environment. Reinforcement learning algorithms struggle in these types of scenarios, for they rely on the assumption that a reward signal propogates learning, but if the probability of encountering any reward at all is so substancially low, these algorithms will not learn any meaningful policy. The paper defines this failure as a combination of two factors, *detachment* and *derailment*.

<img src="https://i.ibb.co/HHcrg30/detachment-v4.png" alt="detachment-v4" border="0" style="display:block;margin-left:auto;margin-right:auto;">
  
#### Detachment
> Detachment is the idea that an agent driven by IM could become detached from the frontiers of
> high intrinsic reward (IR). To understand detachment, we must first consider that intrinsic reward
> is nearly always a consumable resource: a curious agent is curious about states to the extent that it
> has not often visited them (similar arguments apply for surprise, novelty, or prediction-error seeking
> agents [4, 14–16]). If an agent discovers multiple areas of the state space that produce high IR, its
> policy may in the short term focus on one such area. After exhausting some of the IR offered by that
> area, the policy may by chance begin consuming IR in another area. Once it has exhausted that IR, it
> is difficult for it to rediscover the frontier it detached from in the initial area, because it has already
> consumed the IR that led to that frontier (Fig. 1), and it likely will not remember how to return to
> that frontier due to catastrophic forgetting [17–20]. Each time this process occurs, a potential avenue
> of exploration can be lost, or at least be difficult to rediscover. In the worst case, there may be a
> dearth of remaining IR near the areas of state space visited by the current policy (even though much
> IR might remain elsewhere), and therefore no learning signal remains to guide the agent to further
> explore in an effective and informed way. One could slowly add intrinsic rewards back over time,
> but then the entire fruitless process could repeat indefinitely. In theory a replay buffer could prevent
> detachment, but in practice it would have to be large to prevent data about the abandoned frontier to
> not be purged before it becomes needed, and large replay buffers introduce their own optimization
> stability difficulties [21, 22]. The Go-Explore algorithm addresses detachment by explicitly storing
> an archive of promising states visited so that they can then be revisited and explored from later.

#### Derailment
> Derailment can occur when an agent has discovered a promising state and it would be beneficial
> to return to that state and explore from it. Typical RL algorithms attempt to enact such desirable
> behavior by running the policy that led to the initial state again, but with some stochastic perturbations
> to the existing policy mixed in to encourage a slightly different behavior (e.g. exploring further). The
> stochastic perturbation is performed because IM agents have two layers of exploration mechanisms:
> (1) the higher-level IR incentive that rewards when new states are reached, and (2) a more basic
> exploratory mechanism such as epsilon-greedy exploration, action-space noise, or parameter-space
> noise [23–25]. Importantly, IM agents rely on the latter mechanism to discover states containing
> high IR, and the former mechanism to return to them. However, the longer, more complex, and more
> precise a sequence of actions needs to be in order to reach a previously-discovered high-IR state,
> the more likely it is that such stochastic perturbations will “derail” the agent from ever returning to
> that state. That is because the needed precise actions are naively perturbed by the basic exploration
> mechanism, causing the agent to only rarely succeed in reaching the known state to which it is drawn,
> and from which further exploration might be most effective. To address derailment, an insight in
> Go-Explore is that effective exploration can be decomposed into first returning to a promising state
> (without intentionally adding any exploration) before then exploring further.

Go Explore alleviates this problem by, rather than repeatedly exploring from the initial state, returning to prior states as a starting point, and expanding the explored trajectory from that point forwards. However, this assumes that the environment is both *deterministic* and *resettable*.

* A **deterministic** environment is one in which the agent's actions solely determine the state of the environment, ie. taking the same sequence of actions will always lead to the same state. This is in contrast to a **stochastic** environment, in which there is randomness involved in state transitions.
* A **resettable** environment is one in which it is possible to return to a certain state explicitly. In an atari emulator, we can clone and restore the emulator state to accomplish this. Technically, in any deterministic environment, you can just retake the sequence of actions that brought you to the state in question in order to restore it, even if there is no way of explicitly resetting to a particular state.
