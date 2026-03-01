import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('sales.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS sales (
    date TEXT,
    amount REAL
)
''')
conn.commit()

st.title("Daily Sales Tracker")

date = st.date_input("Select Date")
amount = st.number_input("Enter Sales Amount")

if st.button("Save"):
    c.execute("INSERT INTO sales VALUES (?,?)", (str(date), amount))
    conn.commit()
    st.success("Saved!")

df = pd.read_sql("SELECT * FROM sales", conn)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

weekly = df.resample('W').sum()

st.line_chart(weekly)