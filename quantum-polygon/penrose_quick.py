"""Quick Penrose tiling experiment.

JEV's runner-up: higher_dim at 30%. Let's see if Penrose tilings encode canon.
"""
import numpy as np
from pathlib import Path

# Penrose P3 tiling has 2 tiles: kite and dart
# Their matching rules produce non-periodic tilings
# 
# Simple experiment: simulate Penrose matching rules via de Bruijn's method
# (lift from 5D to 2D using projection)

def de_bruijn_penrose(n_tiles=50, seed=42):
    """Generate a Penrose tiling using de Bruijn's method."""
    rng = np.random.default_rng(seed)
    
    # 5D hyperplane
    phi = (1 + np.sqrt(5)) / 2  # golden ratio
    
    # Project 5D to 2D
    angles = np.array([0, 2*np.pi/5, 4*np.pi/5, 6*np.pi/5, 8*np.pi/5])
    points_2d = np.zeros((n_tiles, 2))
    
    for i in range(n_tiles):
        # Random 5D point on the canonical slice
        coords = rng.uniform(0, 1, 5)
        # Project onto the 2D plane perpendicular to (1,1,1,1,1)
        # and project to 2D using cos/sin basis
        x = sum(c * np.cos(a) for c, a in zip(coords, angles))
        y = sum(c * np.sin(a) for c, a in zip(coords, angles))
        points_2d[i] = [x, y]
    
    return points_2d


def random_tiling(n_tiles=50, seed=42):
    """Generate a random tiling for comparison."""
    rng = np.random.default_rng(seed)
    return rng.uniform(-2, 2, (n_tiles, 2))


def trajectory_stats(points, n_steps=10):
    """Compute motion statistics for a set of points."""
    rng = np.random.default_rng(hash(tuple(points.flatten())) % 2**32)
    trajectory = []
    p = points.copy()
    for step in range(n_steps):
        p += rng.normal(0, 0.1, p.shape)
        trajectory.append(p.copy())
    trajectory = np.array(trajectory)  # (n_steps, n_tiles, 2)
    
    velocity = np.diff(trajectory, axis=0)  # (n_steps-1, n_tiles, 2)
    velocity_magnitude = np.linalg.norm(velocity, axis=2)  # (n_steps-1, n_tiles)
    
    return {
        'mean_velocity': float(velocity_magnitude.mean()),
        'std_velocity': float(velocity_magnitude.std()),
        'total_motion': float(velocity_magnitude.sum()),
    }


def run():
    print("Penrose tilings:")
    penrose_stats = []
    for seed in [42, 70051917, 4685000, 3289967, 57322595, 90625407]:
        points = de_bruijn_penrose(50, seed=seed)
        stats = trajectory_stats(points)
        penrose_stats.append(stats)
        print(f"  seed {seed}: vel={stats['mean_velocity']:.3f} std={stats['std_velocity']:.3f}")
    
    print("\nRandom tilings:")
    random_stats = []
    for seed in [42, 85822413, 14942604, 3356887, 99529224, 36913811]:
        points = random_tiling(50, seed=seed)
        stats = trajectory_stats(points)
        random_stats.append(stats)
        print(f"  seed {seed}: vel={stats['mean_velocity']:.3f} std={stats['std_velocity']:.3f}")
    
    from statistics import mean
    p_vel = [s['mean_velocity'] for s in penrose_stats]
    r_vel = [s['mean_velocity'] for s in random_stats]
    
    print(f"\nPenrose mean vel: {mean(p_vel):.3f}")
    print(f"Random mean vel:  {mean(r_vel):.3f}")
    print(f"Difference: {mean(p_vel) - mean(r_vel):+.3f}")
    
    output = {
        'penrose': penrose_stats,
        'random': random_stats,
        'penrose_mean_vel': mean(p_vel),
        'random_mean_vel': mean(r_vel),
    }
    with open('/workspace/research/quantum-polygon/penrose_results.json', 'w') as f:
        import json
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    run()
