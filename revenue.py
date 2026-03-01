import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('studio.db', check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    product_id INTEGER,
    quantity INTEGER,
    total REAL
)
''')
conn.commit()

st.title("📸 Photo Studio Sales Dashboard")

# Insert default products (run once)
products_list = [
    ("Softcopy", 5000),
    ("4x6 Photo", 1000),
    ("A4 Board", 25000),
    ("A3 Board", 35000),
    ("A2 Board", 50000),
    ("A4 Frame", 30000),
    ("A3 Frame", 45000),
    ("Printing", 2000)
]

for p in products_list:
    c.execute("INSERT OR IGNORE INTO products (name, price) VALUES (?,?)", p)
conn.commit()

# Fetch products
products = pd.read_sql("SELECT * FROM products", conn)

# Input section
st.subheader("Enter Daily Sale")

date = st.date_input("Date")
product_name = st.selectbox("Select Product", products['name'])
quantity = st.number_input("Quantity", min_value=1)

if st.button("Save Sale"):
    product = products[products['name'] == product_name].iloc[0]
    total = quantity * product['price']
    c.execute("INSERT INTO sales (date, product_id, quantity, total) VALUES (?,?,?,?)",
              (str(date), product['id'], quantity, total))
    conn.commit()
    st.success(f"Saved! Total = {total}")

# Load sales
sales = pd.read_sql("SELECT * FROM sales", conn)
sales['date'] = pd.to_datetime(sales['date'])
sales.set_index('date', inplace=True)

# Weekly revenue
weekly = sales['total'].resample('W').sum()

st.subheader("📊 Weekly Revenue")
st.line_chart(weekly)

# Revenue by product
merged = sales.merge(products, left_on='product_id', right_on='id')
product_summary = merged.groupby('name')['total'].sum()

st.subheader("💰 Revenue by Product")
st.bar_chart(product_summary)
