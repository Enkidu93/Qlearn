from matplotlib.ticker import AutoMinorLocator
from qlearn.data_models import QAgent, State, Action
from qlearn.environments import ExampleEnvironment, GridWorld, ChaseGridWorld
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from qlearn.trainer import QLearnTrainer

environment = ChaseGridWorld(10)
agent = QAgent(environment,name="TestAgent", epsilon=1.0, alpha=1.0, epsilon_decay=lambda x: x*0.995, alpha_decay=lambda x: x*0.995)
trainer = QLearnTrainer(environment, agent)
rewards, game_lengths = trainer.train(num_episodes=1_000)
plt.plot(rewards)
plt.show()
plt.plot(game_lengths)
plt.show()


# ANIMATE
# fig, ax = plt.subplots()
# ax.set_title(f"Game = {i}")
# circle = plt.Circle((0,0),0.5,fc='r')
# target = plt.Circle((23,23),0.5,fc='b')

# def init():
#     ax.set_xlim(0,25)
#     ax.set_ylim(0,25)
#     ax.set_autoscale_on(True)
#     ax.add_artist(circle)
#     ax.add_artist(target)
#     return circle,

# def animate(i):
#     agent.take_action()
#     global game_length
#     game_length += 1
#     circle.center = agent.state.qualities[0:2]
#     target.center = environment.target_state.qualities
#     return circle,

# def yield_frame():
#     while(not environment.complete):
#         yield 0

# animation = FuncAnimation(fig, animate, init_func=init, frames=yield_frame, interval=50, save_count=100)
# plt.grid(linewidth=3.0, alpha=0.5, color='grey')
# plt.show()