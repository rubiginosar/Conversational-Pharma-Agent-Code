import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Define retriever loading from disk
def load_retriever(index_path="vectorial_dbs/faiss_index_"):
    # Use same embedding model used to build the index
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"FAISS index not found at: {index_path}")

    vector = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return vector.as_retriever()

import json
def retriever_products(query: str) -> str:
    """
    Searches a pre-built FAISS vector database for pharmaceutical product information,
    and returns the results in a structured JSON format for easier parsing by LLMs.

    Parameters:
        query (str): A search term such as a product name or active ingredient.

    Returns:
        str: JSON-formatted list of matching products with fields like ProductId, Name, Price, etc.
    """
    retriever = load_retriever()
    docs = retriever.invoke(query)

    structured_results = []
    for doc in docs:
        # Extract each field assuming they are embedded in plain text
        content = doc.page_content
        item = {}

        # Use regex or line parsing to extract fields
        for line in content.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                item[key.strip()] = value.strip()
        structured_results.append(item)

    return json.dumps(structured_results, indent=2)


import json
from datetime import datetime

def write_order_to_file(user_ID, product_ID,product_name, quantity, total_price, file_path="jsons/orders.json"):
    """
    Appends a new order as a JSON object to the orders.jsonl file.

    Args:
        user_ID (str): identifier of the user placing the order.
        product_ID (str): identifier of the ordered product.
        product_name (str): Name of the product.
        quantity (float or str): Number of units ordered.
        total_price (float or str): Total price of the order.
        file_path (str): Path to the file. Default is 'orders.jsonl'.
    
    Example:
    this is what a retrieved object look like:
    Produit : DOLIPRANE 500MG COMP B/16
    DCI : PARACETAMOL
    Dosage : 500MG
    Forme : COMP.
    Laboratoire : SANOFI-AVENTIS
    Prix : 100.04 DA
    Stock disponible : 44174
    product ID: 00000830 
    here's how an order should be written: 
    write_order_to_file(
        user_ID="user0907",
        product_ID="00000830",
        product_name="DOLIPRANE 500MG COMP B/16",
        quantity=50,
        total_price=5002
    )
    
    """
    order = {
        "OrderDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "UserSubId": user_ID,
        "TotalAmount": float(total_price),
        "ProductId": product_ID,
        "ProductName": product_name,
        "Qty": float(quantity),
    }

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(order) + "\n")

def propose_alternatives(dci_query: str) -> str:
    """
    Searches a pre-built FAISS vector database for pharmaceutical product information based on DCI,
    and returns only the results that have the same exact DCI.

    Parameters:
        dci_query (str): The DCI (Active Ingredient) to search for.

    Returns:
        str: JSON-formatted list of matching products with fields like ProductId, Name, Price, etc.
    """
    retriever = load_retriever()
    docs = retriever.invoke(dci_query)

    structured_results = []
    for doc in docs:
        # Extract each field assuming they are embedded in plain text
        content = doc.page_content
        item = {}

        # Parse the content and check if DCI matches the input DCI query
        dci = None
        for line in content.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                item[key.strip()] = value.strip()
                if key.strip().lower() == 'dci':  # Assuming the DCI is labeled as "DCI"
                    dci = value.strip()

        # If the DCI matches the input query, add this item to the results
        if dci and dci.lower() == dci_query.lower():
            structured_results.append(item)

    return json.dumps(structured_results, indent=2)

def write_ocomplaint_to_file(customer_id, category,sub_category,complaint_text, file_path="jsons/claims.json"):
    """
    Appends a new complaint as a JSON object to the claims.json file.

    Args:
        customer_id (str): identifier of the user placing the complaint.
        category (str): the category of the complaint (Delivery claim, Commercial claim, Recovery claim ).
        subcategory (str): the sub category of the complaint (Driver, Salesperson, Recovery team)
        description (str): the complaint text sent by the user.
        file_path (str): Path to the file. Default is 'claims.json'.
    """
    complaint = {
        "customer_id": customer_id,
        "category": category,
        "subcategory": sub_category,
        "description": complaint_text,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(complaint) + "\n")


import os
from langchain_community.vectorstores import FAISS

# Define retriever loading from disk
def load_retriever_orders(index_path="vectorial_dbs/faiss_index_order"):
    # Use same embedding model used to build the index
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"FAISS index not found at: {index_path}")

    vector = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return vector.as_retriever()

import json
import re
import pandas as pd
from datetime import datetime

# Load and normalize CSV data globally
df_orders = pd.read_csv("data/orderlines_with_status.csv")

# Ensure OrderDate is parsed as datetime
df_orders["OrderDate"] = pd.to_datetime(df_orders["OrderDate"], errors="coerce")
df_orders["OrderDateOnly"] = df_orders["OrderDate"].dt.date
df_orders["RefOrderId"] = df_orders["RefOrderId"].astype(str)

def search_orders(query: str) -> str:
    retriever = load_retriever_orders()

    date_pattern = r"\d{4}-\d{2}-\d{2}"
    is_order_id = query.isdigit()
    is_date = bool(re.fullmatch(date_pattern, query.strip()))

    filtered_df = pd.DataFrame()

    if is_order_id:
        filtered_df = df_orders[df_orders["RefOrderId"] == query]
    elif is_date:
        try:
            query_date = datetime.strptime(query.strip(), "%Y-%m-%d").date()
            filtered_df = df_orders[df_orders["OrderDateOnly"] == query_date]
        except ValueError:
            pass

    if not filtered_df.empty:
        results = []
        for _, row in filtered_df.iterrows():
            results.append({
                "order_id": str(row["RefOrderId"]),
                "product": row["ProductName"],
                "quantity": str(row["Qty"]),
                "amount": str(row["TotalAmount"]),
                "order_date": str(row["OrderDate"]),  # <-- includes timestamp
                "status": row["status"]
            })
        return json.dumps(results, indent=2)

    # Fallback to semantic search
    docs = retriever.invoke(query)
    structured_results = []
    for doc in docs:
        content = doc.page_content
        item = {}
        for line in content.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                item[key.strip().lower().replace(" ", "_")] = value.strip()
        structured_results.append(item)

    return json.dumps(structured_results, indent=2)

def get_latest_orders_for_user(user_id: str, file_path: str = "jsons/orders.json") -> list:
    """
    Returns the latest 5 orders for a given user from a JSON Lines file.

    Args:
        user_id (str): The user ID to filter orders by.
        file_path (str): Path to the JSON Lines file containing order data.

    Returns:
        list: A list of up to 5 most recent orders (dicts) for the user.
    """
    orders = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    order = json.loads(line.strip())
                    if str(order.get("UserSubId")) == str(user_id):
                        # Add parsed date for sorting
                        try:
                            order["parsed_date"] = datetime.strptime(order["OrderDate"], "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            order["parsed_date"] = datetime.min
                        orders.append(order)
                except json.JSONDecodeError:
                    continue  # Skip malformed lines
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

    # Sort and limit to 5 latest
    latest_orders = sorted(orders, key=lambda x: x["parsed_date"], reverse=True)[:5]

    # Clean up before returning
    for order in latest_orders:
        order.pop("parsed_date", None)

    return latest_orders