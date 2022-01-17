import numpy as np
import matplotlib.pyplot as plt
import sys
from random import random

np.set_printoptions(threshold=sys.maxsize, linewidth=300)

actions = {
    '↑': lambda x, y, maze: (x - 1 if x > 0 else 0, y),
    '→': lambda x, y, maze: (x, y + 1 if y < np.size(maze, 1) - 1 else y),
    '↓': lambda x, y, maze: (x + 1 if x < np.size(maze, 0) - 1 else x, y),
    '←': lambda x, y, maze: (x, y - 1 if y > 0 else 0),
}


rewards = {
    '.': -1,
    '#': -100,
    'S': -1,
    'F': 100,
}


def split_chars(string) -> list:
    result = []
    result[:0] = string
    return result


def get_maze(filename):
    txt = open(filename, 'r')
    rows = list(map(
        lambda row: split_chars(row.replace('\n', '')),
        txt.readlines(),
    ))
    txt.close()
    return np.array(rows)


def get_start(maze) -> tuple:
    [x_start], [y_start] = np.where(maze == 'S')
    return x_start, y_start


def get_rewards(maze):
    return np.array([
        np.array([
            rewards[el]
            for el in row
        ])
        for row in maze
    ])


def init_qs(maze):
    return np.array([
        np.array([
            {
                '↑': 0,
                '→': 0,
                '↓': 0,
                '←': 0,
            }
            for el in row
        ]) for row in maze
    ])


def is_terminal(state, maze) -> bool:
    return maze[state] in ['#', 'F']


def choose_action(state, qs, eps) -> str:
    actions_rating = qs[state]
    return (
        max(actions_rating, key=actions_rating.get) if random() > eps
        else np.random.choice(['↑', '→', '↓', '←'])
    )


def choose_best_action(*args):
    return choose_action(*args, eps=0)


def get_str_path(maze, qs):
    state = get_start(maze)
    path = [str(state)]
    maze_with_path = maze.copy()
    while not is_terminal(state, maze):
        action = choose_best_action(state, qs)
        if maze[state] != 'S':
            maze_with_path[state] = action
        state = actions[action](*state, maze)
        path.append(str(state))
    str_path = ' -> '.join(path)
    str_maze_with_path = '\n'.join([
        ''.join(row)
        for row in maze_with_path
    ])
    return str_path, str_maze_with_path


def train(maze, discount, eps, rate, n_iterations):
    qs = init_qs(maze)
    n_steps = []
    n_rewards = []
    for iteration in range(n_iterations):
        state = get_start(maze)
        i_steps = 0
        i_rewards = 0
        while not is_terminal(state, maze):
            action = choose_action(state, qs, eps)
            next_state = actions[action](*state, maze)
            reward = rewards[maze[next_state]]
            future_actions_ratings = qs[next_state]
            max_future_action_rating = max(future_actions_ratings.values())

            # updating Q
            qs[state][action] = (1 - rate) * qs[state][action] + rate * (reward + discount * max_future_action_rating)

            state = next_state
            i_steps += 1
            i_rewards += reward
        n_steps.append(i_steps)
        n_rewards.append(i_rewards)

    return qs, np.array(n_steps), np.array(n_rewards)


def main():
    filename = 'maze1.txt'
    maze = get_maze(filename)
    maze_x_size, maze_y_size = np.size(maze, 1), np.size(maze, 0)
    eps = 0.05
    discount = 0.5
    rate = 0.9
    n_iterations = 600

    qs, n_steps, n_rewards = train(maze, discount, eps, rate, n_iterations)

    fig, (top_ax, bottom_ax) = plt.subplots(2)
    fig.suptitle(
        f'QL {maze_x_size}X{maze_y_size}. eps = {eps}, discount = {discount}, l_rate = {rate}, iterations = {n_iterations}'
    )
    top_ax.bar(x=range(n_iterations), height=n_steps)
    top_ax.set_title('Steps made in each train iteration')
    bottom_ax.bar(x=range(n_iterations), height=n_rewards, color='#ff9933')
    bottom_ax.set_title('Total reward in each train iteration')
    fig.tight_layout()
    plt.savefig(f'./images/figure_{filename}_eps{eps}_disc{discount}_rate{rate}_iters{n_iterations}.png')

    str_path, str_maze_with_path = get_str_path(maze, qs)

    print(str_maze_with_path)
    print('Plan:')
    print(str_path)


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
