from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
"""Simple example of using ArenaRllibEnv, which is a interface that
convert a arena environment to a MultiAgentEnv
(see: https://ray.readthedocs.io/en/latest/rllib-env.html#multi-agent-and-hierarchical)
interface by rllib.
"""

import numpy as np

from envs_layer import ArenaRllibEnv


def main():

    env_config = {
        "env_id": "Tennis-Sparse-2T1P-Discrete",
        "is_shuffle_agents": True,
        "train_mode": False,
    }
    env = ArenaRllibEnv(env_config)

    # Observations are a dict mapping agent names to their obs. Not all agents
    # may be present in the dict in each time step.
    # print(env.reset())
    # {
    #     "agent_0": [[...]],
    #     "agent_1": [[...]],
    # }

    while True:
        # Actions should be provided for each agent that returned an observation.
        new_obs, rewards, dones, infos = env.step(
            actions={"agent_0": 0, "agent_1": 5})

        new_obs_shapes = {}
        for key in new_obs.keys():
            new_obs_shapes[key] = np.shape(new_obs[key])

        print("new_obs_shapes: {}".format(new_obs_shapes))
        # new_obs_shapes: {'agent_0': (84, 84, 1), 'agent_1': (84, 84, 1)}

        print("rewards: {}".format(rewards))
        # rewards: {"agent_0": 3, "agent_1": -1}

        # Individual agents can early exit; env is done when "__all__" = True
        print("dones: {}".format(dones))
        # dones: {"agent_0": True, "agent_1": False,, "__all__": True}

        print("infos: {}".format(infos))

        if dones["__all__"]:
            input('episode end, keep going?')
            env.reset()


if __name__ == '__main__':
    main()