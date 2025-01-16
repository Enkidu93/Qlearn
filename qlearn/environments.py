from typing import Optional
from .data_models import Environment, Action, State, QAgent
from numpy import sign
import random
class ExampleEnvironment(Environment):
    def __init__(self) -> None:
        super().__init__([Action(0, "Get money"), Action(1, "Right"), Action(2, "Left")], [int], State(tuple([0])))
    def take_action(self, agent, action) -> 'tuple[State, float]':
        super().take_action(agent, action)
        if action.value == 0 and agent.state.qualities[0] == 2:
            self.complete = True
            return State(tuple([1])), 1.0
        elif action.value == 1:
            return State(tuple([min(2,agent.state.qualities[0]+1)])), -0.01
        elif action.value == 2:
            return State(tuple([max(0,agent.state.qualities[0]-1)])), -0.01
        return agent.state, -0.01
    
    def reset(self, agent: QAgent):
        return super().reset(agent)
    
class GridWorld(Environment):
    def __init__(self, size:int, quality_definitions:Optional[list[type]]=None) -> None:
        if size < 2:
            raise ValueError('Size must be greater than 1')
        super().__init__([Action(0, 'Right'),Action(1, 'Down'),Action(2, 'Left'),Action(3, 'Up')], [int,int] if quality_definitions is None else quality_definitions, State((0,0)))
        self.size = size
    def take_action(self, agent:QAgent, action) -> 'tuple[State, float]':
        super().take_action(agent, action)
        asq = agent.state.qualities
        s, r = None,None
        if action.value == 0:
            s,r = State(((asq[0], max(asq[1]-1,0)))), -0.01
        elif action.value == 1:
            s,r = State((max(asq[0]-1, 0), asq[1])), -0.01
        elif action.value == 2:
            s,r = State((asq[0],  min(asq[1]+1,self.size-1))), -0.01
        else:
            s,r = State((min(asq[0]+1,self.size-1),  asq[1])), -0.01
        
        if s.qualities[0] == self.size-1 and s.qualities[1] == self.size-1:
            r = 10
            self.complete = True
        return s, r
    def reset(self, agent: QAgent):
        super().reset(agent)        

class ChaseGridWorld(GridWorld):
    def __init__(self, size: int) -> None:
        if size < 4:
            raise ValueError('Size must be greater than 1')
        super().__init__(size, quality_definitions=[int,int,int,int])
        self.target_starting_state = State((self.size-2, self.size-2))
        self.target_state = self.target_starting_state
        self.starting_state = State((0,0,1,1))
    def update_target(self):
        right_spacing = 1
        top_spacing = 1
        left_spacing = 1
        bottom_spacing = 1
        if random.random() < 0.5:
            right_spacing = random.choice(list(range(0,self.size//2)))
            top_spacing = random.choice(list(range(0,self.size//2)))
            left_spacing = random.choice(list(range(0,self.size//2)))
            bottom_spacing = random.choice(list(range(0,self.size//2)))

        if self.target_state.qualities[0] == self.size - 1 - right_spacing:
            if self.target_state.qualities[1] == self.size - 1 - top_spacing:
                self.target_state = State((self.target_state.qualities[0]-1,self.target_state.qualities[1]))
            else:
                self.target_state = State((self.target_state.qualities[0],self.target_state.qualities[1]+1))

        elif self.target_state.qualities[1] == self.size - 1 - top_spacing:
            if self.target_state.qualities[0] == left_spacing:
                self.target_state = State((self.target_state.qualities[0],self.target_state.qualities[1]-1))
            else:
                self.target_state = State((self.target_state.qualities[0]-1,self.target_state.qualities[1]))
        elif self.target_state.qualities[0] == left_spacing:
            if self.target_state.qualities[1] == bottom_spacing:
                self.target_state = State((self.target_state.qualities[0]+1,self.target_state.qualities[1]))
            else:
                self.target_state = State((self.target_state.qualities[0],self.target_state.qualities[1]-1))
        elif self.target_state.qualities[1] == bottom_spacing: 
            if self.target_state.qualities[0] == self.size - 1 - right_spacing:
                self.target_state = State((self.target_state.qualities[0],self.target_state.qualities[1]+1))
            else:
                self.target_state = State((self.target_state.qualities[0]+1,self.target_state.qualities[1]))

        if self.target_state.qualities[0] > self.size - 1:
            self.target_state = State((self.size-right_spacing,self.target_state.qualities[1]))
        if self.target_state.qualities[0] < 0:
            self.target_state = State((left_spacing,self.target_state.qualities[1]))
        if self.target_state.qualities[1] > self.size - 1:
            self.target_state = State((self.target_state.qualities[0],self.size-top_spacing))
        if self.target_state.qualities[1] < 0:
            self.target_state = State((self.target_state.qualities[0],bottom_spacing))

    def take_action(self, agent: QAgent, action) -> 'tuple[State, float]':
        s,r = super().take_action(agent, action)
        self.complete = False
        if r == 10:
            r = -0.01
        self.update_target()
        if s == self.target_state:
            r = 10
            self.complete = True
        s = State((s.qualities[0], s.qualities[1], int(sign(self.target_state.qualities[0]-s.qualities[0])), int(sign(self.target_state.qualities[1]-s.qualities[1]))))
        return s, r
    
    def reset(self, agent):
        super().reset(agent)
        self.target_state = self.target_starting_state
        