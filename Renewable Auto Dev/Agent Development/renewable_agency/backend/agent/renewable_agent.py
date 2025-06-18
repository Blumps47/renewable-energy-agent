"""
Renewable Energy Analyst Agent using PydanticAI
"""

import os
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI

from .models import MathResponse, UserRegistration
from .tools import add_numbers, subtract_numbers, multiply_numbers, divide_numbers, get_renewable_context

# Load environment variables from project root
# Get the path to project root (5 levels up: agent -> backend -> renewable_agency -> Agent Development -> project_root)
project_root = Path(__file__).parent.parent.parent.parent.parent
env_path = project_root / '.env'
print(f"🔍 Loading .env from: {env_path}")
load_result = load_dotenv(env_path)
print(f"📁 .env loaded successfully: {load_result}")

# Check if we should use mock mode (for testing without API key)
USE_MOCK_MODE = os.getenv('USE_MOCK_MODE', 'false').lower() == 'true'
print(f"🎭 USE_MOCK_MODE: {USE_MOCK_MODE}")

# Debug: Print OpenAI key status
openai_key = os.getenv('OPENAI_API_KEY')
print(f"🔑 OpenAI API Key found: {'Yes' if openai_key else 'No'}")
if openai_key:
    print(f"🔑 Key length: {len(openai_key)} characters")
    print(f"🔑 Key preview: {openai_key[:20]}...{openai_key[-10:]}")

if not USE_MOCK_MODE:
    # Initialize OpenAI model
    model = OpenAIModel('gpt-4o-mini')
else:
    print("🔧 Running in MOCK MODE - no OpenAI API calls will be made")
    model = None

# Create agent with memory and structured response
agent = Agent(
    model=model,
    result_type=MathResponse,
    system_prompt="""You are a specialized Renewable Energy Analyst Agent with expertise in:
    - Solar, wind, hydro, geothermal, and other renewable energy technologies
    - Energy markets like ERCOT, CAISO, PJM, and international markets
    - Energy calculations and mathematical analysis
    - Power generation and capacity planning
    - Energy efficiency and sustainability metrics
    - Climate change and environmental impact
    - Energy storage and grid integration
    - Policy and regulatory frameworks

    INSTRUCTIONS:
    1. For mathematical questions: Use the available tools (add, subtract, multiply, divide) and provide renewable energy context
    2. For general renewable energy questions: Provide comprehensive, educational responses about the topic
    3. For ERCOT questions: Discuss Texas electricity market, renewable integration, grid challenges, and opportunities
    4. Always respond in MathResponse format, but adapt the fields creatively:
       - For math: Use result, operation, explanation with calculations
       - For general topics: Use result=0, operation="information", explanation with detailed content
       - renewable_context: Always provide relevant renewable energy insights
       - confidence: Your confidence in the information (0.8-1.0 for factual content)
       - sources: Relevant data sources or organizations

    TOOLS AVAILABLE:
    - add_tool: Add two numbers together
    - subtract_tool: Subtract one number from another  
    - multiply_tool: Multiply two numbers
    - divide_tool: Divide one number by another

    EXAMPLE RESPONSES:
    - Math: "What is 10 + 5?" → Use add_tool, provide kW capacity context
    - General: "Tell me about ERCOT" → operation="information", detailed explanation about Texas grid
    - Policy: "What are renewable energy incentives?" → operation="information", comprehensive policy overview

    Always be helpful, accurate, and provide educational context about renewable energy and sustainability."""
)

# Runtime context for user data
class RenewableContext:
    def __init__(self):
        self.user_data: Dict[str, Any] = {}
        self.conversation_history: list = []
        self.user_preferences: Dict[str, Any] = {}

# Global context instance
context = RenewableContext()

@agent.tool_plain
def add_tool(a: float, b: float) -> dict:
    """Add two numbers together"""
    result = add_numbers(a, b)
    result["renewable_context"] = get_renewable_context("addition", result["result"], a, b)
    return result

@agent.tool_plain
def subtract_tool(a: float, b: float) -> dict:
    """Subtract second number from first number"""
    result = subtract_numbers(a, b)
    result["renewable_context"] = get_renewable_context("subtraction", result["result"], a, b)
    return result

@agent.tool_plain
def multiply_tool(a: float, b: float) -> dict:
    """Multiply two numbers together"""
    result = multiply_numbers(a, b)
    result["renewable_context"] = get_renewable_context("multiplication", result["result"], a, b)
    return result

