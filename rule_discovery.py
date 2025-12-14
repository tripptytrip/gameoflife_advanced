# rule_discovery.py

import threading
import random
import json
import os
import time

from lifeform import Lifeform
from rules import Rule
from experiments.runner import make_grid, run_timeseries, run_damage_spreading
from analysis.criticality_score import score_timeseries
from neighbor_utils import get_max_neighbors

# --- Constants for the Genetic Algorithm ---
POPULATION_SIZE = 20
NUM_PARENTS = 5
GRID_SIZE = 64
NUM_FRAMES = 200
MUTATION_RATE = 1  # Number of bits to flip
# Lattice config
SHAPE = "square"  # Options: square, hexagon, triangle
TRIANGLE_MODE = "edge+vertex"
NEIGHBOR_COUNT = get_max_neighbors(SHAPE, TRIANGLE_MODE)
GENE_LENGTH = 2 * (NEIGHBOR_COUNT + 1)

# A lock to prevent race conditions when writing to the JSON file
file_lock = threading.Lock()

# --- Genome Representation (length depends on neighbor count) ---

def rule_to_gene(rule: Rule, N: int) -> str:
    """Converts a Rule to a gene string of length 2*(N+1)."""
    gene = ['0'] * (2 * (N + 1))
    for b in rule.birth:
        if 0 <= b <= N:
            gene[b] = '1'
    for s in rule.survive:
        if 0 <= s <= N:
            gene[s + N + 1] = '1'
    return "".join(gene)

def gene_to_rule(gene: str, N: int) -> Rule:
    """Converts a gene string to a Rule."""
    birth_rules = {i for i, bit in enumerate(gene[: N + 1]) if bit == '1'}
    survival_rules = {i for i, bit in enumerate(gene[N + 1 :]) if bit == '1'}
    return Rule(birth=birth_rules, survive=survival_rules)

def format_rule_string(gene):
    """Formats a gene into a standard B/S string."""
    rule = gene_to_rule(gene, NEIGHBOR_COUNT)
    return rule.to_bs_string(NEIGHBOR_COUNT)

# --- File Operations ---

def save_rule(gene, score):
    """Saves a high-scoring rule to discovered_rules.json."""
    rule_str = format_rule_string(gene)
    print(f"Found new rule: {rule_str} with score {score:.4f}")

    with file_lock:
        rules = []
        filename = f"discovered_rules_{SHAPE}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    rules = json.load(f)
                except json.JSONDecodeError:
                    pass  # File is empty or corrupt, start fresh

        if rule_str not in rules:
            rules.append(rule_str)
            with open(filename, 'w') as f:
                json.dump(rules, f, indent=4)

# --- Genetic Algorithm Core ---

def run_simulation_for_gene(gene):
    """
    Runs a simulation for a given gene and returns its fitness score.
    """
    rule = gene_to_rule(gene, NEIGHBOR_COUNT)
    birth_rules = sorted(rule.birth)
    survival_rules = sorted(rule.survive)

    # Handle invalid rules (no birth or no survival)
    if not birth_rules or not survival_rules:
        return 0.0

    lifeform = Lifeform(lifeform_id=1, birth_rules=birth_rules, survival_rules=survival_rules)
    grid = make_grid(
        shape=SHAPE,
        lifeform=lifeform,
        width=GRID_SIZE,
        height=GRID_SIZE,
        p0=0.5,
        seed=None,
        wrap=True,
        triangle_mode=TRIANGLE_MODE,
    )

    series = run_timeseries(grid, lifeform_id=lifeform.id, steps=NUM_FRAMES)
    H = run_damage_spreading(
        shape=SHAPE,
        rule=rule,
        steps=NUM_FRAMES,
        seed=random.randint(0, 1_000_000),
        p0=0.5,
        width=GRID_SIZE,
        height=GRID_SIZE,
        wrap=True,
        triangle_mode=TRIANGLE_MODE,
        flip_cells=1,
    )
    return score_timeseries(series["rho"], series["activity"], series.get("frozen_at"), NUM_FRAMES, H=H)

def mutate(gene):
    """Flips random bits in the gene string."""
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
        rule = Rule.random(NEIGHBOR_COUNT, p_birth=0.3, p_survive=0.3, rng=random)
        population.append(rule_to_gene(rule, NEIGHBOR_COUNT))

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
