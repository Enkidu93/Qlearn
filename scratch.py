from matplotlib.ticker import AutoMinorLocator
from qlearn.data_models import QAgent, State, Action
from qlearn.environments import ExampleEnvironment, GridWorld, ChaseGridWorld
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pprint import pprint
from tqdm import tqdm

rs = []
gl = []

environment = ChaseGridWorld(25)
agent = QAgent(environment,name="SmartyPants3", epsilon=0.0, alpha=0.0, epsilon_decay=lambda x: x*0.99999955, alpha_decay=lambda x: x*0.99999955)
# agent.load('SmartyPants2_qvalues.json')
for i in tqdm(range(1)):
    agent.state = environment.starting_state
    environment.target_state = environment.target_starting_state
    agent.total_r = 0
    environment.complete = False
    game_length = 0
    # if i!=0:
    # if True:
    #     agent.load()
    if(i%20_000 == 0):# and i!=0):
        fig, ax = plt.subplots()
        ax.set_title(f"Game = {i}")
        circle = plt.Circle((0,0),0.5,fc='r')
        target = plt.Circle((23,23),0.5,fc='b')

        def init():
            ax.set_xlim(0,25)
            ax.set_ylim(0,25)
            ax.set_autoscale_on(True)
            ax.add_artist(circle)
            ax.add_artist(target)
            return circle,

        def animate(i):
            agent.take_action()
            global game_length
            game_length += 1
            circle.center = agent.state.qualities[0:2]
            target.center = environment.target_state.qualities
            return circle,

        def yield_frame():
            while(not environment.complete):
                yield 0

        animation = FuncAnimation(fig, animate, init_func=init, frames=yield_frame, interval=50)
        plt.grid(linewidth=3.0, alpha=0.5, color='grey')
        plt.show()
    else:
        while(not environment.complete):
            agent.take_action()
            game_length += 1

    agent.save()
    # print(f"Saved at{i}")
    rs.append(agent.total_r)
    gl.append(game_length)    
    # print(i, agent.total_r, agent.epsilon, agent.alpha)

plt.plot(rs)
plt.show()
plt.plot(gl)
plt.show()