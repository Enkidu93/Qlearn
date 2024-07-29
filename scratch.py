from qlearn.data_models import QAgent, State, Action
from qlearn.environments import ExampleEnvironment
import matplotlib.pyplot as plt
from pprint import pprint

rs = []
gl = []

environment = ExampleEnvironment()
agent = QAgent(environment,name="SmartyPants", epsilon=0.5, alpha=0.5, epsilon_decay=lambda x: x*0.995, alpha_decay=lambda x: x*0.995)
for i in range(500):
    agent.state = State(tuple([0]))
    agent.total_r = 0
    environment.complete = False

    if i!=0:
        agent.load()

    game_length = 0
    while(not environment.complete):
        agent.take_action()
        game_length+=1
        # print(f"{agent.name} took action {agent.a_prev.name}")
    agent.save()
    rs.append(agent.total_r)
    gl.append(game_length)    
    print(i, agent.total_r, agent.epsilon, agent.alpha)

plt.plot(rs)
plt.show()
plt.plot(gl)
plt.show()