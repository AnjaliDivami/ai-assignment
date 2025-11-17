from fasthtml.common import *
from agent import Agent
import json

app, rt = fast_app()

# Initialize agent
agent = Agent()

# Store messages as tuples (user_message, response)
messages = []

# Store cart items as dict {product_name: {"quantity": int, "color": str}}
cart = {}

@rt('/')
def get():
    global messages, cart
    messages = []
    cart = {}

    return Titled(
        "E-Commerce App",

        # TOP BAR
        Div(
            H1(" E-Commerce Assistant", 
               style="margin:0; padding:18px; font-size:30px; font-weight:700;"),
            style="""
                text-align:center;
                background:#ffffff;
                box-shadow:0 2px 6px rgba(0,0,0,0.1);
                margin-bottom:10px;
            """
        ),

        # MAIN LAYOUT
        Div(
            # LEFT: CHAT PANEL
            Div(
                H3("Chat", style='margin-bottom: 15px; font-weight:600;'),
                Div(
                    id='chat-result',
                    style='''
                        flex: 1;
                        overflow-y: auto;
                        padding: 20px;
                        border-radius: 12px;
                        margin-bottom: 10px;
                        max-height: calc(80vh - 120px);
                        background: #ffffff;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    '''
                ),
                style='''
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    padding: 25px;
                    border-right: 2px solid #eee;
                    background: #f7f9fc;
                '''
            ),

            # RIGHT: CART PANEL
            Div(
                H3("Cart", style='margin-bottom: 15px; font-weight:600;'),
                Div(
                    id='cart-result',
                    style='''
                        flex: 1;
                        overflow-y: auto;
                        padding: 20px;
                        border-radius: 12px;
                        background-color: #ffffff;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                        max-height: calc(80vh - 120px);
                    '''
                ),
                style='''
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    padding: 25px;
                    background:#f7f9fc;
                '''
            ),

            style='''
                display: flex;
                height: 75vh;
                background: #f0f2f5;
                border-radius: 15px;
                overflow: hidden;
            '''
        ),

        # BOTTOM INPUT AREA
        Form(
            Div(
                Input(
                    id='prompt', name='prompt',
                    placeholder='Type a message...',
                    required=True,
                    style='''
                        flex: 4;
                        padding: 12px 16px;
                        border: 1px solid #ccc;
                        border-radius: 8px;
                        font-size: 16px;
                        background:white;
                    '''
                ),
                Button(
                    'Send',
                    type='submit',
                    style='''
                        flex: 1;
                        padding: 12px;
                        margin-left: 10px;
                        background: #0066ff;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        cursor:pointer;
                    '''
                ),
                style='display: flex; align-items: center;'
            ),
            hx_post='/submit',
            hx_target='#chat-result',
            hx_swap='innerHTML',
            **{'hx-on::after-request': 'this.reset()'},
            style='''
                position: sticky;
                bottom: 0;
                background: white;
                padding: 15px;
                border-top: 1px solid #ddd;
                box-shadow: 0 -2px 12px rgba(0,0,0,0.05);
            '''
        )
    )


@rt('/submit')
async def post(prompt: str):
    try:
        response = await agent.get_response_async(prompt, cart_context=cart)

        chat_message = ""
        try:
            cleaned_response = response.strip()

            # Remove markdown code block wrapper
            if cleaned_response.startswith('```'):
                lines = cleaned_response.split('\n')
                cleaned_response = '\n'.join(lines[1:-1]).strip()

            response_data = json.loads(cleaned_response)
            action = response_data.get('action')

            if action == 'add':
                items = response_data.get('items', [])
                added_items = []

                for item in items:
                    product_name = item.get('name', 'Unknown')
                    quantity = item.get('quantity', 1)
                    color = item.get('color', '')

                    if not color or not color.strip() or color.strip() == '#':
                        color = agent.generate_color_from_title(product_name)

                    attributes = item.get('attributes', '')

                    cart_key = f"{product_name} ({attributes})" if attributes else product_name

                    if cart_key in cart:
                        cart[cart_key]['quantity'] += quantity
                    else:
                        cart[cart_key] = {'quantity': quantity, 'color': color}

                    added_items.append(f"{quantity} {cart_key}")

                chat_message = f"Added {', '.join(added_items)} to cart"

            elif action == 'remove':
                product_name = response_data.get('name', 'Unknown')
                remove_quantity = response_data.get('quantity', 0)

                found_key = None
                for key in cart.keys():
                    if key.startswith(product_name):
                        found_key = key
                        break

                if found_key:
                    current_quantity = cart[found_key]['quantity']

                    if remove_quantity == 0 or remove_quantity >= current_quantity:
                        del cart[found_key]
                        chat_message = f"Removed {found_key} from cart"
                    else:
                        cart[found_key]['quantity'] -= remove_quantity
                        chat_message = (
                            f"Removed {remove_quantity} {found_key} "
                            f"(Remaining: {cart[found_key]['quantity']})"
                        )
                else:
                    chat_message = f"{product_name} not found in cart"
            else:
                chat_message = response

        except (json.JSONDecodeError, TypeError):
            chat_message = response

        messages.append((prompt, chat_message))

        # CHAT BUBBLES
        chat_display = []
        for user_msg, bot_msg in messages:
            # RIGHT (User)
            chat_display.append(
                Div(
                    Div(
                        user_msg,
                        style='''
                            display:inline-block;
                            padding: 12px 18px;
                            background:#0078ff;
                            color:white;
                            border-radius:18px 18px 4px 18px;
                            max-width:70%;
                            line-height:1.4;
                        '''
                    ),
                    style='text-align:right; margin-bottom:10px;'
                )
            )

            # LEFT (Bot)
            chat_display.append(
                Div(
                    Div(
                        bot_msg,
                        style='''
                            display:inline-block;
                            padding: 12px 18px;
                            background:#ececec;
                            color:#111;
                            border-radius:18px 18px 18px 4px;
                            max-width:70%;
                            line-height:1.4;
                        '''
                    ),
                    style='text-align:left; margin-bottom:15px;'
                )
            )

        # CART UI
        cart_display = []
        for product_name, item_data in cart.items():
            quantity = item_data['quantity']
            bg_color = item_data['color']
            text_color = agent.get_text_color(bg_color)

            cart_display.append(
                Div(
                    Div(product_name,
                        style=f'font-weight:600; font-size:18px; margin-bottom:6px; color:{text_color}'),
                    Div(f'Quantity: {quantity}',
                        style=f'font-size:15px; opacity:0.8; color:{text_color}'),
                    style=f'''
                        margin-bottom: 12px;
                        padding: 16px;
                        border-radius: 12px;
                        background-color: {bg_color};
                        box-shadow: 0 3px 8px rgba(0,0,0,0.15);
                        transition: transform 0.2s;
                    ''',
                    onmouseover="this.style.transform='scale(1.02)'",
                    onmouseout="this.style.transform='scale(1)'"
                )
            )

        return Div(
            Div(*chat_display),
            Div(*cart_display, id='cart-result', hx_swap_oob='true')
        )

    except Exception as e:
        return Div(f"Error: {str(e)}", style='color:red; padding:10px;')


serve(port=8001)
