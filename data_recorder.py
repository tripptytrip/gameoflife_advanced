# data_recorder.py

import sqlite3
import threading
import numpy as np
import zlib



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
        # birth_rules/survival_rules are lists of ints (not padded bits)
        birth_str = ','.join(map(str, sorted(birth_rules)))
        survival_str = ','.join(map(str, sorted(survival_rules)))
        lifeform_profile = f"B{birth_str}/S{survival_str}|{shape}"
        self.meta_buffer.add((self.session_id, lifeform_id, lifeform_profile))
        
        self.record_buffer.append((
            self.session_id,
            generation,
            lifeform_id,
            birth_str,
            survival_str,
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
