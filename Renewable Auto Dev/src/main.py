"""Main application entry point for the Renewable Energy AI Agent Ecosystem."""

import asyncio
import argparse
import uuid
from typing import Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from .core.config import settings
from .core.logging import get_logger
from .agents.renewable_energy_agent import RenewableEnergyAgent
from .agents.base_agent import AgentContext
from .database.supabase_client import db_client
from .database.models import Conversation

logger = get_logger(__name__)
console = Console()


class RenewableEnergyAgentApp:
    """Main application class for the renewable energy AI agent ecosystem."""
    
    def __init__(self):
        """Initialize the application."""
        self.agent = None
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize the application components."""
        try:
            console.print(Panel.fit(
                "[bold green]Renewable Energy AI Agent Ecosystem[/bold green]\n"
                "[dim]Initializing...[/dim]",
                title="🌱 Welcome"
            ))
            
            # Initialize the main agent
            self.agent = RenewableEnergyAgent()
            
            # Create conversation record
            conversation = Conversation(
                session_id=self.session_id,
                messages=[],
                context={"app_version": settings.app.app_version}
            )
            await db_client.create_conversation(conversation)
            
            console.print("[green]✓[/green] Application initialized successfully!")
            logger.info("Application initialized")
            
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to initialize application: {e}")
            logger.error(f"Failed to initialize application: {e}")
            raise
    
    async def start_interactive_session(self):
        """Start an interactive chat session with the agent."""
        console.print(Panel.fit(
            "[bold blue]Interactive Session Started[/bold blue]\n"
            "[dim]Type 'exit' to quit, 'help' for commands[/dim]",
            title="💬 Chat"
        ))
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[cyan]You[/cyan]")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'status':
                    await self._show_status()
                    continue
                
                if user_input.lower() == 'clear':
                    self.conversation_history = []
                    console.print("[dim]Conversation history cleared[/dim]")
                    continue
                
                # Process the query
                await self._process_user_query(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted. Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.error(f"Error in interactive session: {e}")
    
    async def _process_user_query(self, query: str):
        """Process a user query and display the response."""
        try:
            # Show thinking indicator
            with console.status("[dim]Processing your query...[/dim]"):
                # Create context
                context = AgentContext(
                    user_query=query,
                    session_id=self.session_id,
                    conversation_history=self.conversation_history
                )
                
                # Get response from agent
                response = await self.agent.process_query(context)
            
            # Display response
            self._display_response(response)
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": query},
                {"role": "assistant", "content": response.content}
            ])
            
            # Update conversation in database
            await db_client.update_conversation(
                self.session_id,
                {"messages": self.conversation_history}
            )
            
        except Exception as e:
            console.print(f"[red]Failed to process query: {e}[/red]")
            logger.error(f"Failed to process query: {e}")
    
    def _display_response(self, response):
        """Display agent response in a formatted way."""
        # Main response content
        console.print(Panel(
            response.content,
            title=f"🤖 {response.metadata.get('agent_name', 'Agent')}",
            title_align="left",
            border_style="green"
        ))
        
        # Show confidence and sources if available
        info_parts = []
        if response.confidence:
            confidence_color = "green" if response.confidence > 0.7 else "yellow" if response.confidence > 0.4 else "red"
            info_parts.append(f"[{confidence_color}]Confidence: {response.confidence:.1%}[/{confidence_color}]")
        
        if response.sources:
            info_parts.append(f"[dim]Sources: {', '.join(response.sources[:3])}[/dim]")
        
        if info_parts:
            console.print(" | ".join(info_parts))
    
    def _show_help(self):
        """Show help information."""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("help", "Show this help message")
        help_table.add_row("status", "Show agent and system status")
        help_table.add_row("clear", "Clear conversation history")
        help_table.add_row("exit/quit/bye", "Exit the application")
        
        console.print(help_table)
        
        console.print(Panel(
            "[bold]Example Questions:[/bold]\n"
            "• What are the key considerations for a 100MW solar farm?\n"
            "• How do I calculate LCOE for a wind project?\n"
            "• What permits are needed for renewable energy projects?\n"
            "• Explain the latest solar panel technologies\n"
            "• What are the financing options for clean energy projects?",
            title="💡 Tips"
        ))
    
    async def _show_status(self):
        """Show agent and system status."""
        status_table = Table(title="System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="white")
        status_table.add_column("Details", style="dim")
        
        # Agent status
        agent_status = await self.agent.get_status()
        status_table.add_row(
            "Agent",
            "[green]Active[/green]",
            f"{agent_status['name']} ({agent_status['type']})"
        )
        
        # Database status
        try:
            # Simple database check
            await db_client.list_agents()
            status_table.add_row("Database", "[green]Connected[/green]", "Supabase")
        except Exception:
            status_table.add_row("Database", "[red]Error[/red]", "Connection failed")
        
        # Session info
        status_table.add_row(
            "Session",
            "[blue]Active[/blue]",
            f"ID: {self.session_id[:8]}..."
        )
        
        status_table.add_row(
            "Conversation",
            "[white]Active[/white]",
            f"{len(self.conversation_history)} messages"
        )
        
        console.print(status_table)


async def main():
    """Main application function."""
    parser = argparse.ArgumentParser(description="Renewable Energy AI Agent Ecosystem")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Initialize and start the application
    app = RenewableEnergyAgentApp()
    
    try:
        await app.initialize()
        await app.start_interactive_session()
    except Exception as e:
        console.print(f"[red]Application failed: {e}[/red]")
        logger.error(f"Application failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 