"""Logging configuration and utilities for the renewable energy AI agent ecosystem."""

import sys
from pathlib import Path
from loguru import logger
from .config import settings


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.app.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler for persistent logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "renewable_energy_agents.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="1 week",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    # Add separate error log
    logger.add(
        log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="2 weeks",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    logger.info(f"Logging configured. Level: {settings.app.log_level}")
    

def get_logger(name: str):
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)


# Initialize logging when module is imported
setup_logging() 