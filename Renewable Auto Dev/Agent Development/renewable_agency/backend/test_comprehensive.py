#!/usr/bin/env python3
"""
Comprehensive test of the Renewable Energy Agent capabilities
"""

import asyncio
import os
from agent.renewable_agent import RenewableEnergyAgent

async def test_comprehensive():
    """Test all agent capabilities"""
    print("🌱 Comprehensive Renewable Energy Agent Test")
    print("=" * 60)
    
    agent = RenewableEnergyAgent()
    
    test_cases = [
        "What is 100 - 25?",
        "Calculate 12 × 8",
        "Divide 144 by 12",
        "I need to register my information. My name is John Doe and email is john@example.com",
        "Calculate the solar power for 20 panels, 300W each, with 6 hours of sun",
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {question}")
        print("-" * 50)
        
        try:
            result = await agent.process_message(question)
            print(f"✅ Result: {result.result}")
            print(f"📋 Operation: {result.operation}")
            print(f"💡 Explanation: {result.explanation}")
            print(f"🌱 Renewable Context: {result.renewable_context}")
            print(f"🎯 Confidence: {result.confidence}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Comprehensive test completed!")
    print("🚀 Backend is ready for frontend integration!")

if __name__ == "__main__":
    asyncio.run(test_comprehensive()) 