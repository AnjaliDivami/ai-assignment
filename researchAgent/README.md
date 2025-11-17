# Research Agent

A conversational AI research agent built with Pydantic AI, supporting Google Gemini and OpenAI models with conversation history.

## Features

- 🤖 Powered by **Pydantic AI**
- 💬 Maintains conversation context across multiple interactions
- 🔄 Support for multiple AI models (Google Gemini, OpenAI)
- 📊 Built-in logging and monitoring with Logfire
- ⚡ Asynchronous execution for better performance

## Prerequisites

- Python 3.9 or higher
- Google AI API key (for Gemini models) or OpenAI API key
- (Optional) Logfire token for monitoring

## Installation

1. **Clone or navigate to the project directory:**

   ```bash
   cd f:\Ai-assignment\researchAgent
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your API keys:

   ```
   GOOGLE_AI_API_KEY=your_actual_google_api_key
   OPENAI_API_KEY=your_actual_openai_api_key
   ```

## Getting API Keys

### Google AI (Gemini)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### OpenAI

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key to your `.env` file

## Usage

Run the research agent:

```bash
python research_agent.py
```

### Example Conversation:

```
You: What is machine learning?
Agent: Machine learning is a subset of artificial intelligence...

You: Can you explain neural networks?
Agent: Building on machine learning, neural networks are...

You: exit
Goodbye! Have a great day!
```

## Configuration

### Switching Models

Edit `research_agent.py` and uncomment your preferred model:

```python
# For Google Gemini (default)
model = "google-gla:gemini-2.5-flash"

# For OpenAI
# model = "openai:gpt-4.1-nano"
```

### Available Models

- **Google Gemini:**

  - `google-gla:gemini-2.5-flash` (fast, cost-effective)
  - `google-gla:gemini-2.5-pro` (more capable)

- **OpenAI:**
  - `openai:gpt-4.1-nano`
  - `openai:gpt-4o`
  - `openai:gpt-4o-mini`

## Project Structure

```
researchAgent/
├── research_agent.py      # Main application file
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your actual environment variables (not tracked)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## How It Works

1. **Initialization:** Loads environment variables and configures the AI agent
2. **Conversation Loop:** Continuously accepts user input
3. **Context Maintenance:** Stores message history to maintain conversation context
4. **Response Generation:** Sends user message + history to AI model
5. **History Update:** Updates conversation history with each interaction

## Troubleshooting

### "API key not found" error

- Make sure you've created a `.env` file (copy from `.env.example`)
- Verify your API key is correctly set in the `.env` file
- Check that the API key is valid and active

### Import errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're using Python 3.9 or higher: `python --version`

### Connection errors

- Check your internet connection
- Verify API quotas haven't been exceeded
- Ensure API keys have proper permissions

## Dependencies

- **pydantic-ai**: Framework for building AI agents
- **logfire**: Logging and monitoring
- **python-dotenv**: Environment variable management
- **asyncio**: Asynchronous I/O support

## License

This project is open source and available for educational purposes.

## Contributing

Feel free to fork this project and customize it for your needs!

## Support

For issues related to:

- Pydantic AI: [GitHub](https://github.com/pydantic/pydantic-ai)
- Google AI: [Documentation](https://ai.google.dev/)
- OpenAI: [Documentation](https://platform.openai.com/docs)
