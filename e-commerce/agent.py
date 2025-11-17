from pydantic_ai import Agent as PydanticAgent
import asyncio
import logfire
from dotenv import load_dotenv
import os
import json
import hashlib

load_dotenv(override=True)
logfire.configure()
logfire.instrument_pydantic_ai()

# Get API key from environment - this will be automatically picked up by pydantic-ai
google_api_key = os.getenv("GOOGLE_API_KEY")

# Strip any whitespace or quotes that might have been added
if google_api_key:
    google_api_key = google_api_key.strip().strip('"').strip("'")
    # Set it back to environment for pydantic-ai to use
    os.environ["GOOGLE_API_KEY"] = google_api_key

# Check if API key is set
if not google_api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please check your .env file"
    )

print(f"Using API key: {google_api_key[:10]}...{google_api_key[-4:] if len(google_api_key) > 14 else ''}")

# Validate API key format
if not google_api_key.startswith("AIza"):
    raise ValueError(
        f"Invalid Google API key format. Google API keys should start with 'AIza'. "
        f"Your key starts with: {google_api_key[:10]}"
    )

model = "gemini-2.5-flash"

class Agent:
    def __init__(self):
        # System prompt to handle e-commerce product additions and removals
        system_prompt = """
You are a helpful e-commerce assistant. 

When the user wants to ADD products (can be multiple items):
Respond with: {"action": "add", "items": [{"name": "ProductName", "quantity": number, "color": "#hexcolor", "attributes": "description"}]}
Identify the natural color of each product and provide it as a hex color code
For clothing items, include color/size in attributes
Examples: 
  * "add grapes" → {"action": "add", "items": [{"name": "Grapes", "quantity": 1, "color": "#8B4789", "attributes": ""}]}
  * "3 apples" → {"action": "add", "items": [{"name": "Apples", "quantity": 3, "color": "#DC143C", "attributes": ""}]}
  * "purple top with white pant" → {"action": "add", "items": [{"name": "Top", "quantity": 1, "color": "#800080", "attributes": "Purple"}, {"name": "Pant", "quantity": 1, "color": "#FFFFFF", "attributes": "White"}]}
  * "red shirt size M" → {"action": "add", "items": [{"name": "Shirt", "quantity": 1, "color": "#DC143C", "attributes": "Red, Size M"}]}

When the user wants to REMOVE a product:
Respond with: {"action": "remove", "name": "ProductName", "quantity": number}
If no quantity specified, set quantity to 0 (remove all)
Examples: 
  * "remove grapes" → {"action": "remove", "name": "Grapes", "quantity": 0}
  * "remove 1 laptop" → {"action": "remove", "name": "Laptop", "quantity": 1}
  * "remove 2 apples" → {"action": "remove", "name": "Apples", "quantity": 2}

When the user asks about their cart (like "how many items", "what's in my cart", "total items"):
Look at the cart contents provided in the message context
Answer their question naturally based on the cart data
Do NOT return JSON, just respond with text

Always capitalize product names properly. ONLY return JSON for add/remove actions.

For other questions, respond normally with text.
"""
        # pydantic-ai will automatically use GOOGLE_API_KEY from environment
        self.agent = PydanticAgent(model, system_prompt=system_prompt)
        self.message_history = []
    
    async def get_response_async(self, user_message: str, cart_context: dict = None) -> str:
        """Get a response from the AI agent asynchronously"""
        # Add cart context to the message if available
        if cart_context:
            cart_info = "\n\nCurrent cart contents:\n"
            if not cart_context:
                cart_info += "Cart is empty"
            else:
                for item_name, item_data in cart_context.items():
                    cart_info += f"- {item_name}: {item_data['quantity']} item(s)\n"
            
            enhanced_message = user_message + cart_info
        else:
            enhanced_message = user_message
        
        # Pass the message history to maintain context
        response = await self.agent.run(enhanced_message, message_history=self.message_history)
        
        # Update message history with new messages from this run
        self.message_history = response.all_messages()
        
        return response.output
    
    def get_response(self, user_message: str) -> str:
        """Synchronous wrapper for get_response_async"""
        return asyncio.run(self.get_response_async(user_message))
    
    @staticmethod
    def generate_color_from_title(title: str) -> str:
        """Generate a consistent color from a title using hash"""
        # Generate hash from title
        hash_object = hashlib.md5(title.encode())
        hash_hex = hash_object.hexdigest()
        
        # Use first 6 characters as color, ensure it's not too dark
        r = int(hash_hex[0:2], 16)
        g = int(hash_hex[2:4], 16)
        b = int(hash_hex[4:6], 16)
        
        # Make colors lighter by ensuring minimum brightness
        r = max(r, 100)
        g = max(g, 100)
        b = max(b, 100)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def get_text_color(bg_color: str) -> str:
        """Determine if text should be white or black based on background color brightness"""
        try:
            # Remove # if present and handle empty/invalid colors
            hex_color = bg_color.lstrip('#').strip()
            
            # Default to black text if color is invalid
            if not hex_color or len(hex_color) < 6:
                return '#000000'
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Calculate relative luminance (perceived brightness)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            
            # Return black text for light backgrounds, white text for dark backgrounds
            return '#000000' if luminance > 0.5 else '#FFFFFF'
        except (ValueError, IndexError):
            # Default to black text on error
            return '#000000'
