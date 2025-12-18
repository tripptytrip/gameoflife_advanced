# main.py
import threading
from game import GameOfLife
from rule_discovery import discover_rules

if __name__ == '__main__':

    # Start the rule discovery in a background thread

    discovery_thread = threading.Thread(target=discover_rules, daemon=True)

    discovery_thread.start()



    game = GameOfLife()

    game.run()

