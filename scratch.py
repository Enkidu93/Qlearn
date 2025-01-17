from matplotlib.ticker import AutoMinorLocator
from qlearn.data_models import QAgent, State, Action
from qlearn.environments import ExampleEnvironment, GridWorld, ChaseGridWorld, Environment
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from qlearn.trainer import QLearnTrainer

environment = ChaseGridWorld(25)
agent = QAgent(environment,name="TestAgentChase25", epsilon=1.0, alpha=1.0, epsilon_decay=lambda x: x*0.99994, alpha_decay=lambda x: x*0.999975)
trainer = QLearnTrainer(environment, agent)

REPLAY_INTERVAL=5_000
replays = []
prev_episode_number = -1
def get_replay(agent:QAgent, environment:Environment):
    global prev_episode_number
    if agent.episode_number > prev_episode_number:
        replays.append([])
        prev_episode_number = agent.episode_number
    if 'target_state' in environment.__dict__:
        replays[-1].append((agent.state.qualities[0:2], environment.target_state.qualities))
    else:
        replays[-1].append(tuple([agent.state.qualities[0:2]]))

rewards, game_lengths = trainer.train(num_episodes=80_000, get_replay=get_replay, get_replay_interval=REPLAY_INTERVAL)
plt.plot(rewards)
plt.show()
plt.plot(game_lengths)
plt.show()

for i, replay in enumerate(replays):
    fig, ax = plt.subplots()
    ax.set_title(f"Episode = {(i+1)*REPLAY_INTERVAL}")
    circle = plt.Circle((environment.starting_state.qualities[0], environment.starting_state.qualities[1]),0.5*(environment.size/25),fc='r')
    if 'target_state' in environment.__dict__:
        target = plt.Circle((environment.target_starting_state.qualities[0], environment.target_starting_state.qualities[1]),0.5*(environment.size/25),fc='b')
        ax.add_artist(target)
    ax.set_xlim(0,environment.size)
    ax.set_ylim(0,environment.size)
    ax.set_autoscale_on(True)
    ax.add_artist(circle)

    def animate(ix):
        circle.center = replay[ix][0]
        if 'target_state' in environment.__dict__:
            target.center = replay[ix][1]
        return circle,

    animation = FuncAnimation(fig, animate, frames=len(replay), interval=75)
    plt.grid(linewidth=3.0, alpha=0.5, color='grey')
    plt.show()