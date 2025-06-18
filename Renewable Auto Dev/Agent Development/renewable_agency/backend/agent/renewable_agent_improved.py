"""
Improved Renewable Energy Analyst Agent using PydanticAI with Mock Mode Support
"""

import os
import asyncio
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI

from .models import MathResponse, UserRegistration
from .tools import add_numbers, subtract_numbers, multiply_numbers, divide_numbers, get_renewable_context

# Load environment variables from parent directory
load_dotenv('../../../.env')

# Check if we should use mock mode (for testing without API key)
USE_MOCK_MODE = os.getenv('USE_MOCK_MODE', 'false').lower() == 'true'

if not USE_MOCK_MODE:
    # Initialize OpenAI model
    try:
        model = OpenAIModel('gpt-4o-mini')
        print("✅ OpenAI model initialized successfully")
    except Exception as e:
        print(f"⚠️ Failed to initialize OpenAI model: {e}")
        print("🔧 Falling back to mock mode")
        USE_MOCK_MODE = True
        model = None
else:
    print("🔧 Running in MOCK MODE - no OpenAI API calls will be made")
    model = None

# Runtime context for user data
class RenewableContext:
    def __init__(self):
        self.user_data: Dict[str, Any] = {}
        self.conversation_history: list = []
        self.user_preferences: Dict[str, Any] = {}

# Global context instance
context = RenewableContext()

