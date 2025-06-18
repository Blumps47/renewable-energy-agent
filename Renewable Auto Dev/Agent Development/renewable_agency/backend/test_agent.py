#!/usr/bin/env python3
"""
Test the PydanticAI agent directly
"""

import asyncio
import os
from agent.renewable_agent import RenewableEnergyAgent

async def test_agent():
    """Test the agent with a simple math question"""
    print("🤖 Testing Renewable Energy Agent...")
    print(f"API Key present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    
    try:
        agent = RenewableEnergyAgent()
        print("✅ Agent created successfully")
        
        # Test with a simple math question
        result = await agent.process_message("What is 15 + 25?")
        print(f"✅ Agent responded successfully!")
        print(f"Result: {result.result}")
        print(f"Operation: {result.operation}")
        print(f"Explanation: {result.explanation}")
        print(f"Renewable Context: {result.renewable_context}")
        print(f"Confidence: {result.confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent())
    print(f"\n🏁 Test {'PASSED' if success else 'FAILED'}") 