import gym
from gym import spaces
import numpy as np
import snakeoil3_gym as snakeoil3
import os
import time
from gym_torcs import TorcsEnv

class Agent(object):
      def __init__(self,idx=0):
          self.idx = idx
          self.port = 3101+self.idx
          self.action_dim = 3
          self.state_dim = 65
          self.obs = []
          self.client = snakeoil3.Client(p=self.port, vision=False)
          self.s_t = []
          self.r_t = 0
          self.done = 0
          self.action = [0,1,0]
          self.client.MAX_STEPS = np.inf

class World(object):
      def __init__(self):
          self.n = 4
          #self.n2 = 0
          self.env = TorcsEnv(vision=False, throttle=True, gear_change=False)
          self.observation_space = self.env.observation_space # basically this is one agents' action space 
          self.action_space = self.env.action_space
          self.step_count = 0 
          self.agent_list = []
          #self.agent2_list = []
          self.initialize_agents()
       

      def initialize_agents(self):  
          self.agent_list = []
          #self.agent2_list = []        
          for i in range(self.n):
              agent = Agent(idx = i) 
              #agent.s_t = self.get_initial_observation(agent,0) #can remove step from here, can even remove the function
              self.agent_list.append(agent)
  
          ''' for i in range(self.n2):			#uncomment this for competitive agents
              agent = Agent(idx = i + self.n) 
              #agent.s_t = self.get_initial_observation(agent,0)
              self.agent2_list.append(agent)'''

          for i in range(self.n):              
              self.agent_list[i].s_t = self.get_initial_observation(self.agent_list[i],0) #can remove step from here, can even remove the function
              
          '''for i in range(self.n2):                   #uncomment this for competitive agents
              self.agent2_list[i].s_t = self.get_initial_observation(self.agent2_list[i],0)'''
      def reset_agents(self):
          for i in range(self.n):
              self.agent_list[i].client.R.d['meta'] = True
        
      def get_initial_observation(self, agent,step_count=0):
          agent.client.get_servers_input(step_count)
          obs = agent.client.S.d
          ob = self.env.make_observation(obs)
          agent.s_t = np.hstack((ob.angle, ob.track, ob.trackPos, ob.speedX, ob.speedY,  ob.speedZ, ob.wheelSpinVel/100.0, ob.rpm, ob.opponents))
          return agent.s_t

      def update_agent_state(self, agent):  #this should be a function in agent class
          print("agent port " + str(agent.port) + "  " + "action is " + str(agent.action))
          ob, r_t, done, info = self.env.step(self.step_count, agent.client, agent.action, early_stop=0)
          agent.done = done
          agent.r_t = r_t
          agent.s_t = np.hstack((ob.angle, ob.track, ob.trackPos, ob.speedX, ob.speedY,  ob.speedZ, ob.wheelSpinVel/100.0, ob.rpm, ob.opponents))

      def reset_world(self):
          self.reset_agents()
          self.env.reset_torcs()
          self.initialize_agents() # check if self required here

      def stepWorld(self):
          for agent in self.agent_list:
                self.update_agent_state(agent)
              
      def reward(self,agent):
          return agent.r_t

      def observation(self,agent):
          return agent.s_t

      def done(self, agent):
          return agent.done
          

