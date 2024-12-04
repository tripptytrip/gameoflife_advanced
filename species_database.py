# species_database.py

import sqlite3
import random

import itertools

def generate_species():
    species_list = []
    neighbor_counts = range(9)  # Neighbor counts from 0 to 8

    # Generate all possible birth rule combinations
    birth_rule_combinations = []
    for i in range(512):  # 2^9 possible combinations
        birth_rule = [int(bit) for bit in bin(i)[2:].zfill(9)]
        birth_rule_combinations.append([idx for idx, bit in enumerate(birth_rule) if bit])

    # Generate all possible survival rule combinations (same as birth rules)
    survival_rule_combinations = birth_rule_combinations.copy()

    # Generate all possible species combinations
    for birth_rules in birth_rule_combinations:
        for survival_rules in survival_rule_combinations:
            # Create a unique name or identifier for the species
            birth_bits = ''.join(['1' if i in birth_rules else '0' for i in range(9)])
            survival_bits = ''.join(['1' if i in survival_rules else '0' for i in range(9)])
            species_name = birth_bits + survival_bits

            species_list.append((
                species_name,
                ','.join(map(str, birth_rules)),
                ','.join(map(str, survival_rules))
            ))

    return species_list

def create_species_database():
    """
    Creates a SQLite database with species.
    """
    conn = sqlite3.connect('species.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS species (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            birth_rules TEXT,
            survival_rules TEXT
        )
    ''')

    # Generate species
    species_list = generate_species()

    # Insert species into the database
    c.executemany('''
        INSERT OR IGNORE INTO species (name, birth_rules, survival_rules)
        VALUES (?, ?, ?)
    ''', species_list)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_species_database()
