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

This is disadvantageous because many real-world tasks involve a great amount of stochasticity (randomness), so this restriction upon environments that are deterministic and resettable is an issue. The authors note the fact that most future applications of Reinforcement Learning will first involved a simulator before being deployed into the real world. Therefore, in many situations, we can infact rely on the assumption that we have a deterministic test environment. However, in the case that we do not, and the agent is forced to explore in a stochastic world, we cannot exploit determinism and resettability. In this case, the authors say, we can use goal-conditioned policies to return to the cells themselves. This is a problem for future work:

> There are also cases where a simulator is not available and where learning algorithms must confront
> stochasticity during training. To create and test algorithms for this second type of problem, we cannot
> exploit determinism and resettability. Examples of this class of problems include when we must
> learn directly in the real world (and an effective simulator is not available and cannot be learned),
> or when studying the learning of biological animals, including ourselves. We believe Go-Explore
> can handle such situations by training goal-conditioned policies [62, 63] that reliably return to cells
> in the archive during the exploration phase, which is an interesting area for future research. While
> computationally much more expensive, this strategy would result in a fully trained policy at the end
> of the exploration phase, meaning there would be no need for a robustification phase at the end. We
> note that there are some problems where the environment has forms of stochasticity that prevent the
> algorithm from reliably returning to a particular cell, regardless of which action the agent takes (e.g.
> in poker, there is no sequence of actions that reliably leads you to a state where you have two aces).
> We leave a discussion and study of whether Go-Explore helps in that problem setting for future work.

### How the algorithm works
Go explore involves sampling random trajectories, recording visitted states, and then returning to a certain state based upon a special heuristic. Over time, the algorithm experiences a wide variety of states that encompass the entire environment. This provides for diverse exploration that is not conditioned upon any reward signal.

There are an intractably large number of possible states, considering a *state* in this case is represented by some RGB pixel image. For this reason, the authors downscale frames into **cells**, and store these in an archive as new ones are found.
<img src="https://i.ibb.co/dWnMyyr/downscale-vis-horiz.png" alt="downscale-vis-horiz" border="0" style="display:block;margin-left:auto;margin-right:auto;">

> One could, in theory, run Go-Explore directly in a high-dimensional state space (wherein each cell
> contains exactly one state); however doing so would be intractable in practice. To be tractable in
> high-dimensional state spaces like Atari, Phase 1 of Go-Explore needs a lower-dimensional space
> within which to search (although the final policy will still play in the same original state space, in this
> case pixels). Thus, the cell representation should conflate similar states while not conflating states
> that are meaningfully different.
> In this way, a good cell representation should reduce the dimensionality of the observations into a
> meaningful low-dimensional space. A rich literature investigates how to obtain good representations
> from pixels. One option is to take latent codes from the middle of neural networks trained with
> traditional RL algorithms maximizing extrinsic and/or intrinsic motivation, optionally adding auxiliary
> tasks such as predicting rewards [52]. Additional options include unsupervised techniques such
> as networks that autoencode [53] or predict future states, and other auxiliary tasks such as pixel
> control [54].

After a cell is returned to, up to 100 random actions are taken. The iteration of exploration from that cell terminates after either 100 steps, or reaching a terminal state, whichever comes first. At each step, the algorithm repeats the previous action with 95% probability. Otherwise, it performs a new random action. This permits the agent to actually move, rather than remaining overall stationary while jittering back and forth due to the effects of sampling repeatedly from a uniform probability distribution across the action space.

<img src="https://i.ibb.co/9hGb4Zt/high-level-overview-v2-1.jpg" alt="high-level-overview-v2-1" border="0" style="display:block;margin-left:auto;margin-right:auto;">

The authors determine that a special return heuristic for selecting cells to explore from improves upon simply random selection. Their heuristic incorperates 3 factors that are weighted separately. The heuristic assigns a positive weight to each cell discovered thus far that is higher for cells that are deemed more promising. The attributes taken into account are as follows:

1. Cells that have been visited less often (at any time during the exploration phase) are deemed more promising
2. Cells that have been explicitly returned to less often are more promising
3. Cells that have recently contributed to discovering a new cell are considered more promising

The exact formulae for computing the cell selection probabilities are irrelevant for this brief overview, but they can be found in the paper.

Once the algorithm has run for quite some time, it will have explored an abundance of trajectories. If the environment in which the agent will be deployed is stochastic, these trajectories might not be robust to function in them. For example, taking a high-scoring trajectory explored during the exploration phase might not always lead to the same state in a stochastic version of the environment. If this is the case, then simply repeating these high-reward trajectories won't work on its own. Instead, we conduct imitation learning to train an agent to replicate these high-performing trajectories without being susceptible to this added stochasticity. Ultimately, we'd have an agent capable of achieving high reward in a stochastic, sparse-reward environment.
