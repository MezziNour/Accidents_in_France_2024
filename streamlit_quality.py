import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Road Safety Data Quality Dashboard",
    layout="wide"
)


# Load data
@st.cache_data
def load_data():
    caract = pd.read_csv("caract-2024.csv", sep=";", dtype=str)
    lieux = pd.read_csv("lieux-2024.csv", sep=";", dtype=str)
    vehicules = pd.read_csv("vehicules-2024.csv", sep=";", dtype=str)
    usagers = pd.read_csv("usagers-2024.csv", sep=";", dtype=str)
    return caract, lieux, vehicules, usagers


caract, lieux, vehicules, usagers = load_data()


# Cleaning helpers
def to_float_comma(series):
    return pd.to_numeric(
        series.astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )


def missing_report(df):
    return pd.DataFrame({
        "Column": df.columns,
        "Missing count": df.isna().sum().values,
        "Missing (%)": (df.isna().mean().values * 100).round(2),
        "Unique values": df.nunique(dropna=True).values
    }).sort_values("Missing (%)", ascending=False)


def count_invalid_codes(df, columns, invalid_values=["-1", "0"]):
    rows = []
    for col in columns:
        if col in df.columns:
            for val in invalid_values:
                count = (df[col].astype(str) == val).sum()
                rows.append({
                    "Column": col,
                    "Code": val,
                    "Count": count,
                    "Percentage": round(count / len(df) * 100, 2)
                })
    return pd.DataFrame(rows)



# Mappings based on BAAC documentation
lum_map = {
    "1": "Daylight",
    "2": "Twilight or dawn",
    "3": "Night without public lighting",
    "4": "Night with public lighting off",
    "5": "Night with public lighting on"
}

agg_map = {
    "1": "Outside urban area",
    "2": "Urban area"
}

atm_map = {
    "-1": "Unknown",
    "1": "Normal",
    "2": "Light rain",
    "3": "Heavy rain",
    "4": "Snow or hail",
    "5": "Fog or smoke",
    "6": "Strong wind or storm",
    "7": "Dazzling weather",
    "8": "Cloudy weather",
    "9": "Other"
}

col_map = {
    "-1": "Unknown",
    "1": "Two vehicles - frontal",
    "2": "Two vehicles - rear-end",
    "3": "Two vehicles - side collision",
    "4": "Three or more vehicles - chain collision",
    "5": "Three or more vehicles - multiple collisions",
    "6": "Other collision",
    "7": "No collision"
}

catr_map = {
    "1": "Motorway",
    "2": "National road",
    "3": "Departmental road",
    "4": "Municipal road",
    "5": "Outside public network",
    "6": "Public parking area",
    "7": "Metropolitan road",
    "9": "Other"
}

surf_map = {
    "-1": "Unknown",
    "1": "Normal",
    "2": "Wet",
    "3": "Puddles",
    "4": "Flooded",
    "5": "Snowy",
    "6": "Muddy",
    "7": "Icy",
    "8": "Oil or grease",
    "9": "Other"
}

catv_map = {
    "0": "Undeterminable",
    "1": "Bicycle",
    "2": "Moped < 50cm3",
    "7": "Car",
    "10": "Utility vehicle",
    "13": "Heavy goods vehicle 3.5T-7.5T",
    "14": "Heavy goods vehicle > 7.5T",
    "30": "Scooter < 50cm3",
    "31": "Motorcycle 50-125cm3",
    "32": "Scooter 50-125cm3",
    "33": "Motorcycle > 125cm3",
    "34": "Scooter > 125cm3",
    "37": "Bus",
    "38": "Coach",
    "39": "Train",
    "40": "Tramway",
    "50": "Motorized personal mobility device",
    "60": "Non-motorized personal mobility device",
    "80": "Electric bike",
    "99": "Other vehicle"
}

motor_map = {
    "-1": "Unknown",
    "0": "Unknown",
    "1": "Hydrocarbon",
    "2": "Hybrid electric",
    "3": "Electric",
    "4": "Hydrogen",
    "5": "Human-powered",
    "6": "Other"
}

catu_map = {
    "1": "Driver",
    "2": "Passenger",
    "3": "Pedestrian"
}

grav_map = {
    "1": "Uninjured",
    "2": "Killed",
    "3": "Hospitalized injured",
    "4": "Slightly injured"
}

sexe_map = {
    "-1": "Unknown",
    "1": "Male",
    "2": "Female"
}

trajet_map = {
    "-1": "Unknown",
    "0": "Unknown",
    "1": "Home-work",
    "2": "Home-school",
    "3": "Shopping",
    "4": "Professional use",
    "5": "Leisure",
    "9": "Other"
}


