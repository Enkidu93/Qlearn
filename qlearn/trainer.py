from typing import Callable, Optional
from .data_models import Environment, QAgent
from tqdm import tqdm

class QLearnTrainer:
    def __init__(self, environment: Environment, agent: QAgent):
        self.environment = environment
        self.agent = agent

    def train(self, num_episodes: Optional[int] = None, num_actions: Optional[int] = None, get_replay: Callable[[QAgent, Environment],None] = None, get_replay_interval:Optional[int] = None, load_preexisting_agent: bool = False) -> tuple[list[float], list[int]]:
        assert bool(num_episodes)^bool(num_actions), "Exactly one of episodes and num_actions must be set"
        rewards = []
        game_lengths = []
        if num_actions:
            agent_actions = 0
            while(True): #TODO refactor to a single loop; move logic to methods
                self.environment.reset(self.agent)
                if self.agent.action_number > 0 or load_preexisting_agent:
                        self.agent.load()
                while(not self.environment.complete):
                    game_length = 0
                    if self.agent.action_number > 0:
                        if get_replay_interval is not None and (i % get_replay_interval) == 0:
                            get_replay(self.agent, self.environment)
                    self.agent.take_action()
                    agent_actions += 1
                    game_length += 1
                    if agent_actions >= num_actions:
                        break

                self.agent.save()
                rewards.append(self.agent.total_r)
                game_lengths.append(game_length)

                if agent_actions >= num_actions:
                    break

        if num_episodes:
            for i in tqdm(range(num_episodes)):
                self.environment.reset(self.agent)
                game_length = 0
                if i > 0 or load_preexisting_agent:
                        self.agent.load()
                while(not self.environment.complete):
                    if self.agent.action_number > 0:
                        if get_replay_interval is not None and (i % get_replay_interval) == 0:
                            get_replay(self.agent, self.environment)
                    self.agent.take_action()
                    game_length += 1
                self.agent.save()
                rewards.append(self.agent.total_r)
                game_lengths.append(game_length)
        
        return rewards, game_lengths


  