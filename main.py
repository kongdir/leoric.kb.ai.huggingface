"""Main entry point for Leoric KB AI Hugging Face."""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Run the KB AI system."""
    print("🐶 Leoric KB AI - Hugging Face Integration")
    print("="*50)
    

if __name__ == "__main__":
    main()