# Apply mappings
caract["lum_label"] = caract["lum"].map(lum_map).fillna("Other / unmapped")
caract["agg_label"] = caract["agg"].map(agg_map).fillna("Other / unmapped")
caract["atm_label"] = caract["atm"].map(atm_map).fillna("Other / unmapped")
caract["col_label"] = caract["col"].map(col_map).fillna("Other / unmapped")

caract["lat_float"] = to_float_comma(caract["lat"])
caract["long_float"] = to_float_comma(caract["long"])

lieux["catr_label"] = lieux["catr"].map(catr_map).fillna("Other / unmapped")
lieux["surf_label"] = lieux["surf"].map(surf_map).fillna("Other / unmapped")
lieux["vma_num"] = pd.to_numeric(lieux["vma"], errors="coerce")

vehicules["catv_label"] = vehicules["catv"].map(catv_map).fillna("Other / unmapped")
vehicules["motor_label"] = vehicules["motor"].map(motor_map).fillna("Other / unmapped")

usagers["catu_label"] = usagers["catu"].map(catu_map).fillna("Other / unmapped")
usagers["grav_label"] = usagers["grav"].map(grav_map).fillna("Other / unmapped")
usagers["sexe_label"] = usagers["sexe"].map(sexe_map).fillna("Other / unmapped")
usagers["trajet_label"] = usagers["trajet"].map(trajet_map).fillna("Other / unmapped")
usagers["age"] = 2024 - pd.to_numeric(usagers["an_nais"], errors="coerce")


# Sidebar
st.sidebar.title("Dashboard filters")

dataset_choice = st.sidebar.selectbox(
    "Select dataset",
    ["Characteristics", "Locations", "Vehicles", "Users"]
)


# Title
st.title("French Road Safety 2024 - Data Quality Dashboard")

st.markdown("""
This dashboard summarizes the main data quality issues detected during profiling:
missing values, coded unknown values, invalid ranges, and categorical mappings.
""")


# Global KPIs
st.header("Global KPIs")

col1, col2, col3, col4 = st.columns(4)

total_accidents = caract["Num_Acc"].nunique()
total_locations = len(lieux)
total_vehicles = len(vehicules)
total_users = len(usagers)

col1.metric("Accidents", f"{total_accidents:,}")
col2.metric("Location rows", f"{total_locations:,}")
col3.metric("Vehicles", f"{total_vehicles:,}")
col4.metric("Users", f"{total_users:,}")

col5, col6, col7, col8 = st.columns(4)

invalid_lat = caract["lat_float"].isna().sum()
invalid_long = caract["long_float"].isna().sum()
unrealistic_vma = (lieux["vma_num"] > 130).sum()
missing_age = usagers["age"].isna().sum()

col5.metric("Invalid latitude", invalid_lat)
col6.metric("Invalid longitude", invalid_long)
col7.metric("Unrealistic speed limits", unrealistic_vma)
col8.metric("Missing age", missing_age)


# Dataset-specific section
st.header(f"{dataset_choice} - Data Quality Analysis")

