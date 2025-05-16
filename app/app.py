

import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("zomato_preprocessed.csv")
    return df

df = load_data()

st.sidebar.header("User Preferences")

cuisines = sorted(df['Primary Cuisine'].dropna().unique())
cities = sorted(df['City'].str.lower().dropna().unique())
cost_categories = ['low', 'medium', 'high']

selected_cuisine = st.sidebar.selectbox("Select Cuisine", ['Any'] + cuisines)
selected_city = st.sidebar.selectbox("Select City", ['Any'] + cities)
selected_cost = st.sidebar.selectbox("Select Budget", ['Any'] + cost_categories)
ranking_strategy = st.sidebar.radio("Ranking Strategy", ["Rating Only", "Rating + Votes"])

def filter_restaurants(df, cuisine, cost, city):
    filtered_df = df.copy()
    if cuisine != 'Any':
        filtered_df = filtered_df[filtered_df['Primary Cuisine'] == cuisine]
    if cost != 'Any':
        filtered_df = filtered_df[filtered_df['Cost Category'] == cost]
    if city != 'Any':
        filtered_df = filtered_df[filtered_df['City'].str.lower() == city]
    return filtered_df

def rank_restaurants(filtered_df, top_n=10, strategy="Rating + Votes"):
    if filtered_df.empty:
        return pd.DataFrame()
    if strategy == "Rating Only":
        return filtered_df.sort_values(by='Rating', ascending=False).head(top_n)

    filtered_df['Rating Norm'] = (filtered_df['Rating'] - filtered_df['Rating'].min()) / (filtered_df['Rating'].max() - filtered_df['Rating'].min())
    filtered_df['Votes Norm'] = (filtered_df['Votes'] - filtered_df['Votes'].min()) / (filtered_df['Votes'].max() - filtered_df['Votes'].min())
    filtered_df['Score'] = (filtered_df['Rating Norm'] * 0.7) + (filtered_df['Votes Norm'] * 0.3)
    return filtered_df.sort_values(by='Score', ascending=False).head(top_n)

results = filter_restaurants(df, selected_cuisine, selected_cost, selected_city)
ranked_results = rank_restaurants(results, strategy=ranking_strategy)

st.header("Top Restaurant Recommendations")

if ranked_results.empty:
    st.write("No restaurants found matching your preferences.")
else:
    for idx, row in ranked_results.iterrows():
        st.subheader(row['Restaurant Name'])
        st.write(f"City: {row['City'].title()} | Cuisine: {row['Primary Cuisine'].title()} | Budget: {row['Cost Category'].title()}")
        st.write(f"Rating: {row['Rating']} ⭐️ | Votes: {row['Votes']}")
        st.write(f"Approximate Cost for Two: {row['Average Cost for two']} {row['Currency']}")

        # Show map if coordinates are available
        if not pd.isna(row['Latitude']) and not pd.isna(row['Longitude']):
            st.map(pd.DataFrame({'lat': [row['Latitude']], 'lon': [row['Longitude']]}))

        st.write("---")

# Feedback Section
st.header("Give Us Your Feedback")

satisfaction = st.radio(
    "How satisfied are you with these recommendations?",
    ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"]
)

relevance = st.radio(
    "Were the recommendations relevant to your preferences?",
    ["Yes", "Somewhat", "No"]
)

usability = st.slider(
    "How easy was it to use the app?", 1, 5, 3
)

if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")
