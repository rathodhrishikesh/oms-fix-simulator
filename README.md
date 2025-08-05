# 💹 TradePilot - OMS & Portfolio Dashboard with FIX Message Simulation

This is a **Streamlit-based Order Management System (OMS)** that has the following functionalities:
- Simulate stock trades (Buy/Sell) for any symbol using live prices from Yahoo Finance.
- Automatically generate **FIX protocol messages** for each order.
- Store trade data in a local **SQLite database**.
- Display a **trade blotter**, compute a **live portfolio summary**, and visualize positions using styled cards and tables.

## 🔍 What is the FIX Protocol?

**FIX (Financial Information eXchange)** is an open messaging standard used for real-time exchange of securities transactions and trade-related messages. It is widely used in the financial industry between institutions, brokers, and exchanges.

In this app, each order generates a simplified FIX message (Version 4.2 – New Order Single) using appropriate tags, providing a feel of how real trading systems communicate using FIX.

---

## 🚀 Features

✅ Fetch live stock prices using [Yahoo Finance](https://finance.yahoo.com/)  
✅ Submit Buy/Sell orders with quantity and price  
✅ Generate and display raw + parsed FIX messages  
✅ View all trades in a dynamic **Trade Blotter**  
✅ View current portfolio with **net quantities and values**  
✅ Delete all records or refresh the blotter on demand  
✅ Beautiful UI using Streamlit and custom HTML components

---

## 🧰 Tech Stack

- **Python 3.10+**
- **Streamlit**
- **SQLite**
- **yFinance** (for live market data)
- **Pandas** (for portfolio aggregation & manipulation)

---

## 🚀 Visit the App Online
👉 [Open App on Streamlit](https://oms-fix-simulator.streamlit.app/)
