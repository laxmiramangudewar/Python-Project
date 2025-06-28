import random
import matplotlib.pyplot as plt

def simulate_preference_drift_stable(V, delta, base):
    """
    Simulate valuation drift around initial preferences to keep values moderate.
    Each value moves within [base - delta, base + delta], clipped at 0.
    """
    for i in range(len(V)):
        for j in range(len(V[i])):
            drift = random.uniform(-delta, delta)
            V[i][j] = max(0, base[i][j] + drift)
    return V

def is_EF1(i, j, allocation, valuations):
    """
    Check if agent i envies agent j beyond EF1 condition.
    """
    val_i = sum(valuations[i][item] for item in allocation[i])
    val_j_items = sorted(allocation[j], key=lambda item: valuations[i][item], reverse=True)
    if not val_j_items:
        return True
    val_j_minus_most = sum(valuations[i][item] for item in val_j_items[1:])
    return val_i >= val_j_minus_most

def greedy_local_EF1_restore(allocation, valuations, min_transfer_diff=0):
    """
    Fix EF1 violations by transferring most envied items only if transfer
    improves recipient satisfaction by min_transfer_diff.
    """
    changed = False
    for i in range(len(allocation)):
        for j in range(len(allocation)):
            if i != j and not is_EF1(i, j, allocation, valuations):
                # Identify most envied item by agent i in j's bundle
                most_envied = max(allocation[j], key=lambda item: valuations[i][item])
                # Check if transfer improves recipient's satisfaction enough
                current_val_i = sum(valuations[i][item] for item in allocation[i])
                potential_val_i = current_val_i + valuations[i][most_envied]
                current_val_j = sum(valuations[j][item] for item in allocation[j])
                potential_val_j = current_val_j - valuations[j][most_envied]

                if potential_val_i - current_val_i >= min_transfer_diff:
                    allocation[j].remove(most_envied)
                    allocation[i].append(most_envied)
                    print(f"⚠️ Agent {i} envied Agent {j}. Transferred item {most_envied} → Agent {i}")
                    changed = True
    return allocation, changed

def simulate_EF1_over_time(allocation, valuations, base_valuations, delta=1.0, time_steps=5, min_transfer_diff=0):
    """
    Main loop simulating valuation drift and restoring EF1.
    Tracks satisfaction over time.
    """
    satisfaction_history = [[] for _ in range(len(allocation))]

    print("🚀 Initial Allocation:")
    for idx, items in enumerate(allocation):
        print(f"Agent {idx}: Items {items}")

    for t in range(time_steps):
        print(f"\nTime Step {t+1}")
        valuations = simulate_preference_drift_stable(valuations, delta, base_valuations)

        while True:
            allocation, changed = greedy_local_EF1_restore(allocation, valuations, min_transfer_diff)
            if not changed:
                break

        # Track satisfaction per agent
        for i in range(len(allocation)):
            val = sum(valuations[i][item] for item in allocation[i])
            satisfaction_history[i].append(val)

        print(f"Current Allocation:")
        for idx, items in enumerate(allocation):
            print(f"Agent {idx}: Items {items}")

    return allocation, valuations, satisfaction_history

# === Parameters ===
num_agents = 3
num_items = 9
delta = 4.0     # Max deviation from base valuation
time_steps = 10
min_transfer_diff = 0 # Min satisfaction improvement to allow transfer (set >0 to be stricter)

# Initial round-robin allocation
allocation = [[] for _ in range(num_agents)]
for item in range(num_items):
    allocation[item % num_agents].append(item)

# Generate initial valuations randomly and save a copy as base
valuations = [
    [random.uniform(1, 10) for _ in range(num_items)]
    for _ in range(num_agents)
]
base_valuations = [row.copy() for row in valuations]

# Run simulation
final_alloc, final_vals, satisfaction_history = simulate_EF1_over_time(
    allocation, valuations, base_valuations, delta, time_steps, min_transfer_diff
)

# Plot agent satisfaction over time
import matplotlib.pyplot as plt

for i, agent_vals in enumerate(satisfaction_history):
    plt.plot(agent_vals, label=f"Agent {i}")

plt.title("Agent Satisfaction Over Time (Stable EF1 Division)")
plt.xlabel("Time Step")
plt.ylabel("Total Value of Allocated Items")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