class RenewableEnergyAgent:
    """
    Main agent class for handling renewable energy analysis
    """
    
    def __init__(self):
        self.context = context
        self.use_mock = USE_MOCK_MODE or model is None
        
        if not self.use_mock:
            # Create agent with memory and structured response
            self.agent = Agent(
                model=model,
                result_type=MathResponse,
                system_prompt="""You are a specialized Renewable Energy Analyst Agent with expertise in:
                - Solar, wind, and other renewable energy technologies
                - Energy calculations and mathematical analysis
                - Power generation and capacity planning
                - Energy efficiency and sustainability metrics

                INSTRUCTIONS:
                1. When users ask mathematical questions, use the available tools (add, subtract, multiply, divide)
                2. Always provide renewable energy context for calculations when relevant
                3. Ask for user's full name and email address for tracking and engagement
                4. Remember previous conversation context and user preferences
                5. Respond with structured MathResponse format including:
                   - result: The calculated value
                   - operation: The mathematical operation performed
                   - explanation: Clear explanation of the calculation
                   - renewable_context: How this relates to renewable energy (when applicable)
                   - units: Appropriate units of measurement
                   - confidence: Your confidence in the result (0.0 to 1.0)
                   - sources: Data sources used

                TOOLS AVAILABLE:
                - add_tool: Add two numbers together
                - subtract_tool: Subtract one number from another
                - multiply_tool: Multiply two numbers
                - divide_tool: Divide one number by another

                Always be helpful, accurate, and provide educational context about renewable energy."""
            )
            
            # Add tools if not in mock mode
            @self.agent.tool_plain
            def add_tool(a: float, b: float) -> dict:
                """Add two numbers together"""
                result = add_numbers(a, b)
                result["renewable_context"] = get_renewable_context("addition", result["result"], a, b)
                return result

            @self.agent.tool_plain
            def subtract_tool(a: float, b: float) -> dict:
                """Subtract second number from first number"""
                result = subtract_numbers(a, b)
                result["renewable_context"] = get_renewable_context("subtraction", result["result"], a, b)
                return result

            @self.agent.tool_plain
            def multiply_tool(a: float, b: float) -> dict:
                """Multiply two numbers together"""
                result = multiply_numbers(a, b)
                result["renewable_context"] = get_renewable_context("multiplication", result["result"], a, b)
                return result

            @self.agent.tool_plain
            def divide_tool(a: float, b: float) -> dict:
                """Divide first number by second number"""
                result = divide_numbers(a, b)
                result["renewable_context"] = get_renewable_context("division", result["result"], a, b)
                return result
        else:
            self.agent = None
            print("🔧 Agent initialized in mock mode")
        
    async def process_message(self, message: str, user_id: Optional[str] = None) -> MathResponse:
        """
        Process a user message and return structured response
        
        Args:
            message: User's message/question
            user_id: Optional user identifier
            
        Returns:
            MathResponse: Structured response from the agent
        """
        try:
            # Add message to conversation history
            self.context.conversation_history.append({
                "role": "user",
                "content": message,
                "user_id": user_id
            })
            
            # Handle mock mode
            if self.use_mock:
                return self._mock_response(message)
            
            # Run the agent
            result = await self.agent.run(message)
            
            # Add response to conversation history
            self.context.conversation_history.append({
                "role": "assistant",
                "content": result.data.model_dump() if result.data else None
            })
            
            return result.data
            
        except Exception as e:
            # Return error response in structured format
            error_msg = str(e)
            
            # Provide specific guidance for API key issues
            if "401" in error_msg or "Incorrect API key" in error_msg or "invalid_api_key" in error_msg:
                explanation = "OpenAI API key is invalid or missing. Please check your .env file and set a valid OPENAI_API_KEY from https://platform.openai.com/account/api-keys"
                renewable_context = "To get renewable energy analysis, a valid OpenAI API key is required. The agent uses AI to provide contextual renewable energy insights."
            else:
                explanation = f"Error processing message: {error_msg}"
                renewable_context = "Unable to process renewable energy analysis due to technical issue"
            
            return MathResponse(
                result=0.0,
                operation="error",
                explanation=explanation,
                renewable_context=renewable_context,
                confidence=0.0,
                sources=["error_handler"]
            )
    
    def _mock_response(self, message: str) -> MathResponse:
        """
        Generate a mock response for testing without API key
        """
        # Look for mathematical patterns in the message
        add_pattern = r'(?:add|plus|\+)\s*(\d+(?:\.\d+)?)\s*(?:and|to|with)?\s*(\d+(?:\.\d+)?)'
        subtract_pattern = r'(?:subtract|minus|-)\s*(\d+(?:\.\d+)?)\s*(?:from|and)?\s*(\d+(?:\.\d+)?)'
        multiply_pattern = r'(?:multiply|times|\*|×)\s*(\d+(?:\.\d+)?)\s*(?:by|and|with)?\s*(\d+(?:\.\d+)?)'
        divide_pattern = r'(?:divide|divided by|/|÷)\s*(\d+(?:\.\d+)?)\s*(?:by|and)?\s*(\d+(?:\.\d+)?)'
        
        # Try to find math operations
        add_match = re.search(add_pattern, message.lower())
        subtract_match = re.search(subtract_pattern, message.lower())
        multiply_match = re.search(multiply_pattern, message.lower())
        divide_match = re.search(divide_pattern, message.lower())
        
        if add_match:
            a, b = float(add_match.group(1)), float(add_match.group(2))
            result = a + b
            return MathResponse(
                result=result,
                operation="addition",
                explanation=f"I added {a} + {b} = {result}",
                renewable_context=f"In renewable energy, adding {a} kW and {b} kW solar panel capacities would give you a total of {result} kW, enough to power approximately {int(result/4)} average homes.",
                units="kW",
                confidence=0.95,
                sources=["mock_calculation", "renewable_energy_database"]
            )
        elif subtract_match:
            a, b = float(subtract_match.group(1)), float(subtract_match.group(2))
            result = a - b
            return MathResponse(
                result=result,
                operation="subtraction",
                explanation=f"I subtracted {a} - {b} = {result}",
                renewable_context=f"This could represent reducing energy consumption by {b} kWh from {a} kWh, resulting in {result} kWh, helping reduce carbon footprint by approximately {result * 0.4:.1f} kg CO2.",
                units="kWh",
                confidence=0.95,
                sources=["mock_calculation", "carbon_footprint_calculator"]
            )
        elif multiply_match:
            a, b = float(multiply_match.group(1)), float(multiply_match.group(2))
            result = a * b
            return MathResponse(
                result=result,
                operation="multiplication",
                explanation=f"I multiplied {a} × {b} = {result}",
                renewable_context=f"If you have {a} wind turbines each generating {b} kW, your total capacity would be {result} kW, producing approximately {result * 8760 * 0.35:.0f} kWh annually.",
                units="kW",
                confidence=0.95,
                sources=["mock_calculation", "wind_energy_stats"]
            )
        elif divide_match:
            a, b = float(divide_match.group(1)), float(divide_match.group(2))
            if b != 0:
                result = a / b
                return MathResponse(
                    result=result,
                    operation="division",
                    explanation=f"I divided {a} ÷ {b} = {result:.2f}",
                    renewable_context=f"This could represent the efficiency ratio in renewable energy systems - {a} kWh output divided by {b} kWh input gives {result:.2f} efficiency ratio.",
                    units="ratio",
                    confidence=0.95,
                    sources=["mock_calculation", "efficiency_calculator"]
                )
            else:
                return MathResponse(
                    result=0.0,
                    operation="error",
                    explanation="Cannot divide by zero",
                    renewable_context="In renewable energy calculations, division by zero would indicate an undefined efficiency or ratio.",
                    confidence=0.0,
                    sources=["error_handler"]
                )
        else:
            return MathResponse(
                result=0.0,
                operation="general_response",
                explanation="I'm a Renewable Energy Analyst Agent running in mock mode. I can help with mathematical calculations related to renewable energy. Try asking me to add, subtract, multiply, or divide numbers!",
                renewable_context="Renewable energy systems rely heavily on mathematical calculations for capacity planning, efficiency analysis, and environmental impact assessment. Common calculations include power generation capacity, energy storage requirements, and carbon footprint reduction estimates.",
                confidence=0.8,
                sources=["mock_mode", "renewable_energy_guide"]
            )
    
    def get_conversation_history(self) -> list:
        """Get the conversation history"""
        return self.context.conversation_history
    
    def get_user_data(self) -> dict:
        """Get current user data"""
        return self.context.user_data
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference"""
        self.context.user_preferences[key] = value
    
    def get_user_preferences(self) -> dict:
        """Get user preferences"""
        return self.context.user_preferences

# Main testing loop
async def main():
    """
    Main loop for testing the agent
    """
    print("🌱 Renewable Energy Analyst Agent (Improved)")
    print("=" * 50)
    print("Ask me questions about renewable energy and mathematics!")
    print("Type 'q', 'quit', or 'exit' to stop.")
    print("Type 'register' to provide your name and email.")
    if USE_MOCK_MODE:
        print("🔧 Running in MOCK MODE - no OpenAI API calls")
    print("=" * 50)
    
    renewable_agent = RenewableEnergyAgent()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("\n👋 Goodbye! Thanks for exploring renewable energy!")
                break
            
            if not user_input:
                print("Please enter a message.")
                continue
            
            # Process message
            print("\n🤔 Processing...")
            response = await renewable_agent.process_message(user_input)
            
            # Display response
            print(f"\n🤖 Agent Response:")
            print(f"   Result: {response.result}")
            print(f"   Operation: {response.operation}")
            print(f"   Explanation: {response.explanation}")
            print(f"   Renewable Context: {response.renewable_context}")
            if response.units:
                print(f"   Units: {response.units}")
            print(f"   Confidence: {response.confidence:.2f}")
            print(f"   Sources: {', '.join(response.sources)}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 