import random
import copy

# -------- Helper functions --------

def initialize_allocation(num_agents, num_items):
    """Simple round-robin allocation."""
    allocation = {i: [] for i in range(num_agents)}
    for item in range(num_items):
        allocation[item % num_agents].append(item)
    return allocation

def initialize_valuations(num_agents, num_items):
    """Initialize valuations randomly between 1 and 10."""
    valuations = [[random.randint(1, 10) for _ in range(num_items)] for _ in range(num_agents)]
    return valuations

def simulate_valuation_drift(valuations, delta=0.1):
    """Apply small random drift to valuations."""
    for i in range(len(valuations)):
        for j in range(len(valuations[i])):
            drift = random.uniform(-delta, delta)
            valuations[i][j] = max(0, valuations[i][j] + drift)  # no negative valuations
    return valuations

def agent_value(agent, items, valuations):
    """Sum valuation for an agent over given items."""
    return sum(valuations[agent][item] for item in items)

def is_EF1(allocation, valuations):
    """Check if allocation is EF1 for all pairs."""
    agents = list(allocation.keys())
    for i in agents:
        val_i = agent_value(i, allocation[i], valuations)
        for j in agents:
            if i == j:
                continue
            val_j_items = sorted([valuations[i][item] for item in allocation[j]], reverse=True)
            # If envy's value is larger than val_i plus any one item removed from j's bundle
            if len(val_j_items) == 0:
                continue
            # EF1 condition: val_i >= val_j without the highest item
            if val_i < sum(val_j_items[1:]):
                return False
    return True

def find_ef1_violators(allocation, valuations):
    """Return list of (envying_agent, envied_agent) pairs violating EF1."""
    violators = []
    agents = list(allocation.keys())
    for i in agents:
        val_i = agent_value(i, allocation[i], valuations)
        for j in agents:
            if i == j:
                continue
            val_j_items = sorted([valuations[i][item] for item in allocation[j]], reverse=True)
            if len(val_j_items) == 0:
                continue
            if val_i < sum(val_j_items[1:]):
                violators.append((i, j))
    return violators

def get_most_impactful_item(envying_agent, envied_agent, envied_bundle, valuations):
    """Return item in envied_bundle that envying_agent values most."""
    if not envied_bundle:
        return None
    best_item = max(envied_bundle, key=lambda item: valuations[envying_agent][item])
    return best_item

def is_near_ef1(allocation, valuations, epsilon=0.1):
    """Simple near-EF1 check: max envy difference < epsilon."""
    agents = list(allocation.keys())
    for i in agents:
        val_i = agent_value(i, allocation[i], valuations)
        for j in agents:
            if i == j:
                continue
            val_j_items = sorted([valuations[i][item] for item in allocation[j]], reverse=True)
            if len(val_j_items) == 0:
                continue
            envy_amount = sum(val_j_items[1:]) - val_i
            if envy_amount > epsilon:
                return False
    return True

# -------- Main iEF1 Algorithm --------

def incremental_ef1_restoration(num_agents, num_items, timesteps, delta=0.1, epsilon=0.1):
    allocation = initialize_allocation(num_agents, num_items)
    valuations = initialize_valuations(num_agents, num_items)

    print("🚀 Initial Allocation:")
    for a in allocation:
        print(f"Agent {a}: Items {allocation[a]}")
    print()

    for t in range(1, timesteps+1):
        print(f"📦 Time Step {t}")

        # 1. Valuations drift
        valuations = simulate_valuation_drift(valuations, delta)

        # 2. Restore EF1 if needed
        max_restoration_steps = 100
        num_transfers = 0

        while not is_EF1(allocation, valuations) and num_transfers < max_restoration_steps:
            violators = find_ef1_violators(allocation, valuations)
            if not violators:
                break

            # Take first violator pair
            envier, envied = violators[0]
            print(f"⚠️ Agent {envier} envied Agent {envied}.")

            item_to_transfer = get_most_impactful_item(envier, envied, allocation[envied], valuations)
            if item_to_transfer is None:
                print("  No item to transfer found.")
                break

            # Simulate transfer and check near EF1
            new_allocation = copy.deepcopy(allocation)
            new_allocation[envied].remove(item_to_transfer)
            new_allocation[envier].append(item_to_transfer)

            if is_near_ef1(new_allocation, valuations, epsilon):
                allocation = new_allocation
                num_transfers += 1
                print(f"  Transferred item {item_to_transfer} from Agent {envied} to Agent {envier}.")
            else:
                print("  Transfer not valid (breaks near EF1). Stopping restoration for this step.")
                break

        print("✅ Current Allocation:")
        for a in allocation:
            print(f"Agent {a}: Items {allocation[a]}")
        print()

    return allocation, valuations

# -------- Run the simulation --------
if __name__ == "__main__":
    incremental_ef1_restoration(num_agents=3, num_items=9, timesteps=10, delta=0.2, epsilon=0.1)
