"""
datatool.py - Main entry point for the CLI Data Engineering Tool
Run: python datatool.py
"""

import sys
import logging
from ingest import ingest_file
from validate import validate_file
from transform import transform_file

# ── Logging Setup ──────────────────────────────────────────────
logging.basicConfig(
    filename="datatool.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Help Text ──────────────────────────────────────────────────
def show_help():
    print("""
╔══════════════════════════════════════════════════════╗
║              datatool - Help Menu                    ║
╠══════════════════════════════════════════════════════╣
║  ingest <input_file>                                 ║
║      Read a CSV/JSON file and display summary        ║
║                                                      ║
║  validate <input_file>                               ║
║      Check for nulls, duplicates, type issues        ║
║                                                      ║
║  transform <input_file> <output_file>                ║
║      Clean and save data to output file              ║
║                                                      ║
║  help                                                ║
║      Show this help menu                             ║
║                                                      ║
║  exit                                                ║
║      Exit the tool                                   ║
╚══════════════════════════════════════════════════════╝
""")


# ── REPL Loop ──────────────────────────────────────────────────
def main():
    print("=" * 54)
    print("   Welcome to PipelineX - Your CLI Data Engineering Tool")
    print("   Type 'help' for available commands")
    print("=" * 54)

    while True:
        try:
            raw = input("\ndatatool> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting datatool. Goodbye!")
            logger.info("Session ended by user.")
            sys.exit(0)

        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()

        # ── exit ──────────────────────────────────────
        if command == "exit":
            print("Exiting PipelineX! Goodbye!")
            logger.info("Session ended via exit command.")
            break

        # ── help ──────────────────────────────────────
        elif command == "help":
            show_help()

        # ── ingest ────────────────────────────────────
        elif command == "ingest":
            if len(parts) < 2:
                print("  Usage: ingest <input_file>")
            else:
                logger.info(f"ingest called with: {parts[1]}")
                ingest_file(parts[1])

        # ── validate ──────────────────────────────────
        elif command == "validate":
            if len(parts) < 2:
                print("  Usage: validate <input_file>")
            else:
                logger.info(f"validate called with: {parts[1]}")
                validate_file(parts[1])

        # ── transform ─────────────────────────────────
        elif command == "transform":
            if len(parts) < 3:
                print("  Usage: transform <input_file> <output_file>")
            else:
                logger.info(f"transform called with: {parts[1]} -> {parts[2]}")
                transform_file(parts[1], parts[2])

        # ── unknown ───────────────────────────────────
        else:
            print(f"  Unknown command: '{command}'. Type 'help' to see available commands.")
            logger.warning(f"Unknown command entered: {command}")


if __name__ == "__main__":
    main()