if dataset_choice == "Characteristics":
    df = caract

    st.subheader("Missing values")
    st.dataframe(missing_report(df), use_container_width=True)

    st.subheader("Mapped categorical variables")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            df["lum_label"].value_counts().reset_index(),
            x="count",
            y="lum_label",
            orientation="h",
            title="Accidents by lighting condition",
            labels={"count": "Count", "lum_label": "Lighting condition"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            df["atm_label"].value_counts().reset_index(),
            x="count",
            y="atm_label",
            orientation="h",
            title="Accidents by atmospheric condition",
            labels={"count": "Count", "atm_label": "Atmospheric condition"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Geographic range checks")
    geo_checks = pd.DataFrame({
        "Check": [
            "Latitude < -90 or > 90",
            "Longitude < -180 or > 180",
            "Missing latitude after conversion",
            "Missing longitude after conversion"
        ],
        "Count": [
            ((df["lat_float"] < -90) | (df["lat_float"] > 90)).sum(),
            ((df["long_float"] < -180) | (df["long_float"] > 180)).sum(),
            df["lat_float"].isna().sum(),
            df["long_float"].isna().sum()
        ]
    })
    st.dataframe(geo_checks, use_container_width=True)

elif dataset_choice == "Locations":
    df = lieux

    st.subheader("Missing values")
    st.dataframe(missing_report(df), use_container_width=True)

    st.subheader("Critical missing columns")
    critical_missing = missing_report(df)
    critical_missing = critical_missing[critical_missing["Missing (%)"] > 10]
    st.dataframe(critical_missing, use_container_width=True)

    st.subheader("Road context after mapping")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            df["catr_label"].value_counts().reset_index(),
            x="count",
            y="catr_label",
            orientation="h",
            title="Accidents by road category",
            labels={"count": "Count", "catr_label": "Road category"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            df["surf_label"].value_counts().reset_index(),
            x="count",
            y="surf_label",
            orientation="h",
            title="Accidents by road surface condition",
            labels={"count": "Count", "surf_label": "Surface condition"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speed limit validity")
    speed_issues = pd.DataFrame({
        "Issue": [
            "Unknown speed limit (-1)",
            "Zero speed limit",
            "Speed limit above 130 km/h"
        ],
        "Count": [
            (df["vma"] == "-1").sum(),
            (df["vma"] == "0").sum(),
            (df["vma_num"] > 130).sum()
        ]
    })
    st.dataframe(speed_issues, use_container_width=True)

    fig = px.histogram(
        df[df["vma_num"].between(0, 130)],
        x="vma_num",
        nbins=30,
        title="Distribution of valid speed limits",
        labels={"vma_num": "Speed limit"}
    )
    st.plotly_chart(fig, use_container_width=True)

elif dataset_choice == "Vehicles":
    df = vehicules

    st.subheader("Missing values")
    st.dataframe(missing_report(df), use_container_width=True)

    st.subheader("Vehicle mappings")

    c1, c2 = st.columns(2)

    with c1:
        top_vehicles = df["catv_label"].value_counts().head(15).reset_index()
        fig = px.bar(
            top_vehicles,
            x="count",
            y="catv_label",
            orientation="h",
            title="Top vehicle categories",
            labels={"count": "Count", "catv_label": "Vehicle category"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            df["motor_label"].value_counts().reset_index(),
            x="count",
            y="motor_label",
            orientation="h",
            title="Vehicles by motorization",
            labels={"count": "Count", "motor_label": "Motorization"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Unknown or not applicable coded values")
    invalid_vehicle_cols = ["senc", "catv", "obs", "obsm", "choc", "manv", "motor"]
    st.dataframe(
        count_invalid_codes(df, invalid_vehicle_cols),
        use_container_width=True
    )

elif dataset_choice == "Users":
    df = usagers

    st.subheader("Missing values")
    st.dataframe(missing_report(df), use_container_width=True)

    st.subheader("User and severity mappings")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            df["grav_label"].value_counts().reset_index(),
            x="count",
            y="grav_label",
            orientation="h",
            title="Users by injury severity",
            labels={"count": "Count", "grav_label": "Severity"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            df["catu_label"].value_counts().reset_index(),
            x="count",
            y="catu_label",
            orientation="h",
            title="Users by category",
            labels={"count": "Count", "catu_label": "User category"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Age validity")

    age_checks = pd.DataFrame({
        "Issue": [
            "Missing age",
            "Age below 0",
            "Age above 100"
        ],
        "Count": [
            df["age"].isna().sum(),
            (df["age"] < 0).sum(),
            (df["age"] > 100).sum()
        ]
    })
    st.dataframe(age_checks, use_container_width=True)

    fig = px.histogram(
        df[df["age"].between(0, 100)],
        x="age",
        nbins=50,
        title="Age distribution of users",
        labels={"age": "Age"}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Unknown coded values")
    invalid_user_cols = [
        "sexe", "trajet", "secu1", "secu2", "secu3",
        "locp", "actp", "etatp"
    ]
    st.dataframe(
        count_invalid_codes(df, invalid_user_cols),
        use_container_width=True
    )


# Joined analytical view
st.header("Joined analytical view")

merged = (
    usagers
    .merge(vehicules[["Num_Acc", "id_vehicule", "catv_label", "motor_label"]],
           on=["Num_Acc", "id_vehicule"],
           how="left")
    .merge(caract[["Num_Acc", "lum_label", "atm_label", "agg_label"]],
           on="Num_Acc",
           how="left")
)

st.subheader("Severity by user category")

severity_category = (
    merged.groupby(["catu_label", "grav_label"])
    .size()
    .reset_index(name="count")
)

fig = px.bar(
    severity_category,
    x="catu_label",
    y="count",
    color="grav_label",
    barmode="group",
    title="Injury severity by user category",
    labels={
        "catu_label": "User category",
        "grav_label": "Severity",
        "count": "Count"
    }
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Severity by vehicle category")

severity_vehicle = (
    merged.groupby(["catv_label", "grav_label"])
    .size()
    .reset_index(name="count")
)

top_catv = merged["catv_label"].value_counts().head(10).index
severity_vehicle = severity_vehicle[severity_vehicle["catv_label"].isin(top_catv)]

fig = px.bar(
    severity_vehicle,
    x="count",
    y="catv_label",
    color="grav_label",
    orientation="h",
    title="Injury severity by top vehicle categories",
    labels={
        "catv_label": "Vehicle category",
        "grav_label": "Severity",
        "count": "Count"
    }
)
st.plotly_chart(fig, use_container_width=True)
