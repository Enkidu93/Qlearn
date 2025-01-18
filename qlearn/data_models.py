import json
import random
from abc import ABC, abstractmethod
from pprint import pprint
from typing import Hashable, Optional, Union


class State:
    def __init__(self, qualities: "tuple[Hashable]") -> None:
        self.qualities = qualities

    def __eq__(self, value: object) -> bool:
        return self.qualities == value.qualities


class Action:
    def __init__(
        self,
        value: int,
        name: str = "Nameless action",
        inititalization_value: float = 0.0,
    ) -> None:
        self.value = value
        self.name = name
        self._initialization_value = inititalization_value

    def __hash__(self) -> int:
        return self.value


class ActionTable:
    def __init__(self, initialization_value: float = 0.0, table=None) -> None:
        self._table: "dict[int,float]" = {}
        if table is not None:
            self._table = {int(k): v for k, v in table.items()}
        self._initialization_value = initialization_value

    def __getitem__(self, a: Action):
        if a.value not in self._table:
            self._table[a.value] = self._initialization_value
        return self._table[a.value]

    def __setitem__(self, a: Action, v: float):
        self._table[a.value] = v


class QTable:
    def __init__(self, initialization_value: float = 0.0) -> None:
        self._table: "dict[tuple,ActionTable]" = {}
        self._initialization_value = initialization_value

    def __getitem__(self, s: State):
        if s.qualities not in self._table:
            self._table[s.qualities] = ActionTable(self._initialization_value)
        return self._table[s.qualities]

    def max_q_for(self, s, possible_actions) -> float:
        return max([self[s][a] for a in possible_actions])

    def action_with_max_q_for(self, s, possible_actions) -> float:
        random.shuffle(possible_actions)  # TODO make more efficient
        return max(possible_actions, key=lambda a: self[s][a])

    def update(self, s_prev, a_prev, s, r, alpha, gamma, possible_actions):
        if s_prev is not None and a_prev is not None:
            self[s_prev][a_prev] = self[s_prev][a_prev] + alpha * (
                r + gamma * self.max_q_for(s, possible_actions) - self[s_prev][a_prev]
            )

    def save(self, filename: str):
        data = {str(k): v._table for k, v in self._table.items()}
        with open(filename, "w") as f:
            json.dump(data, f)

    def load(self, filename: str):
        with open(filename, "r") as f:
            data = json.load(f)
        self._table = {eval(k): ActionTable(table=v) for k, v in data.items()}


class Environment(ABC):
    def __init__(
        self,
        possible_actions: "list[Action]",
        quality_definitions: "list[type]",
        starting_state: State,
    ) -> None:
        self.possible_actions = possible_actions
        self.quality_definitions = quality_definitions
        self.starting_state = starting_state
        self.complete = False

    @abstractmethod
    def take_action(self, agent, action) -> "tuple[State, float]":
        if len(self.quality_definitions) != len(agent.state.qualities):
            raise RuntimeError(
                f"State qualities of agent differ from environment-defined quality types in number: {len(agent.state.qualities)} vs {len(self.quality_definitions)}"
            )
        for t, s_q in zip(self.quality_definitions, agent.state.qualities):
            if not isinstance(s_q, t):
                raise RuntimeError(
                    f"State quality {s_q} (which is type {type(s_q)}) is not of environment-defined type {t}"
                )

    @abstractmethod
    def reset(self, agent):  # TODO add agent reset method
        agent.state = self.starting_state
        agent.total_r = 0
        self.complete = False
        agent.action_number = 0


class QAgent:
    def __init__(
        self,
        environment: Environment,
        epsilon: float = 0.5,
        alpha: float = 1.0,
        gamma: float = 1.0,
        epsilon_decay=lambda x: x * 0.99,
        alpha_decay=lambda x: x * 0.99,
        name: str = "Nameless agent",
        decay_after_episodes: Union[int, bool] = 1,
        decay_after_actions: Union[int, bool] = False,
    ) -> None:
        self.environment = environment
        self.state = environment.starting_state
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon_decay = epsilon_decay
        self.alpha_decay = alpha_decay
        self.decay_after_episodes = decay_after_episodes
        self.decay_after_actions = decay_after_actions

        self.episode_number = 0
        self.action_number = 0

        self.name = name

        self.q_table = QTable()
        self.s_prev = None
        self.a_prev = None

        self.total_r = 0

    def take_action(self, action: Optional[Action] = None):
        if action is None:
            if random.random() < self.epsilon:
                action = random.choice(self.environment.possible_actions)
            else:
                action = self.q_table.action_with_max_q_for(
                    self.state, self.environment.possible_actions
                )

        if action not in self.environment.possible_actions:
            raise ValueError(
                f"{action.name} with value {action.value} is not one of the possible actions in this environment. Possible actions are [{self.possible_actions}]"
            )
        s_new, r = self.environment.take_action(self, action)

        self.total_r += r

        self.a_prev = action
        tmp = self.state
        self.state = s_new
        self.s_prev = tmp

        self.q_table.update(
            self.s_prev,
            self.a_prev,
            self.state,
            r,
            self.alpha,
            self.gamma,
            self.environment.possible_actions,
        )

        self.action_number += 1
        if (
            self.decay_after_actions
            and self.action_number > 0
            and (self.action_number % int(self.decay_after_actions)) == 0
        ):
            self.epsilon = self.epsilon_decay(self.epsilon)
            self.alpha = self.alpha_decay(self.alpha)

        if self.environment.complete:
            self.episode_number += 1
            if (
                self.decay_after_episodes
                and self.episode_number > 0
                and (self.episode_number % int(self.decay_after_episodes)) == 0
            ):
                self.epsilon = self.epsilon_decay(self.epsilon)
                self.alpha = self.alpha_decay(self.alpha)

    def save(self):
        self.q_table.save(f"{self.name.replace(' ','')}_qvalues.json")

    def load(self, filename=None):
        if filename is not None:
            self.q_table.load(filename)
        else:
            self.q_table.load(f"{self.name.replace(' ','')}_qvalues.json")
