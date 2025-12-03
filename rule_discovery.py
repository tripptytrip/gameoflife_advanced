# rule_discovery.py

import threading
import random
import json
import os
import time
import numpy as np

from square_grid import SquareGrid
from data_recorder import evaluate_rule_criticality
from lifeform import Lifeform

# --- Constants for the Genetic Algorithm ---
POPULATION_SIZE = 20
NUM_PARENTS = 5
GRID_SIZE = 64
NUM_FRAMES = 200
MUTATION_RATE = 1  # Number of bits to flip

# A lock to prevent race conditions when writing to the JSON file
file_lock = threading.Lock()

# --- Genome Representation ---

def rules_to_gene(birth_rules, survival_rules):
    """Converts B/S rules (lists of ints) to an 18-bit gene string."""
    gene = ['0'] * 18
    for b in birth_rules:
        gene[b] = '1'
    for s in survival_rules:
        gene[s + 9] = '1'
    return "".join(gene)

def gene_to_rules(gene):
    """Converts an 18-bit gene string to B/S rules."""
    birth_rules = [i for i, bit in enumerate(gene[:9]) if bit == '1']
    survival_rules = [i for i, bit in enumerate(gene[9:]) if bit == '1']
    return birth_rules, survival_rules

def format_rule_string(gene):
    """Formats a gene into a standard B/S string."""
    b, s = gene_to_rules(gene)
    return f"B{''.join(map(str, b))}/S{''.join(map(str, s))}"

# --- File Operations ---

def save_rule(gene, score):
    """Saves a high-scoring rule to discovered_rules.json."""
    rule_str = format_rule_string(gene)
    print(f"Found new rule: {rule_str} with score {score:.4f}")

    with file_lock:
        rules = []
        if os.path.exists('discovered_rules.json'):
            with open('discovered_rules.json', 'r') as f:
                try:
                    rules = json.load(f)
                except json.JSONDecodeError:
                    pass  # File is empty or corrupt, start fresh

        if rule_str not in rules:
            rules.append(rule_str)
            with open('discovered_rules.json', 'w') as f:
                json.dump(rules, f, indent=4)

# --- Genetic Algorithm Core ---

def run_simulation_for_gene(gene):
    """
    Runs a simulation for a given gene and returns its fitness score.
    """
    birth_rules, survival_rules = gene_to_rules(gene)

    # Handle invalid rules (no birth or no survival)
    if not birth_rules or not survival_rules:
        return 0.0

    lifeform = Lifeform(lifeform_id=1, birth_rules=birth_rules, survival_rules=survival_rules)
    grid = SquareGrid(
        lifeforms=[lifeform],
        grid_width=GRID_SIZE,
        grid_height=GRID_SIZE,
        initial_alive_percentage=0.5
    )

    grid_history = []
    total_cells = grid.grid.size

    for _ in range(NUM_FRAMES):
        grid_state = (grid.grid > 0).astype(np.uint8)
        
        # Early Exit Condition
        population = np.count_nonzero(grid_state)
        if population == 0 or population == total_cells:
            return 0.0 # Extinct or saturated, fitness is 0

        grid_history.append(grid_state)
        grid.update()
        
    # Ensure history is not too short for evaluation
    if len(grid_history) < 50:
        return 0.0
        
    return evaluate_rule_criticality(grid_history)

def mutate(gene):
    """Flips a random bit in the gene string."""
    gene_list = list(gene)
    for _ in range(MUTATION_RATE):
        index_to_flip = random.randint(0, len(gene_list) - 1)
        gene_list[index_to_flip] = '1' if gene_list[index_to_flip] == '0' else '0'
    return "".join(gene_list)

def discover_rules():
    """
    The main background task that runs the genetic algorithm to find rules.
    """
    # 1. Initialization
    population = []
    for _ in range(POPULATION_SIZE):
        # Generate random B/S rules and convert to a gene
        b = sorted(random.sample(range(9), k=random.randint(1, 4)))
        s = sorted(random.sample(range(9), k=random.randint(1, 4)))
        population.append(rules_to_gene(b, s))

    generation_count = 0
    while True:
        generation_count += 1

        # 2. Evaluation
        evaluated_population = []
        for gene in population:
            score = run_simulation_for_gene(gene)
            evaluated_population.append((gene, score))
            
            # Save any rule that meets the criteria
            if score > 0.8:
                save_rule(gene, score)

        # 3. Selection
        evaluated_population.sort(key=lambda x: x[1], reverse=True)
        
        best_gene, best_score = evaluated_population[0]
        print(f"Gen {generation_count}: Best rule {format_rule_string(best_gene)} | Score: {best_score:.4f}")

        parents = [gene for gene, score in evaluated_population[:NUM_PARENTS]]

        # 4. Breeding / Mutation
        next_population = parents[:] # Carry over the best parents

        while len(next_population) < POPULATION_SIZE:
            parent_gene = random.choice(parents)
            child_gene = mutate(parent_gene)
            next_population.append(child_gene)

        # 5. Replacement
        population = next_population
        
        # Small delay to prevent pegging CPU and allow logs to be read
        time.sleep(0.1)

if __name__ == '__main__':
    print("Starting rule discovery process using a genetic algorithm.")
    print("Found rules will be saved to 'discovered_rules.json'.")
    discover_rules()