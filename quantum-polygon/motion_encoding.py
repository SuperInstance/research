"""Motion encoding experiment — evolve polygons over time, encode trajectory.

JEV says (p=0.43): try motion encoding.
Casey asked: "can motion encode novel insights and information beyond spatial theory?"

Hypothesis: polygons that evolve "coherently" (smooth trajectory in state space)
might be more canon-worthy than polygons that jump randomly.
"""
import sys
import json
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, "/workspace/research/quantum-polygon")


def evolve_polygon(seed, n_steps=20, n_vertices=8):
    """Evolve a polygon over time. Each step perturbs the vertex angles."""
    rng = np.random.default_rng(seed)
    
    trajectory = []
    angles = rng.uniform(0, 2 * np.pi, n_vertices)
    angles = np.sort(angles)
    
    for step in range(n_steps):
        # Apply small perturbation
        perturbation = rng.normal(0, 0.1, n_vertices)
        angles += perturbation
        angles = angles % (2 * np.pi)
        angles = np.sort(angles)
        
        trajectory.append(angles.copy())
    
    return np.array(trajectory)  # shape (n_steps, n_vertices)


def trajectory_signature(seed, n_steps=20, n_vertices=8):
    """Compute trajectory features for canon analysis."""
    traj = evolve_polygon(seed, n_steps, n_vertices)  # (20, 8)
    
    # Velocity (step-to-step change)
    velocity = np.diff(traj, axis=0)  # (19, 8)
    velocity_magnitude = np.linalg.norm(velocity, axis=1)  # (19,)
    
    # Acceleration (change in velocity)
    acceleration = np.diff(velocity, axis=0)  # (18, 8)
    accel_magnitude = np.linalg.norm(acceleration, axis=1)  # (18,)
    
    # Coherence: how aligned are the velocities across vertices?
    coherence_values = []
    for v in velocity:
        # If all vertices move in the same direction = coherent
        v_unit = v / (np.linalg.norm(v) + 1e-10)
        alignment = np.abs(np.mean(np.sign(v)))
        coherence_values.append(alignment)
    coherence = float(np.mean(coherence_values))
    
    return {
        'seed': seed,
        'mean_velocity': float(velocity_magnitude.mean()),
        'std_velocity': float(velocity_magnitude.std()),
        'mean_acceleration': float(accel_magnitude.mean()),
        'coherence': coherence,
        'total_motion': float(velocity_magnitude.sum()),
    }


def run_study():
    gm = json.load(open('/workspace/research/substrate-walker/playtest/great_moments.json'))
    canon_seeds = [m['seed'] for m in sorted(gm, key=lambda x: -x.get('score', 0))[:30]]
    
    import random
    random.seed(42)
    random_seeds = random.sample(range(1, 100_000_000), 30)
    
    print("Canon trajectories:")
    canon_sigs = []
    for seed in canon_seeds:
        sig = trajectory_signature(seed)
        canon_sigs.append(sig)
        print(f"  seed {seed}: v_mean={sig['mean_velocity']:.3f} coherence={sig['coherence']:.3f}")
    
    print("\nRandom trajectories:")
    random_sigs = []
    for seed in random_seeds:
        sig = trajectory_signature(seed)
        random_sigs.append(sig)
        print(f"  seed {seed}: v_mean={sig['mean_velocity']:.3f} coherence={sig['coherence']:.3f}")
    
    from statistics import mean, stdev
    canon_coh = [s['coherence'] for s in canon_sigs]
    random_coh = [s['coherence'] for s in random_sigs]
    canon_vel = [s['mean_velocity'] for s in canon_sigs]
    random_vel = [s['mean_velocity'] for s in random_sigs]
    
    print(f"\n=== MOTION ENCODING RESULTS ===")
    print(f"Canon coherence:  mean={mean(canon_coh):.4f} std={stdev(canon_coh):.4f}")
    print(f"Random coherence: mean={mean(random_coh):.4f} std={stdev(random_coh):.4f}")
    print(f"Coherence diff:   {mean(canon_coh) - mean(random_coh):+.4f}")
    print(f"\nCanon velocity:   mean={mean(canon_vel):.4f}")
    print(f"Random velocity:  mean={mean(random_vel):.4f}")
    print(f"Velocity diff:    {mean(canon_vel) - mean(random_vel):+.4f}")
    
    output = {
        'canon': canon_sigs,
        'random': random_sigs,
        'canon_mean_coherence': mean(canon_coh),
        'random_mean_coherence': mean(random_coh),
        'canon_mean_velocity': mean(canon_vel),
        'random_mean_velocity': mean(random_vel),
    }
    with open('/workspace/research/quantum-polygon/motion_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    return output


if __name__ == "__main__":
    run_study()
