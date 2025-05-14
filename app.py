import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Initialize session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Function to fetch data from Flask server
@st.cache_data
def fetch_data(table_name):
    response = requests.get(f"https://b59c-2a06-c701-bc8e-9800-e882-70fd-a82f-ef9e.ngrok-free.app/{table_name}")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error(f"Error fetching data from {table_name}")
        return pd.DataFrame()

# Load data
your_store_df = fetch_data("your_store")
competitor_df = fetch_data("competitor_store")

# Merge dataframes
merged_df = your_store_df.merge(competitor_df, on=["ItemCode", "Product Name", "Unit"], suffixes=("_your", "_competitor"))
merged_df = merged_df[["ItemCode", "Product Name", "Price_your", "Price_competitor", "Unit"]]

# Create two columns for 50:50 layout
col1, col2 = st.columns([1, 1])

# Shopping Cart (Left Column)
with col1:
    st.markdown("<h3 style='font-family: Arial; font-size: 18px;'>Shopping Cart</h3>", unsafe_allow_html=True)
    
    if st.session_state.cart:
        cart_items = []
        for item in st.session_state.cart:
            item_code = item['ItemCode']
            qty = item['quantity']
            product_row = merged_df[merged_df['ItemCode'] == item_code].iloc[0]
            product_name = product_row['Product Name']
            price_your = product_row['Price_your']
            price_competitor = product_row['Price_competitor']
            unit = product_row['Unit']
            
            # Inline prices with color and bold
            cart_entry = f"{product_name} (Qty: {qty}, "
            cart_entry += f"<span style='color: #008000; font-family: Arial; font-size: 14px;'>Your Store: <b>${price_your:.2f}</b></span>, "
            cart_entry += f"<span style='color: #FF0000; font-family: Arial; font-size: 14px;'>Competitor: <b>${price_competitor:.2f}</b></span>) "
            cart_entry += f"[{unit}]"
            cart_items.append((item_code, qty, cart_entry))
        
        for item_code, qty, cart_entry in cart_items:
            st.markdown(cart_entry, unsafe_allow_html=True)
            col_plus, col_minus, col_delete = st.columns([1, 1, 1])
            with col_plus:
                if st.button("➕", key=f"plus_{item_code}"):
                    for item in st.session_state.cart:
                        if item['ItemCode'] == item_code:
                            item['quantity'] += 1
                            st.rerun()
            with col_minus:
                if st.button("➖", key=f"minus_{item_code}"):
                    for item in st.session_state.cart:
                        if item['ItemCode'] == item_code:
                            if item['quantity'] > 1:
                                item['quantity'] -= 1
                            else:
                                st.session_state.cart.remove(item)
                            st.rerun()
            with col_delete:
                if st.button("🗑️", key=f"delete_{item_code}"):
                    st.session_state.cart = [item for item in st.session_state.cart if item['ItemCode'] != item_code]
                    st.rerun()
        
        # Export Buttons
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            if st.button("Export List with Prices"):
                export_content = ""
                for item in st.session_state.cart:
                    product_row = merged_df[merged_df['ItemCode'] == item['ItemCode']].iloc[0]
                    export_content += f"{product_row['Product Name']}: {item['quantity']} "
                    export_content += f"(Your Store: ${product_row['Price_your']:.2f}, Competitor: ${product_row['Price_competitor']:.2f}) "
                    export_content += f"[{product_row['Unit']}]\n"
                st.download_button(
                    label="Download List with Prices",
                    data=export_content,
                    file_name="shopping_list.txt",
                    mime="text/plain"
                )
        with col_export2:
            if st.button("Export List without Prices"):
                export_content = ""
                for item in st.session_state.cart:
                    product_row = merged_df[merged_df['ItemCode'] == item['ItemCode']].iloc[0]
                    export_content += f"{product_row['Product Name']}: {item['quantity']} [{product_row['Unit']}]\n"
                st.download_button(
                    label="Download List without Prices",
                    data=export_content,
                    file_name="shopping_list.txt",
                    mime="text/plain"
                )
    else:
        st.write("Cart is empty")

# Product Selection (Right Column)
with col2:
    st.markdown("<h3 style='font-family: Arial; font-size: 18px;'>Select Product</h3>", unsafe_allow_html=True)
    
    product_options = merged_df.apply(
        lambda row: f"{row['Product Name']} (Your Store: ${row['Price_your']:.2f}, Competitor: ${row['Price_competitor']:.2f}) [{row['Unit']}]",
        axis=1
    ).tolist()
    product_dict = dict(zip(product_options, merged_df['ItemCode']))
    
    selected_product = st.selectbox("Choose a product", product_options, key="product_select")
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key="quantity")
    
    if st.button("Add to Cart"):
        item_code = product_dict[selected_product]
        existing_item = next((item for item in st.session_state.cart if item['ItemCode'] == item_code), None)
        if existing_item:
            existing_item['quantity'] += quantity
        else:
            st.session_state.cart.append({'ItemCode': item_code, 'quantity': quantity})
        st.rerun()