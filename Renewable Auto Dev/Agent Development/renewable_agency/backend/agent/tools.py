"""
Mathematical tools and utilities for the Renewable Energy Agent
"""

import random
from typing import Dict, Any

def add_numbers(a: float, b: float) -> Dict[str, Any]:
    """
    Add two numbers together
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dictionary with calculation details
    """
    result = a + b
    return {
        "result": result,
        "operation": "addition",
        "explanation": f"Added {a} + {b} = {result}",
        "confidence": 1.0,
        "sources": ["calculator"],
        "units": ""
    }

def subtract_numbers(a: float, b: float) -> Dict[str, Any]:
    """
    Subtract second number from first number
    
    Args:
        a: First number (minuend)
        b: Second number (subtrahend)
        
    Returns:
        Dictionary with calculation details
    """
    result = a - b
    return {
        "result": result,
        "operation": "subtraction",
        "explanation": f"Subtracted {a} - {b} = {result}",
        "confidence": 1.0,
        "sources": ["calculator"],
        "units": ""
    }

def multiply_numbers(a: float, b: float) -> Dict[str, Any]:
    """
    Multiply two numbers together
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dictionary with calculation details
    """
    result = a * b
    return {
        "result": result,
        "operation": "multiplication",
        "explanation": f"Multiplied {a} × {b} = {result}",
        "confidence": 1.0,
        "sources": ["calculator"],
        "units": ""
    }

def divide_numbers(a: float, b: float) -> Dict[str, Any]:
    """
    Divide first number by second number
    
    Args:
        a: Dividend
        b: Divisor
        
    Returns:
        Dictionary with calculation details
    """
    if b == 0:
        return {
            "result": float('inf'),
            "operation": "division",
            "explanation": f"Cannot divide {a} by zero",
            "confidence": 0.0,
            "sources": ["calculator"],
            "units": ""
        }
    
    result = a / b
    return {
        "result": result,
        "operation": "division",
        "explanation": f"Divided {a} ÷ {b} = {result}",
        "confidence": 1.0,
        "sources": ["calculator"],
        "units": ""
    }

def get_renewable_context(operation: str, result: float, a: float, b: float) -> str:
    """
    Generate renewable energy context for mathematical operations
    
    Args:
        operation: The mathematical operation performed
        result: The calculated result
        a: First operand
        b: Second operand
        
    Returns:
        String with renewable energy context
    """
    contexts = {
        "addition": [
            f"This could represent combining {a} kW and {b} kW of solar capacity for a total of {result} kW",
            f"Adding {a} wind turbines to {b} existing ones gives {result} total turbines",
            f"Combining energy production of {a} MWh and {b} MWh yields {result} MWh total",
            f"Sum of {a} tons CO2 saved and {b} tons CO2 saved equals {result} tons total CO2 reduction"
        ],
        "subtraction": [
            f"Energy demand of {a} MWh minus {b} MWh renewable generation leaves {result} MWh from grid",
            f"After installing {b} kW of solar, the remaining capacity needed is {result} kW from {a} kW total",
            f"Net energy production: {a} MWh generated minus {b} MWh consumed = {result} MWh surplus",
            f"Carbon footprint reduction: {a} tons baseline minus {b} tons with renewables = {result} tons net"
        ],
        "multiplication": [
            f"With {a} solar panels each producing {b} kWh daily, total production is {result} kWh/day",
            f"Wind farm efficiency: {a} turbines × {b} MW each = {result} MW total capacity",
            f"Annual savings: {a} years × {b} dollars saved per year = ${result} total savings",
            f"Carbon offset: {a} households × {b} tons CO2 saved each = {result} tons total CO2 offset"
        ],
        "division": [
            f"Energy per unit: {a} MWh total capacity ÷ {b} units = {result} MWh per unit",
            f"Cost efficiency: ${a} total cost ÷ {b} kW capacity = ${result} per kW installed",
            f"Daily consumption: {a} kWh monthly usage ÷ {b} days = {result} kWh per day",
            f"ROI calculation: ${a} savings ÷ ${b} investment = {result} return ratio"
        ]
    }
    
    if operation in contexts:
        return random.choice(contexts[operation])
    else:
        return f"This {operation} operation with result {result} could be applied to renewable energy calculations"

def calculate_solar_power(panel_count: int, panel_wattage: float, sun_hours: float) -> Dict[str, Any]:
    """
    Calculate solar power generation
    
    Args:
        panel_count: Number of solar panels
        panel_wattage: Wattage per panel
        sun_hours: Average daily sun hours
        
    Returns:
        Dictionary with solar power calculation
    """
    daily_kwh = (panel_count * panel_wattage * sun_hours) / 1000
    monthly_kwh = daily_kwh * 30
    annual_kwh = daily_kwh * 365
    
    return {
        "result": daily_kwh,
        "operation": "solar_power_calculation",
        "explanation": f"{panel_count} panels × {panel_wattage}W × {sun_hours}h = {daily_kwh:.2f} kWh/day",
        "renewable_context": f"Daily: {daily_kwh:.2f} kWh, Monthly: {monthly_kwh:.2f} kWh, Annual: {annual_kwh:.2f} kWh",
        "confidence": 0.95,
        "sources": ["solar_calculator"],
        "units": "kWh"
    }

def calculate_wind_power(turbine_count: int, rated_power: float, capacity_factor: float) -> Dict[str, Any]:
    """
    Calculate wind power generation
    
    Args:
        turbine_count: Number of wind turbines
        rated_power: Rated power per turbine in MW
        capacity_factor: Capacity factor (0.0 to 1.0)
        
    Returns:
        Dictionary with wind power calculation
    """
    annual_mwh = turbine_count * rated_power * 8760 * capacity_factor
    
    return {
        "result": annual_mwh,
        "operation": "wind_power_calculation",
        "explanation": f"{turbine_count} turbines × {rated_power}MW × 8760h × {capacity_factor} = {annual_mwh:.2f} MWh/year",
        "renewable_context": f"Annual wind generation: {annual_mwh:.2f} MWh with {capacity_factor*100:.1f}% capacity factor",
        "confidence": 0.90,
        "sources": ["wind_calculator"],
        "units": "MWh/year"
    } 