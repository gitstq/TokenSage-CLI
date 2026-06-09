"""Entry point for running TokenSage-CLI as a module.

Allows running with: python -m tokensage
"""

import sys

from tokensage.cli import main

if __name__ == "__main__":
    sys.exit(main())
