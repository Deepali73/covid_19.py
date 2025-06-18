import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("🦠 COVID-19 India Stats Dashboard (Rootnet API)")

@st.cache_data(ttl=1800)
def fetch_covid_data():
    url = "https://api.rootnet.in/covid19-in/stats/latest"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

data = fetch_covid_data()

# Extract API last refreshed date and format
last_refreshed = data['lastRefreshed']  # e.g. '2023-09-21T10:00:00.000Z'
last_refreshed_date = datetime.strptime(last_refreshed[:10], "%Y-%m-%d").strftime("%B %d, %Y")

# Month selector - user selects a month/year from pandemic period
# For demo, let's assume data from Jan 2020 to Dec 2023
months = pd.date_range("2020-01-01", "2023-12-01", freq='MS').strftime("%B %Y").tolist()
selected_month = st.selectbox("Select Month of Data (Demo filter)", months)

st.markdown(f"### Showing data for: **{selected_month}**")
st.markdown(f"*(Note: Actual data is latest available from API dated {last_refreshed_date} — month filter is demo only)*")

states_data = data['data']['regional']

# Prepare DataFrame
state_df = pd.DataFrame(states_data)
state_df = state_df.rename(columns={
    "loc": "State",
    "totalConfirmed": "Confirmed",
    "discharged": "Recovered",
    "deaths": "Deaths"
})
state_df["Active"] = state_df["Confirmed"] - (state_df["Recovered"] + state_df["Deaths"])
state_df = state_df.sort_values(by="Confirmed", ascending=False)

selected_states = st.multiselect(
    "Select states to display",
    options=state_df["State"].tolist()
)

if selected_states:
    filtered_df = state_df[state_df["State"].isin(selected_states)]

    st.subheader("COVID-19 Stats for Selected States")
    st.dataframe(filtered_df.set_index("State"))

    st.subheader("Bar Chart of COVID-19 Stats")
    st.bar_chart(filtered_df.set_index("State")[["Confirmed", "Active", "Recovered", "Deaths"]])

    st.markdown("---")

    # Dummy age group data (example)
    age_groups = {
        "0-17": 50000,
        "18-30": 200000,
        "31-45": 300000,
        "46-60": 250000,
        "61+": 150000
    }
    age_df = pd.DataFrame(list(age_groups.items()), columns=["Age Group", "Cases"])

    st.subheader("Estimated COVID-19 Cases by Age Group (Demo Data)")
    st.dataframe(age_df.set_index("Age Group"))
    st.bar_chart(age_df.set_index("Age Group")["Cases"])

    max_age_group = age_df.loc[age_df["Cases"].idxmax(), "Age Group"]
    st.info(f"🧑‍🤝‍🧑 Age group with the most cases: **{max_age_group}**")

else:
    st.info("Please select at least one state to display COVID-19 data.")
