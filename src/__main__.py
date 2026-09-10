"""Entry point for the Turners scraper actor."""
import asyncio
from .main import main

if __name__ == '__main__':
    asyncio.run(main())
