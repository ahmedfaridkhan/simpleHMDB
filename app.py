import streamlit as st
import pandas as pd

# Load the data
data = pd.read_csv('Raw Data.csv')

# Convert Score to numeric by removing '%' and converting to float
data['Score'] = data['Score'].str.replace('%', '').astype(float)
data['5 Star Cut Point'] = data['5 Star Cut Point'].str.replace('%', '').astype(float)
data['4 Star Cut Point'] = data['4 Star Cut Point'].str.replace('%', '').astype(float)
data['3 Star Cut Point'] = data['3 Star Cut Point'].str.replace('%', '').astype(float)
data['2 Star Cut Point'] = data['2 Star Cut Point'].str.replace('%', '').astype(float)

# Constants
BASE_REVENUE = 1341920160
BASE_STARS = 4.071428571429
BASE_WEIGHT_SUM = 69
NON_CHANGEABLE_MEASURES_SCORE = 295
REVENUE_INCREASE_RATE = 0.075  # 0.075% revenue increase per 0.01 increase in stars

# Title and description
st.title("Medicare Advantage What-If Tool")
st.markdown("This tool allows you to simulate the impact of increasing scores for certain measures on the overall Stars Rating and revenue.")

# Display data
st.subheader("Current Measures and Scores")
st.write(data[['Measure', 'Score', 'Measure Star', 'Weight']])

# Initialize a new column for "What-If Score" based on user input
data['What-If Score'] = data['Score']

# Create sliders for each measure to allow the user to adjust the scores
st.subheader("Adjust Scores for Measures")

for index, row in data.iterrows():
    new_score = st.slider(f"Adjust Score for {row['Measure']}", min_value=row['Score'], max_value=row['5 Star Cut Point'], value=row['Score'], step=1.0)
    data.at[index, 'What-If Score'] = new_score

# Calculate What-If Stars based on updated scores and cut points
def calculate_stars(row):
    if row['What-If Score'] >= row['5 Star Cut Point']:
        return 5
    elif row['What-If Score'] >= row['4 Star Cut Point']:
        return 4
    elif row['What-If Score'] >= row['3 Star Cut Point']:
        return 3
    elif row['What-If Score'] >= row['2 Star Cut Point']:
        return 2
    else:
        return 1

data['What-If Stars'] = data.apply(calculate_stars, axis=1)

# Calculate new overall Stars Rating
total_weight = BASE_WEIGHT_SUM + data['Weight'].sum()
weighted_stars = NON_CHANGEABLE_MEASURES_SCORE + (data['What-If Stars'] * data['Weight']).sum()
new_stars_rating = weighted_stars / total_weight

# Calculate the change in revenue based on the difference in Stars Rating
stars_increase = new_stars_rating - BASE_STARS

# Only calculate revenue increase if there is an actual change
if abs(stars_increase) > 1e-20:  # 1e-6 is a small threshold to handle floating-point precision
    revenue_increase_percentage = stars_increase * 100 * REVENUE_INCREASE_RATE
    revenue_impact = BASE_REVENUE * (revenue_increase_percentage / 100)
else:
    revenue_impact = 0.0

# Calculate the new revenue (baseline + impact)
new_revenue = BASE_REVENUE + revenue_impact

# Display results
st.subheader("Results")
st.write(f"2023 Stars Rating: {BASE_STARS:.2f}")
st.write(f"What-If Stars Rating: {new_stars_rating:.2f}")
st.write(f"Revenue Impact: ${revenue_impact:,.2f}")

# Display table for What-If Scores and Stars
st.subheader("What-If Scenario")
st.write(data[['Measure', 'Score', 'What-If Score', 'Measure Star', 'What-If Stars']])