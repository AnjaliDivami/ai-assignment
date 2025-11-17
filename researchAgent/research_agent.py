from pydantic_ai import Agent
import asyncio
import logfire
from dotenv import load_dotenv
import time
from tools import web_search, save_research, get_date_time

# Load environment variables
load_dotenv(override=True)

# Configure logfire for monitoring
logfire.configure()
logfire.instrument_pydantic_ai()

# Use Gemini 2.5 Flash (available model for Google AI Studio)
model = "gemini-2.5-flash"

# Create the research agent with tools
agent = Agent(
    model,
    system_prompt="""You are an expert research assistant focused on gathering, analyzing, and presenting information.
    
    Your capabilities:
    - 🔍 Search the web for current information, facts, and research
    - 💾 Save research findings to files for later reference
    - 📅 Provide current date and time information
    
    When conducting research:
    1. Use web_search to find information on topics you need to research
    2. Synthesize information from multiple searches if needed
    3. Provide clear, well-organized summaries with key findings
    4. Cite sources when available
    
    CRITICAL - When saving research:
    - ONLY call save_research when user explicitly says "save", "store", "keep", or "write to file"
    - Pass your COMPLETE RESEARCH RESPONSE as the 'content' parameter
    - Include ALL findings, facts, summaries, and source URLs you gathered
    - The content should be the SAME comprehensive answer you would give to the user
    - After saving, tell the user where the file was saved
    
    Example workflow for "research Python and save it":
    1. Call web_search("Python programming")
    2. Prepare detailed summary with findings
    3. Call save_research(topic="Python programming", content="[Your complete detailed research with all findings and sources]")
    4. Respond to user with the summary AND confirm file was saved
    
    Always be thorough, accurate, and cite your sources when possible.
    """,
    tools=[web_search, save_research, get_date_time]
)

time.sleep(1)


async def main():
    """Main function to run the research agent"""
    message_history = []  # Initialize empty message history
    
    print("=" * 70)
    print("🔬 RESEARCH AGENT - Powered by Gemini 2.5 Flash")
    print("=" * 70)
    print("I can help you research any topic using web search!")
    print("\nAvailable capabilities:")
    print("  🔍 Web search for information and facts")
    print("  💾 Save research findings to files")
    print("  📅 Get current date and time")
    print("\nType 'exit', 'quit', or 'bye' to end the session.")
    print("=" * 70)
    print()

    while True:
        try:
            message = input("You: ")
            
            if message.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye! Happy researching!")
                break
            
            if not message.strip():
                continue

            # Run agent with message history for context
            response = await agent.run(message, message_history=message_history)
            print(f"\n🤖 Agent:\n{response.output}\n")

            # Update message history to maintain conversation context
            message_history = response.all_messages()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Happy researching!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            logfire.error(f"Error in main loop: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
