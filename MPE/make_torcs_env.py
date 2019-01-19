import gym
from gym import spaces
import numpy as np
from torcs_world import World, Agent
# environment for all agents in the multiagent world
# currently code assumes that no agents will be created/destroyed at runtime!
from OU import OU

OU = OU()       #Ornstein-Uhlenbeck Process

class MultiAgentTorcsEnv():

    def __init__(self, world, adv=0, reset_callback=None, reward_callback=None,
                 observation_callback=None, info_callback=None,
                 done_callback=None):

        self.world = world
        self.agents = self.world.agent_list

        # set required vectorized gym env property
        self.n = world.n
        self.adv = adv
        # scenario callbacks
        self.reset_callback = reset_callback
        self.reward_callback = reward_callback
        self.observation_callback = observation_callback
        self.info_callback = info_callback
        self.done_callback = done_callback

        # environment parameters
        self.discrete_action_space = True
        # if true, action is a number 0...N, otherwise action is a one-hot N-dimensional vector
        self.discrete_action_input = True
        # if true, even the action is continuous, action will be performed discretely
        self.force_discrete_action = False 

        # if true, every agent has the same reward
        self.shared_reward = False
        self.time = 0

        # configure spaces
        self.action_space = []
        self.observation_space = []

        for agent in self.agents:
            self.action_space.append(world.action_space)
            # observation space
            #obs_dim = len(observation_callback(agent, self.world))
            self.observation_space.append(world.observation_space)
            #agent.action.c = np.zeros(self.world.dim_c)

    def step(self, action_n, e, t):
        obs_n = []
        reward_n = []
        done_n = []
        info_n = {'n': []}
        self.agents = self.world.agent_list

        # set action for each agent
            agent.action = action_n[i] 

        # advance world state
        self.world.stepWorld()         
        # record observation for each agent
        for agent in self.agents:
            obs_n.append(self._get_obs(agent))
            reward_n.append(self._get_reward(agent))
            done_n.append(self._get_done(agent))
            info_n['n'].append(self._get_info(agent))

        # all agents get total reward in cooperative case
        reward = np.sum(reward_n)
        if self.shared_reward:
            reward_n = [reward] * self.n

        return obs_n, reward_n, done_n, info_n

    def reset(self):
        # reset world
        self.reset_callback()
        # record observations for each agent
        obs_n = []
        self.agents = self.world.agent_list
        for agent in self.agents:
            obs_n.append(self._get_obs(agent))
        return obs_n

    # get info used for benchmarking
    def _get_info(self, agent):
        if self.info_callback is None:
            return {}
        return self.info_callback(agent, self.world)

    # get observation for a particular agent
    def _get_obs(self, agent):
        if self.observation_callback is None:
            return np.zeros(0)
        return self.observation_callback(agent)

    # get dones for a particular agent
    def _get_done(self, agent):
        if self.done_callback is None:
            return False
        return self.done_callback(agent)

    # get reward for a particular agent
    def _get_reward(self, agent):
        if self.reward_callback is None:
            return 0.0
        return self.reward_callback(agent)


