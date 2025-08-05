import streamlit as st
import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime

DB_PATH = "trade_db.sqlite"

FIX_TAGS = {
    "8": "BeginString", "35": "MsgType", "49": "SenderCompID", "56": "TargetCompID", "34": "MsgSeqNum",
    "52": "SendingTime", "11": "ClOrdID", "21": "HandlInst", "55": "Symbol", "54": "Side",
    "38": "OrderQty", "40": "OrdType", "44": "Price", "10": "CheckSum"
}

def generate_fix_message(cl_ord_id, symbol, side, quantity, price):
    side_val = "1" if side == "Buy" else "2"
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    fix_parts = {
        "8": "FIX.4.2",
        "35": "D",
        "49": "CLIENT1",
        "56": "BROKERX",
        "34": "1",
        "52": timestamp,
        "11": cl_ord_id,
        "21": "1",
        "55": symbol,
        "54": side_val,
        "38": str(int(quantity)),
        "40": "2",
        "44": f"{price:.2f}",
        "10": "000"
    }
    raw_msg = "|".join([f"{k}={v}" for k, v in fix_parts.items()])
    return raw_msg, fix_parts

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cl_ord_id TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity INTEGER,
                    price REAL,
                    status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def refresh_trade_blotter():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM trades ORDER BY timestamp DESC", conn)
    conn.close()

    # Compute Trade Value (formatted to 2 decimal places)
    df["Trade Value"] = df["quantity"] * df["price"]

    # Reorder columns
    df = df[[
        "cl_ord_id", "symbol", "side", "quantity", "price",
        "Trade Value", "status", "timestamp"
    ]]

    # Rename columns
    df.columns = [
        "Client Order ID", "Symbol", "Side", "Quantity", "Price",
        "Trade Value", "Status", "Timestamp"
    ]

    # Format Price and Trade Value to 2 decimal places with $
    df["Price"] = df["Price"].apply(lambda x: f"${x:.2f}")
    df["Trade Value"] = df["Trade Value"].apply(lambda x: f"${x:.2f}")

    # Styling for Side column
    def highlight_side(val):
        color = "green" if val == "Buy" else "red"
        return f"color: {color}; font-weight: bold"

    styled_df = df.style.applymap(highlight_side, subset=["Side"])
    st.dataframe(styled_df)

def oms_ui():
    init_db()

    if "fetched_symbol" not in st.session_state:
        st.session_state.fetched_symbol = ""
    if "fetched_price" not in st.session_state:
        st.session_state.fetched_price = 0.0
    if "fix_msg_raw" not in st.session_state:
        st.session_state.fix_msg_raw = ""
    if "fix_msg_dict" not in st.session_state:
        st.session_state.fix_msg_dict = {}

    # Split Layout – Left = Fetch + Form, Right = FIX Message
    col1, col2 = st.columns(2)

    # --- Left Side: Fetch Price + Order Form ---
    with col1:
        # Moved inside left column
        with st.form("fetch_price_form"):
            input_symbol = st.text_input("Enter Stock Symbol", "AAPL").upper()
            fetch_price = st.form_submit_button("Fetch Live Price")

        if fetch_price:
            try:
                ticker = yf.Ticker(input_symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = round(hist["Close"].iloc[-1], 2)
                    st.session_state.fetched_symbol = input_symbol
                    st.session_state.fetched_price = price
                    st.success(f"Fetched live price for {input_symbol}: ${price}")
                    
                    try:
                        company_name = ticker.info.get("longName")
                        if company_name:
                            st.session_state.fetched_company_name = company_name
                        else:
                            st.session_state.fetched_company_name = None
                    except:
                        st.session_state.fetched_company_name = None
                        
                else:
                    st.warning("No price data found.")
            except Exception as e:
                st.error(f"Error: {e}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT cl_ord_id FROM trades ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row and row[0]:
            last_id = row[0]
            prefix = ''.join(filter(str.isalpha, last_id)) or "ORD"
            num = int(''.join(filter(str.isdigit, last_id))) + 1
            new_cl_ord_id = f"{prefix}{num:03}"
        else:
            new_cl_ord_id = "ORD001"

        with st.form("order_form"):
            st.markdown("### 📝 Place Order")
            cl_ord_id = st.text_input("Client Order ID", new_cl_ord_id)
            symbol = st.text_input("Symbol", st.session_state.fetched_symbol or "AAPL", disabled=True)
            
            st.text_input("Company Name", st.session_state.get("fetched_company_name", "Apple Inc."), disabled=True)
            
            side = st.selectbox("Side", ["Buy", "Sell"])
            quantity = st.number_input("Quantity", 10)
            price = st.number_input("Price", value=st.session_state.fetched_price or 202.00, disabled=True)

            submit = st.form_submit_button("Submit Order")

            if submit:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''INSERT INTO trades 
                             (cl_ord_id, symbol, side, quantity, price, status, timestamp) 
                             VALUES (?, ?, ?, ?, ?, ?, datetime('now'))''',
                          (cl_ord_id, symbol, side, quantity, price, "New"))
                conn.commit()
                conn.close()

                raw_msg, parsed = generate_fix_message(cl_ord_id, symbol, side, quantity, price)
                st.session_state.fix_msg_raw = raw_msg
                st.session_state.fix_msg_dict = parsed
                st.success(f"✅ Order for {symbol} at ${price} submitted.")
                st.session_state.refresh_blotter = True

    # --- Right Side: FIX Viewer ---
    with col2:
        st.markdown("#### 💬 FIX Message")

        if st.session_state.fix_msg_raw:
            st.text_area("Raw FIX Message", st.session_state.fix_msg_raw.replace("|", " | "), height=100)

            st.markdown("#### 🔍 Parsed FIX Message")
            fix_df = pd.DataFrame([
                {
                    "Tag": tag,
                    "Tag Name": FIX_TAGS.get(tag, "Unknown"),
                    "Value": value
                } for tag, value in st.session_state.fix_msg_dict.items()
            ])
            st.dataframe(fix_df, use_container_width=True)
        else:
            st.info("No FIX message generated yet.")

    # --- Trade Blotter ---
    st.markdown("### 📄 Trade Blotter")
    # if st.button("Refresh Trade Blotter", key="refresh_trade_blotter_popup"):
        # st.session_state.refresh_blotter = True
        
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh Trade Blotter", key="refresh_trade_blotter_popup"):
            st.session_state.refresh_blotter = True

    with col2:
        if st.button("🗑️ Delete All Records", key="delete_all_trades"):
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trades")
                conn.commit()
            st.warning("All trade records deleted.")
            st.session_state.refresh_blotter = True  # Trigger refresh after delete

    # Display the blotter table if triggered
    if st.session_state.get("refresh_blotter", False):
        refresh_trade_blotter()
        st.session_state.refresh_blotter = False
        
        