import math
import random
#################################
# 这个文件里的所有代码是ai生成的
#################################


# Set interactive backend before importing pyplot
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib.collections import LineCollection

# Import Entity class from main.py
import sys
sys.path.insert(0, '/home/happysalt/Documents/evolution_emulator')
import main as main_module
from main import Entity, generateGauss

# Set g before using Entity
main_module.g = 9.98

NUM_ENTITIES = 10
NUM_ROUNDS = 10

# 10 distinct colors for entities
COLORS = ['#e6194b', '#3cb44b', '#4363d8', '#f58231', '#911eb4',
          '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#dcbeff']


def create_visualization():
    # Create entities
    entities = [Entity(i) for i in range(NUM_ENTITIES)]
    for ent in entities:
        ent.reset()

    # State tracking
    state = {
        'round': 0,
        'all_done': False,
        'best_x': 0,
        'best_id': -1,
        'step': 0,
    }

    # Setup figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Ground line
    ax.axhline(y=0, color='brown', linewidth=2, label='Ground')

    # Visual elements for each entity
    visuals = []
    for i, ent in enumerate(entities):
        color = COLORS[i % len(COLORS)]
        body = Circle((ent.x, ent.y), 1.5, color=color, alpha=0.8, zorder=5)
        ax.add_patch(body)
        leg1, = ax.plot([], [], '-', color=color, linewidth=1.5, alpha=0.7)
        leg2, = ax.plot([], [], '-', color=color, linewidth=1.5, alpha=0.7)
        leg3, = ax.plot([], [], '-', color=color, linewidth=1.5, alpha=0.7)
        end1, = ax.plot([], [], 'o', color=color, markersize=4, alpha=0.7)
        end2, = ax.plot([], [], 'o', color=color, markersize=4, alpha=0.7)
        end3, = ax.plot([], [], 'o', color=color, markersize=4, alpha=0.7)
        visuals.append({
            'body': body,
            'leg1': leg1, 'leg2': leg2, 'leg3': leg3,
            'end1': end1, 'end2': end2, 'end3': end3,
            'color': color,
        })

    # Info text
    info_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                        verticalalignment='top', fontsize=11, family='monospace',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

    # Best entity highlight
    best_marker, = ax.plot([], [], '*', color='gold', markersize=20, zorder=10,
                           markeredgecolor='black', markeredgewidth=1, label='Best')

    ax.set_xlim(-20, 100)
    ax.set_ylim(-10, 60)
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_title('Evolution Simulation — 10 Entities × 10 Rounds')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    def reset_round():
        """Reset all entities for a new round."""
        state['all_done'] = False
        state['best_x'] = 0
        state['best_id'] = -1
        state['step'] = 0
        for ent in entities:
            ent.reset()

    def regenerate_round():
        """Find best entity and regenerate all based on it."""
        best_id = -1
        best_x = 0
        for i, ent in enumerate(entities):
            if ent.x > best_x:
                best_x = ent.x
                best_id = i
        state['best_x'] = best_x
        state['best_id'] = best_id

        print(f"\nRound {state['round']}: Best id={best_id}, x={best_x:.2f}")
        print(f"  omega={entities[best_id].omega}")
        print(f"  theta={entities[best_id].theta}")
        print(f"  radicals={entities[best_id].radicals}")

        # Regenerate all entities based on the best one
        for ent in entities:
            ent.regen_entity(entities[best_id].omega, 0.5, 'omega')
            ent.regen_entity(entities[best_id].theta, 0.5, 'theta')
            ent.regen_entity(entities[best_id].radicals, 0.5, 'radicals')

    def init():
        state['round'] = 0
        for ent in entities:
            ent.__init__(ent.id)
            ent.reset()
        state['all_done'] = False
        state['best_x'] = 0
        state['best_id'] = -1
        state['step'] = 0
        return []

    def animate(frame):
        if state['round'] >= NUM_ROUNDS:
            return []

        # Check if all entities are done this round
        all_dead = all(ent.energy <= 0 for ent in entities)
        if all_dead:
            if not state['all_done']:
                state['all_done'] = True
                regenerate_round()
                # Wait a few frames to show final state, then move on
                state['round'] += 1
                if state['round'] >= NUM_ROUNDS:
                    info_text.set_text(
                        f'=== EVOLUTION COMPLETE ===\n'
                        f'Rounds: {NUM_ROUNDS}\n'
                        f'Final Best X: {state["best_x"]:.2f}\n'
                        f'Final Best ID: {state["best_id"]}'
                    )
                    return []
                reset_round()
                return []
            return []

        # Update active entities (5 steps per frame for speed)
        max_x = 0
        for _ in range(5):
            for i, ent in enumerate(entities):
                if ent.energy > 0:
                    ent.update_entity()
        for ent in entities:
            if ent.x > max_x:
                max_x = ent.x

        state['step'] += 1

        # Update visuals
        all_artists = []
        for i, ent in enumerate(entities):
            v = visuals[i]
            # Body
            v['body'].center = (ent.x, ent.y)
            # Dim inactive entities
            alpha = 0.8 if ent.energy > 0 else 0.2
            v['body'].set_alpha(alpha)

            # Legs
            v['leg1'].set_data([ent.x, ent.endpoint1[0]], [ent.y, ent.endpoint1[1]])
            v['leg2'].set_data([ent.x, ent.endpoint2[0]], [ent.y, ent.endpoint2[1]])
            v['leg3'].set_data([ent.x, ent.endpoint3[0]], [ent.y, ent.endpoint3[1]])

            # Endpoints
            v['end1'].set_data([ent.endpoint1[0]], [ent.endpoint1[1]])
            v['end2'].set_data([ent.endpoint2[0]], [ent.endpoint2[1]])
            v['end3'].set_data([ent.endpoint3[0]], [ent.endpoint3[1]])

            for line in [v['leg1'], v['leg2'], v['leg3']]:
                line.set_alpha(0.7 if ent.energy > 0 else 0.15)
            for pt in [v['end1'], v['end2'], v['end3']]:
                pt.set_alpha(0.7 if ent.energy > 0 else 0.15)

            all_artists.extend([v['body'], v['leg1'], v['leg2'], v['leg3'],
                                v['end1'], v['end2'], v['end3']])

        # Show best marker on current leading entity
        alive_entities = [(ent.x, ent.id, i) for i, ent in enumerate(entities) if ent.energy > 0]
        if alive_entities:
            leader = max(alive_entities, key=lambda t: t[0])
            leader_ent = entities[leader[2]]
            best_marker.set_data([leader_ent.x], [leader_ent.y])
        else:
            best_marker.set_data([], [])
        all_artists.append(best_marker)

        # Info text
        alive_count = sum(1 for ent in entities if ent.energy > 0)
        info_text.set_text(
            f'Round: {state["round"] + 1}/{NUM_ROUNDS}\n'
            f'Step: {state["step"]}\n'
            f'Alive: {alive_count}/{NUM_ENTITIES}\n'
            f'Leader X: {max_x:.1f}\n'
            f'Last Best: id={state["best_id"]}, x={state["best_x"]:.1f}'
        )

        # Auto-scale X axis to follow the leading entity
        ax.set_xlim(-20, max(max_x + 30, 100))

        ax.set_title(f'Evolution Simulation — Round {state["round"] + 1}/{NUM_ROUNDS}')

        all_artists.append(info_text)
        return all_artists

    # Create animation
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                    frames=20000, interval=1, blit=False,
                                    repeat=False)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    create_visualization()
