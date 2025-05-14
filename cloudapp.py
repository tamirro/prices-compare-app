import streamlit as st
import pandas as pd
import requests
import base64

st.set_page_config(page_title="Grocery Price Comparison", layout="wide")

# Custom CSS for consistent cart font and button alignment
st.markdown("""
    <style>
    .cart-container {
        font-family: Arial, sans-serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        line-height: 1.5 !important;
    }
    .cart-container * {
        font-family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
    }
    .cart-container .bold {
        font-weight: 700 !important;
    }
    .cart-container .export-link {
        color: #1f77b4 !important;
        text-decoration: underline !important;
    }
    .cart-container .price {
        font-family: Arial, sans-serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
    }
    .cart-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .cart-item-text {
        flex-grow: 1;
        margin-right: 10px;
    }
    .cart-buttons {
        display: flex;
        gap: 5px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(table_name):
    response = requests.get(f" https://edb3-2a06-c701-bc8e-9800-e882-70fd-a82f-ef9e.ngrok-free.app/data/{table_name}")
    return pd.DataFrame(response.json())

your_store = load_data('your_store')
competitor_store = load_data('competitor_store')

if 'cart' not in st.session_state:
    st.session_state.cart = []

with st.sidebar:
    st.markdown('<div class="cart-container">', unsafe_allow_html=True)
    st.header("Shopping Cart")
    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df['total_price_your_store'] = cart_df['quantity'] * cart_df['price_your_store']
        cart_df['total_price_competitor'] = cart_df['quantity'] * cart_df['price_competitor']
        
        # Display cart
        st.markdown('<div class="bold">Cart Contents</div>', unsafe_allow_html=True)
        for idx, item in cart_df.iterrows():
            # Create a flex container for item text and buttons
            with st.container():
                st.markdown('<div class="cart-item">', unsafe_allow_html=True)
                # Item text
                st.markdown(
                    f'<div class="cart-item-text">{item["Product Name"]} (Qty: {item["quantity"]}, <span class="price">Your Store: ${item["total_price_your_store"]:.2f}</span>, <span class="price">Competitor: ${item["total_price_competitor"]:.2f}</span>)</div>',
                    unsafe_allow_html=True
                )
                # Buttons
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("➕", key=f"add_{idx}"):
                        st.session_state.cart[idx]['quantity'] += 1
                        st.rerun()
                with col2:
                    if st.button("➖", key=f"remove_{idx}"):
                        if st.session_state.cart[idx]['quantity'] > 1:
                            st.session_state.cart[idx]['quantity'] -= 1
                        else:
                            st.session_state.cart.pop(idx)
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"delete_{idx}"):
                        st.session_state.cart.pop(idx)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Display totals
        total_your_store = cart_df['total_price_your_store'].sum()
        total_competitor = cart_df['total_price_competitor'].sum()
        savings = total_competitor - total_your_store
        st.markdown(f'<div class="bold">Total (Your Store): ${total_your_store:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bold">Total (Competitor): ${total_competitor:.2f}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bold">Savings: ${savings:.2f}</div>', unsafe_allow_html=True)
        
        # Export shopping list
        shopping_list = "\n".join([f"{item['Product Name']}: {item['quantity']} (Your Store: ${item['total_price_your_store']:.2f}, Competitor: ${item['total_price_competitor']:.2f})" for _, item in cart_df.iterrows()])
        b64 = base64.b64encode(shopping_list.encode()).decode()
        st.markdown(f'<div><a class="export-link" href="data:text/plain;base64,{b64}" download="shopping_list.txt">Export List</a></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div>Cart is empty</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.header("Grocery Price Comparison")
selected_product = st.selectbox("Select Product", your_store['Product Name'], key="product_select")
quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key="quantity_input")

if st.button("Add to Cart", key="add_to_cart"):
    product_data = your_store[your_store['Product Name'] == selected_product].iloc[0]
    competitor_data = competitor_store[competitor_store['Product Name'] == selected_product]
    competitor_price = competitor_data['Price'].iloc[0] if not competitor_data.empty else 0
    st.session_state.cart.append({
        'Product Name': selected_product,
        'quantity': quantity,
        'price_your_store': product_data['Price'],
        'price_competitor': competitor_price
    })
    st.success(f"Added {quantity} {selected_product} to cart")
    st.rerun()