@agent.tool_plain
def divide_tool(a: float, b: float) -> dict:
    """Divide first number by second number"""
    result = divide_numbers(a, b)
    result["renewable_context"] = get_renewable_context("division", result["result"], a, b)
    return result

@agent.tool_plain
def register_user(name: str, email: str) -> dict:
    """Register user with name and email for tracking"""
    try:
        user_reg = UserRegistration(name=name, email=email)
        context.user_data = {
            "name": user_reg.name,
            "email": user_reg.email,
            "registered": True
        }
        return {
            "success": True,
            "message": f"Successfully registered {name} with email {email}",
            "user_id": f"user_{hash(email) % 10000}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Registration failed: {str(e)}",
            "user_id": None
        }

class RenewableEnergyAgent:
    """
    Main agent class for handling renewable energy analysis
    """
    
    def __init__(self):
        self.agent = agent
        self.context = context
        
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
            if USE_MOCK_MODE or model is None:
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
        import re
        
        # Check for renewable energy topics first
        message_lower = message.lower()
        
        # ERCOT-specific responses
        if 'ercot' in message_lower:
            return MathResponse(
                result=0.0,
                operation="information",
                explanation="ERCOT (Electric Reliability Council of Texas) manages the electric grid for about 90% of Texas. The grid serves over 26 million customers and has seen massive renewable energy growth, particularly wind and solar. Texas leads the US in wind generation and is rapidly expanding solar capacity. ERCOT faces unique challenges with renewable integration, including managing intermittency and ensuring grid stability during extreme weather events.",
                renewable_context="ERCOT has become a leading example of renewable energy integration at scale. Wind power provides over 25% of ERCOT's electricity, with solar growing rapidly. The grid operates as an energy-only market, which creates both opportunities and challenges for renewable energy development. Recent winter storms have highlighted the importance of winterization and grid resilience.",
                units="information",
                confidence=0.9,
                sources=["ERCOT", "EIA", "Texas Public Utility Commission"]
            )
        
        # General renewable energy topics
        elif any(term in message_lower for term in ['renewable', 'solar', 'wind', 'clean energy', 'sustainability']):
            return MathResponse(
                result=0.0,
                operation="information", 
                explanation="Renewable energy comes from naturally replenishing sources like sunlight, wind, rain, tides, waves, and geothermal heat. These sources are sustainable and have minimal environmental impact compared to fossil fuels. The main types include solar (photovoltaic and thermal), wind (onshore and offshore), hydroelectric, geothermal, and biomass. Renewable energy is crucial for reducing greenhouse gas emissions and combating climate change.",
                renewable_context="The renewable energy sector has experienced dramatic cost reductions and technological improvements. Solar and wind are now the cheapest sources of electricity in many regions. Energy storage technologies like batteries are solving intermittency challenges, making renewables more reliable and dispatchable.",
                units="information",
                confidence=0.95,
                sources=["International Renewable Energy Agency (IRENA)", "U.S. Department of Energy", "National Renewable Energy Laboratory (NREL)"]
            )
        
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
    print("🌱 Renewable Energy Analyst Agent")
    print("=" * 50)
    print("Ask me questions about renewable energy and mathematics!")
    print("Type 'q', 'quit', or 'exit' to stop.")
    print("Type 'register' to provide your name and email.")
    print("=" * 50)
    
    renewable_agent = RenewableEnergyAgent()
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("\n👋 Thank you for using the Renewable Energy Analyst Agent!")
                break
            
            if user_input.lower() == 'register':
                name = input("📝 Enter your full name: ").strip()
                email = input("📧 Enter your email address: ").strip()
                
                if name and email:
                    reg_result = register_user(name, email)
                    print(f"\n✅ {reg_result['message']}")
                    if reg_result['success']:
                        print(f"🆔 Your user ID: {reg_result['user_id']}")
                else:
                    print("\n❌ Please provide both name and email.")
                continue
            
            if not user_input:
                print("❓ Please enter a message or question.")
                continue
            
            print("\n🤖 Agent: Processing your request...")
            
            # Process the message
            response = await renewable_agent.process_message(user_input)
            
            # Display the structured response
            print(f"\n📊 Result: {response.result}")
            print(f"🔧 Operation: {response.operation}")
            print(f"💡 Explanation: {response.explanation}")
            
            if response.renewable_context:
                print(f"🌱 Renewable Context: {response.renewable_context}")
            
            if response.units:
                print(f"📏 Units: {response.units}")
            
            print(f"🎯 Confidence: {response.confidence:.1%}")
            
            if response.sources:
                print(f"📚 Sources: {', '.join(response.sources)}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    # Run the main testing loop
    asyncio.run(main()) 