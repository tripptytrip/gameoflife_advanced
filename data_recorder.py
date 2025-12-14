# data_recorder.py

import sqlite3
import threading
import numpy as np
import zlib

def evaluate_rule_criticality(grid_history):
    """
    Evaluates if a rule shows complex, maze-like behavior.
    Args:
        grid_history: A list of the last 50 grid states (numpy arrays).
    Returns:
        float: A score (0.0 to 1.0). Higher is more 'critical/maze-like'.
    """
    
    # 1. Check for extinction or saturation
    final_grid = grid_history[-1]
    population = np.count_nonzero(final_grid)
    total_cells = final_grid.size
    density = population / total_cells
    
    # Reject if empty or totally full
    if density < 0.05 or density > 0.95:
        return 0.0

    # 2. Check for Activity (is it frozen?)
    # Compare last frame to 10 frames ago. If identical, it's static.
    if len(grid_history) >= 10 and np.array_equal(final_grid, grid_history[-10]):
        return 0.0 

    # 3. The Compression Test (The "Maze" Detector)
    # Convert grid to bytes
    grid_bytes = final_grid.tobytes()
    compressed = zlib.compress(grid_bytes)
    
    # Calculate compression ratio
    ratio = len(compressed) / len(grid_bytes)
    
    # We want a "Goldilocks" ratio. 
    # Based on the video, labyrinths usually compress to about 30-50% of original size.
    # We score based on distance from an ideal target of 0.4
    target_ratio = 0.4
    dist = abs(ratio - target_ratio)
    
    # Invert distance to get score (closer is better)
    score = max(0, 1.0 - (dist * 2)) 
    
    return score

class DataRecorder:
    """
    Handles data recording to the database.
    """
    def __init__(self, session_id, batch_size=1000):
        self.session_id = session_id
        self.conn = sqlite3.connect('species.db', check_same_thread=False)
        self.lock = threading.Lock()
        self.create_tables()
        self.record_buffer = []
        self.meta_buffer = set()
        self.batch_size = batch_size
    
    def create_tables(self):
        with self.lock:
            c = self.conn.cursor()
            # Create life_records table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS life_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    generation INTEGER,
                    lifeform INTEGER,
                    lifeform_birth_rules TEXT,
                    lifeform_survival_rules TEXT,
                    alive_count INTEGER,
                    static_count INTEGER,
                    shape TEXT,
                    average_cluster_size REAL,
                    growth_rate REAL,
                    death_rate REAL,
                    average_lifespan REAL,
                    max_cluster_size INTEGER,
                    dominance_ratio REAL,
                    entropy REAL,
                    mobility REAL,
                    diversity INTEGER
                )
            ''')

            # Check existing columns in life_records table
            c.execute("PRAGMA table_info(life_records)")
            existing_columns = [row[1] for row in c.fetchall()]

            # List of required columns
            required_columns = [
                'average_cluster_size',
                'growth_rate',
                'death_rate',
                'average_lifespan',
                'max_cluster_size',
                'dominance_ratio',
                'entropy',
                'mobility',
                'diversity'
            ]

            # Add missing columns
            for column in required_columns:
                if column not in existing_columns:
                    # Determine column type
                    if column in ['max_cluster_size', 'diversity']:
                        column_type = 'INTEGER'
                    else:
                        column_type = 'REAL'
                    c.execute(f"ALTER TABLE life_records ADD COLUMN {column} {column_type}")

            # Create lifeform_meta table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS lifeform_meta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    lifeform INTEGER,
                    lifeform_profile TEXT UNIQUE
                )
            ''')
            self.conn.commit()
        
    def insert_record(self, generation, lifeform_id, birth_rules, survival_rules, alive_count, static_count, shape, metrics):
        lifeform_profile = ''.join(map(str, birth_rules)) + ''.join(map(str, survival_rules))
        self.meta_buffer.add((self.session_id, lifeform_id, lifeform_profile))
        
        self.record_buffer.append((
            self.session_id,
            generation,
            lifeform_id,
            ','.join(map(str, birth_rules)),
            ','.join(map(str, survival_rules)),
            alive_count,
            static_count,
            shape,
            metrics.get('average_cluster_size', 0),
            metrics.get('growth_rate', 0),
            metrics.get('death_rate', 0),
            metrics.get('average_lifespan', 0),
            metrics.get('max_cluster_size', 0),
            metrics.get('dominance_ratio', 0),
            metrics.get('entropy', 0),
            metrics.get('mobility', 0),
            metrics.get('diversity', 0)
        ))
        
        if len(self.record_buffer) >= self.batch_size:
            self.flush()
        
    def flush(self):
        with self.lock:
            if not self.record_buffer:
                return

            c = self.conn.cursor()
            
            # Insert lifeform metadata
            c.executemany('''
                INSERT OR IGNORE INTO lifeform_meta (
                    session_id,
                    lifeform,
                    lifeform_profile
                ) VALUES (?, ?, ?)
            ''', list(self.meta_buffer))
            
            # Insert lifeform records
            c.executemany('''
                INSERT INTO life_records (
                    session_id,
                    generation,
                    lifeform,
                    lifeform_birth_rules,
                    lifeform_survival_rules,
                    alive_count,
                    static_count,
                    shape,
                    average_cluster_size,
                    growth_rate,
                    death_rate,
                    average_lifespan,
                    max_cluster_size,
                    dominance_ratio,
                    entropy,
                    mobility,
                    diversity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', self.record_buffer)
            
            self.conn.commit()
            self.record_buffer.clear()
            self.meta_buffer.clear()

    def close(self):
        self.flush()
        with self.lock:
            self.conn.close()
