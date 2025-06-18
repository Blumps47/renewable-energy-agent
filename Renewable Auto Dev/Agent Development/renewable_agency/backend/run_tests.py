#!/usr/bin/env python3
"""
Test runner for Renewable Energy Analyst Agent
Runs all tests and logs results
"""

import subprocess
import sys
import os
import datetime
from pathlib import Path


def log_result(message: str, log_file: str = "logs/test_results.log"):
    """Log test results to file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print(log_entry.strip())


def run_command(command: list, description: str) -> bool:
    """Run a command and log results"""
    log_result(f"Starting: {description}")
    log_result(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            log_result(f"✅ SUCCESS: {description}")
            if result.stdout:
                log_result(f"Output: {result.stdout.strip()}")
            return True
        else:
            log_result(f"❌ FAILED: {description}")
            log_result(f"Exit code: {result.returncode}")
            if result.stderr:
                log_result(f"Error: {result.stderr.strip()}")
            if result.stdout:
                log_result(f"Output: {result.stdout.strip()}")
            return False
            
    except Exception as e:
        log_result(f"❌ EXCEPTION: {description} - {str(e)}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    log_result("=== Checking Dependencies ===")
    
    required_packages = [
        "pytest",
        "fastapi",
        "pydantic-ai",
        "openai",
        "uvicorn"
    ]
    
    all_good = True
    for package in required_packages:
        success = run_command(
            [sys.executable, "-c", f"import {package.replace('-', '_')}"],
            f"Check {package} import"
        )
        if not success:
            all_good = False
    
    return all_good


def run_unit_tests():
    """Run unit tests"""
    log_result("=== Running Unit Tests ===")
    
    # Run agent tests
    agent_success = run_command(
        [sys.executable, "-m", "pytest", "tests/test_agent.py", "-v"],
        "Agent unit tests"
    )
    
    # Run API tests
    api_success = run_command(
        [sys.executable, "-m", "pytest", "tests/test_api.py", "-v"],
        "API unit tests"
    )
    
    return agent_success and api_success


def run_integration_tests():
    """Run integration tests"""
    log_result("=== Running Integration Tests ===")
    
    # Run all tests together
    integration_success = run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        "All integration tests"
    )
    
    return integration_success


def test_api_manually():
    """Test API endpoints manually (requires server to be running)"""
    log_result("=== Manual API Testing ===")
    log_result("Note: These tests require the FastAPI server to be running on localhost:8000")
    
    # Test commands from PRD
    test_commands = [
        {
            "cmd": ["curl", "-s", "-X", "GET", "http://localhost:8000/api/health"],
            "desc": "Health check endpoint"
        },
        {
            "cmd": ["curl", "-s", "-X", "POST", "http://localhost:8000/api/chat",
                   "-H", "Content-Type: application/json",
                   "-d", '{"message": "What is 15 + 25?"}'],
            "desc": "Chat endpoint with math question"
        },
        {
            "cmd": ["curl", "-s", "-X", "POST", "http://localhost:8000/api/register",
                   "-H", "Content-Type: application/json", 
                   "-d", '{"name": "Test User", "email": "test@example.com"}'],
            "desc": "User registration endpoint"
        }
    ]
    
    all_success = True
    for test in test_commands:
        success = run_command(test["cmd"], test["desc"])
        if not success:
            all_success = False
    
    return all_success


def run_agent_directly():
    """Test the agent directly"""
    log_result("=== Testing Agent Directly ===")
    
    # Test the agent script itself
    success = run_command(
        [sys.executable, "-c", """
import asyncio
from agent.renewable_agent import RenewableEnergyAgent

async def test_agent():
    agent = RenewableEnergyAgent()
    response = await agent.process_message("Test message")
    print(f"Agent response type: {type(response)}")
    return True

# Run test
result = asyncio.run(test_agent())
print("Agent direct test completed")
"""],
        "Direct agent functionality test"
    )
    
    return success


def main():
    """Main test runner"""
    log_result("=" * 60)
    log_result("🌱 RENEWABLE ENERGY ANALYST AGENT - TEST SUITE")
    log_result("=" * 60)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    log_result(f"Working directory: {os.getcwd()}")
    
    # Track results
    results = {}
    
    # 1. Check dependencies
    results["dependencies"] = check_dependencies()
    
    # 2. Run unit tests
    results["unit_tests"] = run_unit_tests()
    
    # 3. Run integration tests  
    results["integration_tests"] = run_integration_tests()
    
    # 4. Test agent directly
    results["agent_direct"] = run_agent_directly()
    
    # 5. Manual API tests (optional - requires server running)
    log_result("Manual API tests skipped - start server manually and use curl commands")
    results["manual_api"] = None
    
    # Summary
    log_result("=" * 60)
    log_result("🏁 TEST SUMMARY")
    log_result("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in results.items():
        if result is not None:
            total_tests += 1
            status = "✅ PASSED" if result else "❌ FAILED"
            log_result(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed_tests += 1
        else:
            log_result(f"{test_name.replace('_', ' ').title()}: ⏭️ SKIPPED")
    
    log_result(f"")
    log_result(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        log_result("🎉 ALL TESTS PASSED!")
        return 0
    else:
        log_result("⚠️ Some tests failed. Check the log for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 