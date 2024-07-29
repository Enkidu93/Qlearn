from qlearn.data_models import Environment, Action, State

class ExampleEnvironment(Environment):
    def __init__(self) -> None:
        super().__init__([Action(0, "Get money"), Action(1, "Right"), Action(2, "Left")], [int], State(tuple([0])))
    def take_action(self, agent, action) -> float:
        super().take_action(agent, action)
        if action.value == 0 and agent.state.qualities[0] == 2:
            self.complete = True
            return State(tuple([1])), 1.0
        elif action.value == 1:
            return State(tuple([min(2,agent.state.qualities[0]+1)])), -0.01
        elif action.value == 2:
            return State(tuple([max(0,agent.state.qualities[0]-1)])), -0.01
        return agent.state, -0.01