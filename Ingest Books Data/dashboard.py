import streamlit as st
import pandas as pd
import plotly.express as px

def launch_dashboard(csv_path):
    st.set_page_config(page_title="Book Insights", layout="wide")
    st.title("Book Data Ingestion Dashboard")

    df = pd.read_csv(csv_path)

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Books", len(df))
    c2.metric("Average Price", f"£{df['price'].mean():.2f}")
    c3.metric("Stock Availability", f"{df['availability'].sum()} In Stock")

    # Visualizations
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Pricing by Rating")
        fig1 = px.box(df, x='rating', y='price', color='rating')
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.subheader("Rating Distribution")
        fig2 = px.histogram(df, x='rating', color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Dataset Preview")
    st.dataframe(df.head(10))

if __name__ == "__main__":
    csv_path = "Ingest/data/transformed/books/books_transformed.csv"
    launch_dashboard(csv_path)