# data_recorder.py

import sqlite3
import threading

class DataRecorder:
    """
    Handles data recording to the database.
    """
    def __init__(self, session_id):
        self.session_id = session_id
        self.conn = sqlite3.connect('species.db', check_same_thread=False)
        self.lock = threading.Lock()
        self.create_tables()
    
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
        with self.lock:
            c = self.conn.cursor()
            lifeform_profile = ''.join(map(str, birth_rules)) + ''.join(map(str, survival_rules))
            # Insert lifeform metadata if not exists
            c.execute('''
                INSERT OR IGNORE INTO lifeform_meta (
                    session_id,
                    lifeform,
                    lifeform_profile
                ) VALUES (?, ?, ?)
            ''', (
                self.session_id,
                lifeform_id,
                lifeform_profile
            ))
            # Insert lifeform record
            c.execute('''
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
            ''', (
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
            self.conn.commit()
        
    def close(self):
        with self.lock:
            self.conn.close()
