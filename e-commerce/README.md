# E-Commerce Assistant

An AI-powered e-commerce assistant built with FastHTML and Pydantic AI that helps users manage their shopping cart through natural language conversations.

## Features

- **Natural Language Shopping**: Add or remove products from your cart using conversational language
- **Smart Product Recognition**: Automatically identifies products, quantities, and attributes (colors, sizes)
- **Visual Cart Management**: Real-time cart visualization with color-coded items
- **Multi-Item Support**: Add multiple products in a single command
- **AI-Powered Responses**: Uses Google's Gemini 2.5 Flash model for intelligent product interpretation

## Tech Stack

- **FastHTML**: Modern Python web framework for building the UI
- **Pydantic AI**: AI agent framework for handling natural language processing
- **Google Gemini API**: Large language model for understanding user requests
- **Logfire**: Monitoring and logging
- **Python 3.14+**: Latest Python features

## Project Structure

```
e-commerce/
├── app.py           # Main FastHTML application
├── agent.py         # AI agent logic and configuration
├── .env             # Environment variables (not in repo)
└── README.md        # This file
```

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd e-commerce
   ```

2. **Install dependencies**

   ```bash
   pip install python-fasthtml pydantic-ai logfire python-dotenv
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:

   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

   To get a Google API key:

   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and paste it into your `.env` file

## Usage

1. **Start the application**

   ```bash
   python app.py
   ```

2. **Access the app**

   Open your browser and navigate to:

   ```
   http://localhost:8001
   ```

3. **Interact with the assistant**

   Example commands:

   - "Add 3 apples" - Adds 3 apples to cart
   - "Purple top with white pant" - Adds both items
   - "Red shirt size M" - Adds shirt with attributes
   - "Remove grapes" - Removes all grapes
   - "Remove 2 apples" - Removes 2 apples
   - "What's in my cart?" - Shows cart contents
   - "How many items do I have?" - Shows item count

## How It Works

### 1. Agent Configuration (`agent.py`)

The AI agent is configured with a system prompt that defines:

- **Add Action**: Recognizes product additions with JSON response format
- **Remove Action**: Handles product removal from cart
- **Query Action**: Answers questions about cart contents
- **Color Recognition**: Automatically assigns hex colors to products
- **Attribute Extraction**: Identifies sizes, colors, and other attributes

### 2. Web Application (`app.py`)

The FastHTML application provides:

- **Chat Interface**: Left panel for conversing with the AI
- **Cart Display**: Right panel showing items with visual color indicators
- **Real-time Updates**: HTMX-powered dynamic updates without page refresh
- **Session Management**: Maintains cart state during the session

### 3. Response Processing

When you send a message:

1. User input is sent to the AI agent with current cart context
2. Agent analyzes the request and returns appropriate response
3. JSON responses for add/remove actions update the cart
4. Text responses are displayed in the chat
5. Cart panel updates automatically
