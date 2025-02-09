import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd






# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="Sexual Assault & Rape Case Analytics in India",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")


st.markdown(
    "<h2 style='color:yellow; text-align:center; text-decoration:underline;'>🚔🔴 Sexual Assault Cases Dashboard (1999-2020) 🔴🚔 </h2>",
    unsafe_allow_html=True)
st.markdown(
    """
    <div style='font-size:20px; text-align:justify;'>
         🚔 Sexual Assault & Rape Case Analytics in India – An interactive dashboard to explore crime trends, distribution, and density across states. Analyze data with visualizations, filters, and download options for deeper insights.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Custom CSS for Background Colors
st.markdown("""
    <style>
    .main {
        background-color: #000000;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #808080;
    }
    </style>
""", unsafe_allow_html=True)





# # -------------------------
# Load Data
# -------------------------
# Dataset for 1999-2013
df = pd.read_csv("Cleaned State wise Sexual Assault (Detailed) 1999 - 2013.csv")
# Dataset for 2015-2020
df1 = pd.read_csv("Cleaned Summary of cases (rape) 2015-2020.csv")





# -------------------------
# 🎨 Custom Sidebar Design
# -------------------------
st.sidebar.markdown("""
    <style>
        [data-testid="stSidebar"] {
            # background-color: #4B0082; /* Dark Indigo */
            background-color: #2C2C2C; /* Light Black / Charcoal Gray */
            padding: 20px;
            border-right: 2px solid #FFD700; /* Gold Border */
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            color: #FFD700; /* Gold */
            text-align: center;
        }
        .sidebar-subtitle {
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-top: 15px;
        }
        .stSlider, .stMultiselect {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 5px;
        }
    </style>
""", unsafe_allow_html=True)





# -------------------------
# Sidebar Filters
# -------------------------
# Display the image in the sidebar
st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.markdown("<div class='sidebar-subtitle'>📅 Filter by Year</div>", unsafe_allow_html=True)

# Year Range Filter
min_year = int(min(df["YEAR"].min(), df1["Year"].min()))
max_year = int(max(df["YEAR"].max(), df1["Year"].max()))
year_range = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))





# -------------------------
# 📍 States/UT Filter
# -------------------------
st.sidebar.markdown("<div class='sidebar-subtitle'>🌍 Select States/UT</div>", unsafe_allow_html=True)

states_list = sorted(set(df["STATE/UT"].unique()).union(set(df1["State/UT"].unique())))
states_list.insert(0, "Select All")
selected_states = st.sidebar.multiselect("Select States/UT", options=states_list, default="Select All")

if "Select All" in selected_states:
    selected_states = states_list[1:]





# -------------------------
# 👤 Offender Category Filter
# -------------------------
st.sidebar.markdown("<div class='sidebar-subtitle'>👤 Offender Categories</div>", unsafe_allow_html=True)

offender_categories = ['Known_To_The_Victims', 'Parents_Close_Family_Members', 'Relatives', 'Neighbours', 'Other_Known_Persons']
offender_categories.insert(0, "Select All")
selected_categories = st.sidebar.multiselect("Select Offender Categories", options=offender_categories, default="Select All")

if "Select All" in selected_categories:
    selected_categories = offender_categories[1:]





# -------------------------
# Apply Filters
# -------------------------
df_filtered = df[(df["YEAR"] >= year_range[0]) & (df["YEAR"] <= year_range[1])]
df1_filtered = df1[(df1["Year"] >= year_range[0]) & (df1["Year"] <= year_range[1])]

if selected_states:
    df_filtered = df_filtered[df_filtered["STATE/UT"].isin(selected_states)]
    df1_filtered = df1_filtered[df1_filtered["State/UT"].isin(selected_states)]





# -------------------------
# KPIs
# -------------------------
# 📊 KPI Section Header
st.markdown("<h2 style='color:yellow; text-align:center;'>📊 Key Performance Indicators</h2>", unsafe_allow_html=True)

# --- KPI Calculations ---
total_cases_1999_2020 = df_filtered.drop(columns=["YEAR", "STATE/UT"]).select_dtypes(include=np.number).sum().sum() + df1_filtered["Cases_Reported"].sum()

# Calculate yearly totals from both datasets
yearly_total_filtered = df_filtered.groupby("YEAR").sum(numeric_only=True).sum(axis=1)
yearly_total_filtered1 = df1_filtered.groupby("Year")["Cases_Reported"].sum()

# Combine and filter
combined_yearly_series = pd.concat([yearly_total_filtered, yearly_total_filtered1.rename_axis('YEAR')]).sort_index()
combined_yearly_series = combined_yearly_series.loc[year_range[0]:year_range[1]]

# Handle highest/lowest year
if combined_yearly_series.empty:
    highest_case_year = 'No data'
    lowest_case_year = 'No data'
else:
    highest_case_year = combined_yearly_series.idxmax()
    lowest_case_year = combined_yearly_series.idxmin()

average_cases_per_state = total_cases_1999_2020 / len(selected_states) if selected_states else 0
cases_per_year = total_cases_1999_2020 / (year_range[1] - year_range[0] + 1)  # Adjusted to selected range

# State with highest average cases
state_total_filtered = df_filtered.groupby("STATE/UT").sum(numeric_only=True).sum(axis=1)
state_total_filtered1 = df1_filtered.groupby("State/UT")["Cases_Reported"].sum()

combined_state_series = pd.concat([state_total_filtered.rename_axis('State/UT'), state_total_filtered1]).groupby('State/UT').sum()

if not combined_state_series.empty:
    state_avg_cases = combined_state_series / (year_range[1] - year_range[0] + 1)
    highest_avg_state = state_avg_cases.idxmax()
    highest_avg_state_cases = int(state_avg_cases.max())
else:
    highest_avg_state = 'No data'
    highest_avg_state_cases = 0


# 🔢 Formatting numbers for better readability
def format_number(num):
    return "{:,}".format(int(num))

# --- KPI Layout ---
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)


# --- Displaying KPIs ---
kpi_data = [
    ("Total Cases (1999-2020)", format_number(total_cases_1999_2020)),
    ("Avg Cases per State/UT", format_number(average_cases_per_state)),
    ("Avg Cases per Year", format_number(cases_per_year)),
    ("Year with Highest Cases", highest_case_year),
    ("Year with Lowest Cases", lowest_case_year),
    (f"Highest Avg Cases Per Year ({highest_avg_state})", format_number(highest_avg_state_cases)),]


# --- Assigning KPIs to Columns ---
for col, (label, value) in zip([col1, col2, col3, col4, col5, col6], kpi_data):
    with col:
        st.markdown(f"""
            <div class='kpi-container'>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value'>{value}</div>
            </div>
        """, unsafe_allow_html=True)


# --- Custom Styling for KPIs ---
st.markdown("""
    <style>
        .kpi-container {
            background: linear-gradient(135deg, #FFD700, #DAA520); /* Gold Gradient */
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            box-shadow: 0px 5px 15px rgba(255, 223, 0, 0.3);
            margin-bottom: 15px;
            transition: transform 0.3s ease-in-out;
        }
        .kpi-container:hover {
            transform: scale(1.07);
        }
        .kpi-label {
            font-size: 15px;
            font-weight: bold;
            color: black;
        }
        .kpi-value {
            font-size: 30px;
            font-weight: bold;
            color: #fff;
            text-shadow: 2px 2px 5px black;
        }
    </style>
""", unsafe_allow_html=True)


st.markdown("---")





# # --------- # # 
# Visualizations
# # --------- # # 


# -------------------------
# 1. Total Reported Cases Nationwide (1999-2020)
# -------------------------

st.markdown('<h3 style="color: yellow; text-align: center;">1. Total Reported Cases Nationwide (1999-2020)</h3>', unsafe_allow_html=True)

# For 1999-2013: Group by YEAR and sum all numeric columns
yearly_total = df_filtered.groupby("YEAR").sum(numeric_only=True).sum(axis=1).reset_index()
yearly_total.columns = ["Year", "Total Cases"]

# For 2015-2020: Group by Year for Cases_Reported
yearly = df1_filtered.groupby("Year")["Cases_Reported"].sum().reset_index()
yearly.columns = ["Year", "Total Cases"]

# Ensure both datasets are concatenated properly
combined_df = pd.concat([yearly_total, yearly], ignore_index=True).sort_values(by="Year")

# Plot using plotly express
fig = px.line(combined_df, x="Year", y="Total Cases", markers=True, labels={"Total Cases": "Total Reported Cases", "Year": "Year"},)

fig.update_traces(line=dict(width=2, color='yellow'))
fig.update_layout(template='plotly_white')

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div style="font-size:16px; text-align:justify; color: white;">
    This line graph represents the total reported cases of sexual assault in India from 1999 to 2020. 
    The graph helps in understanding the overall trend and variations in reported cases over the years.
</div>
""", unsafe_allow_html=True)

st.markdown("---")





# -------------------------
# 2. Yearly Trends by Offender Category (1999-2013)
# -------------------------

st.markdown('<h3 style="color: yellow;text-align: center;">2. Yearly Trends by Offender Category (1999-2013)</h3>', unsafe_allow_html=True)

if df_filtered.empty or df_filtered.iloc[:, 1:].sum().sum() == 0:  # Check if data is empty or all values are zero
    st.markdown("<div class='summary-box'>Yearly trend data not available for the selected year range.</div>", unsafe_allow_html=True)
else:
    category_trends = df_filtered.groupby("YEAR").sum(numeric_only=True)
    
    fig2 = go.Figure()
    for column in category_trends.columns:
        fig2.add_trace(go.Scatter(x=category_trends.index, y=category_trends[column], mode='lines', name=column, stackgroup='one', hoverinfo='x+y+name'))

    fig2.update_layout(xaxis_title="Year", yaxis_title="Number of Cases", template='plotly_white', colorway=['#fdae61', '#abd9e9', '#2c7bb6', '#d7191c',
    '#1a9641'])
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
        <div class='summary-box'>
            This graph shows the yearly trends of sexual assault cases in India from 1999 to 2013 based on different offender categories. 
            The highest number of cases involve Other Known Persons, and there is a noticeable increase in total cases after 2010.
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")




# -------------------------
# 3. State-wise Comparison (Horizontal Bar Chart)
# -------------------------

st.markdown('<h3 style="color: yellow;text-align: center;">3. Top 10 States by Total Cases Reported (1999-2020)</h3>', unsafe_allow_html=True)

# For 1999-2013: Aggregate data by STATE/UT
state_total = df_filtered.groupby("STATE/UT").sum(numeric_only=True).sum(axis=1).sort_values(ascending=False).head(10)

# For 2015-2020: Aggregate Cases_Reported by State/UT
df1_grouped = df1_filtered.groupby("State/UT")["Cases_Reported"].sum().reset_index().sort_values(by="Cases_Reported", ascending=False).head(10)

fig3 = go.Figure()
fig3.add_trace(go.Bar(y=state_total.index, x=state_total.values,name="1999-2013", orientation='h'))
fig3.add_trace(go.Bar(y=df1_grouped["State/UT"], x=df1_grouped["Cases_Reported"], name="2015-2020", orientation='h'))
fig3.update_layout(xaxis_title="Total Cases Reported", yaxis_title="State/UT")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
<div style="font-size:16px; text-align:justify; color: white;">
    This bar chart displays the total number of reported cases of sexual assault in India from 1999 to 2020 across different states. Madhya Pradesh has the highest number of cases, followed by Maharashtra and Rajasthan, highlighting regional disparities.
</div>
""", unsafe_allow_html=True)

st.markdown("---")





# -------------------------
# 4. Offender Category Breakdown (Pie Chart)
# -------------------------

st.markdown('<h3 style="color: yellow;text-align: center;">4. Offender Category Distribution (1999-2013)</h3>', unsafe_allow_html=True)

available_pie_cols = [col for col in offender_categories if col in df_filtered.columns]

if df_filtered.empty or df_filtered[available_pie_cols].sum().sum() == 0:
    st.markdown("<div class='summary-box'>Offender category data not available for the selected year range.</div>", unsafe_allow_html=True)
else:
    category_totals = df_filtered[available_pie_cols].sum()
    
    fig4 = px.pie(values=category_totals.values, names=category_totals.index, color_discrete_sequence=px.colors.qualitative.Pastel, hole=0.3)
    
    fig4.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1, 0.1, 0.1], marker=dict(line=dict(color='#000000', width=2)))
    
    st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("""
    <div class='summary-box'>
    This 3D pie chart illustrates the distribution of offender categories in sexual assault cases from 1999 to 2013. The majority (50%) of offenders were known to the victims, followed by other known persons (28.7%) and neighbors (16.9%), highlighting the prevalence of assaults by familiar individuals.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")





# -------------------------
# 5. Correlation Heatmap (1999-2013)
# -------------------------

st.markdown('<h3 style="color: yellow;text-align: center;">5. Correlation Heatmap (1999-2013)</h3>', unsafe_allow_html=True)

df_corr = df_filtered if not df_filtered.empty else df

if available_pie_cols:
    # Compute correlation matrix
    corr = df_corr[available_pie_cols].corr().round(2)
    
    # Create 3D surface plot
    fig_heat_3d = go.Figure(data=[go.Surface(z=corr.values, x=corr.columns, y=corr.index, colorscale='RdBu')])
    
    fig_heat_3d.update_layout(width=900, height=700, 
                              scene=dict(xaxis_title="Offender Categories", yaxis_title="Offender Categories", zaxis_title="Correlation",),autosize=True,)

    # Display in Streamlit
    st.plotly_chart(fig_heat_3d, use_container_width=True)

    # Add summary box
    st.markdown("<div class='summary-box'>This 3D heatmap visualizes the correlation between different offender categories, helping to identify hidden patterns in the data.</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class='summary-box'>
    This 3D correlation heatmap visualizes the relationship between different offender categories from 1999 to 2013. The color gradient indicates the strength of correlations, helping to identify patterns and connections among offender types.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")





# -------------------------
# 6. Geospatial Distribution of Total Sexual Assault Cases in India (1999-2020)
# -------------------------

st.markdown('<h3 style="color: yellow;text-align: center;">6. Geospatial Distribution of Total Sexual Assault Cases in India (1999-2020)</h3>', unsafe_allow_html=True)

# Standardize state names
df["STATE/UT"] = df["STATE/UT"].str.upper().str.strip()
df1["State/UT"] = df1["State/UT"].str.upper().str.strip()
df_filtered["STATE/UT"] = df_filtered["STATE/UT"].str.upper().str.strip()
df1_filtered["State/UT"] = df1_filtered["State/UT"].str.upper().str.strip()

# Load GeoJSON
india_geo = gpd.read_file("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
india_geo["ST_NM"] = india_geo["ST_NM"].str.upper().str.strip()

# Prepare data for mapping
df_geo = df_filtered.groupby('STATE/UT').sum(numeric_only=True).sum(axis=1).reset_index(name='Cases_1999_2013')
df1_geo = df1_filtered.groupby('State/UT')['Cases_Reported'].sum().reset_index(name='Cases_2015_2020')

# Merge datasets
combined_data = pd.merge(df_geo, df1_geo, left_on='STATE/UT', right_on='State/UT', how='outer')
combined_data['Total_Cases'] = combined_data['Cases_1999_2013'].fillna(0) + combined_data['Cases_2015_2020'].fillna(0)

# Merge with GeoJSON
merged_data = india_geo.merge(combined_data, how="left", left_on="ST_NM", right_on="STATE/UT")
merged_data['Total_Cases'] = merged_data['Total_Cases'].fillna(0)

fig5 = px.choropleth(merged_data, geojson=india_geo, locations='ST_NM', featureidkey="properties.ST_NM", color='Total_Cases', color_continuous_scale="OrRd", scope="asia", labels={'Total_Cases': 'Reported Cases'})
fig5.update_geos(fitbounds="locations", visible=False)
fig5.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
st.plotly_chart(fig5, use_container_width=True)
st.markdown("""<div class='summary-box'>
This choropleth map visualizes the geographical distribution of total sexual assault cases in India from 1999 to 2020. Darker red areas indicate a higher number of reported cases, while lighter shades represent relatively fewer cases. The map helps in understanding crime trends across different states and identifying the most affected regions
</div>
""", unsafe_allow_html=True)

st.markdown("---")







# -------------------------
# Custom Styling
# -------------------------

st.markdown("<h1 style='color: white;'>📝 Feedback: Get In Touch With Sexual Assault Report!</h1>", unsafe_allow_html=True)

# Enhanced Contact Form with Stylish Design
contact_form = """
    <form action="https://formsubmit.co/sagyy2001@gmail.com" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your Name" required>
        <input type="email" name="email" placeholder="Your Email" required>
        <textarea name="message" placeholder="Your Message Here..." required></textarea>
        <button type="submit">🚀 Send Message</button>
    </form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

# Enhanced Local CSS for a Modern Look
def local_css():
    st.markdown("""
        <style>
            /* Form Container */
            form {
                background: linear-gradient(135deg, #1E1E1E, #333333);
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 5px 15px rgba(255, 215, 0, 0.4); /* Gold Glow */
                text-align: center;
            }

            /* Input Fields */
            input, textarea {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                border: none;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 16px;
                outline: none;
            }

            /* Placeholder Text Color */
            ::placeholder {
                color: #D3D3D3;
            }

            /* Submit Button */
            button {
                background: linear-gradient(135deg, #FFD700, #FF8C00); /* Gold to Orange */
                color: black;
                font-size: 18px;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.3s ease-in-out;
                box-shadow: 0px 4px 10px rgba(255, 215, 0, 0.5);
            }

            /* Hover Effect */
            button:hover {
                background: linear-gradient(135deg, #FF8C00, #FFD700);
                transform: scale(1.05);
                box-shadow: 0px 6px 15px rgba(255, 165, 0, 0.6);
            }
        </style>
    """, unsafe_allow_html=True)

# Apply the CSS Styling
local_css()


st.markdown("""# :male-student: About Section - 
This Streamlit dashboard analyzes sexual assault and rape cases in India (1999-2020) with interactive visualizations and geospatial mapping. It includes filters, trends, offender breakdowns, and state-wise comparisons for deeper insights. Optimized with custom styling and KPI metrics, it ensures an engaging user experience.
*Done By*
\n:one: Daniyal Shaikh
\n:two: Jasveer
\n:three: Sagar patil
\n:four: Akash singh rathour
\n Thanks :heartpulse:
""")



