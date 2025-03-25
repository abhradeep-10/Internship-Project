import streamlit as st
import pandas as pd

# Helper function for generic categorical dropdowns.
def dropdown_with_counts(label, df, column, default_option, include_all=False, all_option="All"):
    options = {}
    # Default option (without count)
    options[default_option] = None
    # Option for "All" if needed (show total count)
    if include_all:
        options[f"{all_option} (Datapoints in this slice: {len(df)})"] = "ALL"
    # Get unique values and their counts.
    unique_vals = sorted(df[column].dropna().unique())
    counts = df[column].value_counts().to_dict()
    for val in unique_vals:
        options[f"{val} (Datapoints in this slice: {counts.get(val, 0)})"] = val
    selected_label = st.selectbox(label, list(options.keys()))
    return options[selected_label]

# Special helper function for the country dropdown.
def dropdown_country_with_counts(df, default_option="Select Country"):
    counts = df["country"].value_counts().to_dict()
    options = {}
    options[default_option] = None
    # Get unique countries.
    unique_countries = sorted(df["country"].dropna().unique())
    # Merge Australia and New Zealand if present.
    if "Australia" in unique_countries or "New Zealand" in unique_countries:
        unique_countries = [c for c in unique_countries if c not in ["Australia", "New Zealand"]]
        merged_count = counts.get("Australia", 0) + counts.get("New Zealand", 0)
        options[f"Australia & New Zealand (Datapoints in this slice: {merged_count})"] = "Australia & New Zealand"
    for country in unique_countries:
        options[f"{country} (Datapoints in this slice: {counts.get(country, 0)})"] = country
    selected_label = st.selectbox("Select Country", list(options.keys()))
    return options[selected_label]

# Load the dataset
file_path = "All_country_data.csv"
df = pd.read_csv(file_path)

st.title("Higher Education Filtering System")

# ---------------------------
# 1. Learning Pathway Filter with counts
lp_options = {}
lp_options["Select Learning Pathway"] = None
lp_counts = df["Learning_Pathway"].value_counts().to_dict()
for lp in sorted(df["Learning_Pathway"].dropna().unique()):
    lp_options[f"{lp} (Datapoints in this slice: {lp_counts.get(lp, 0)})"] = lp
selected_lp_label = st.selectbox("Select Learning Pathway", list(lp_options.keys()))
selected_lp = lp_options[selected_lp_label]

if selected_lp is None:
    st.write("Please select a Learning Pathway to enable further filters.")
else:
    # Filter dataframe based on Learning Pathway.
    df_lp = df[df["Learning_Pathway"] == selected_lp].copy()
    st.write(f"Data points after Learning Pathway selection: {len(df_lp)}")
    
    # ---------------------------
    # 2. Country Filter with counts
    selected_country = dropdown_country_with_counts(df_lp)
    if selected_country is None:
        st.write("Please select a Country to continue.")
        st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
        st.selectbox("Select Degree", ["Select Degree"], disabled=True)
    else:
        if selected_country == "Australia & New Zealand":
            df_country = df_lp[df_lp["country"].isin(["Australia", "New Zealand"])].copy()
        else:
            df_country = df_lp[df_lp["country"] == selected_country].copy()
        st.write(f"Data points available for **{selected_country}**: {len(df_country)}")
        
        # ---------------------------
        # Country-Specific Filtering Logic
        
        # ----- Indonesia Branch -----
        if selected_country == "Indonesia":
            df_country["cost"] = pd.to_numeric(df_country["cost"], errors='coerce').fillna(0)
            # First, filter by Degree.
            selected_degree = dropdown_with_counts("Select Degree", df_country, "degree", "Select Degree", include_all=True)
            if selected_degree is None:
                st.write("Please select a Degree.")
            else:
                if selected_degree != "ALL":
                    df_filtered = df_country[df_country["degree"] == selected_degree].copy()
                else:
                    df_filtered = df_country.copy()
                st.write(f"Data points after Degree selection: {len(df_filtered)}")
                # Now apply the cost filter.
                min_cost = int(df_filtered["cost"].min())
                max_cost = int(df_filtered["cost"].max())
                if min_cost >= max_cost:
                    st.write(f"Cost is fixed at {min_cost}")
                    selected_cost_range = (min_cost, max_cost)
                else:
                    selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                df_filtered = df_filtered[(df_filtered["cost"] >= selected_cost_range[0]) & (df_filtered["cost"] <= selected_cost_range[1])]
                st.write(f"Data points after Cost Range selection: {len(df_filtered)}")
                st.dataframe(df_filtered)
        
        # ----- India Branch -----
        elif selected_country == "India":
            selected_state = dropdown_with_counts("Select State", df_country, "state", "Select State", include_all=True)
            if selected_state is None:
                st.write("Please select a State to continue.")
                st.selectbox("Select Institution Type", ["Select Institution Type"], disabled=True)
                st.selectbox("Select Degree Level", ["Select Degree Level"], disabled=True)
            else:
                if selected_state != "ALL":
                    df_india = df_country[df_country["state"] == selected_state].copy()
                else:
                    df_india = df_country.copy()
                st.write(f"Data points after State selection: {len(df_india)}")
                selected_inst = dropdown_with_counts("Select Institution Type", df_india, "institution_type", "Select Institution Type", include_all=True)
                if selected_inst is None:
                    st.write("Please select an Institution Type.")
                    st.selectbox("Select Degree Level", ["Select Degree Level"], disabled=True)
                else:
                    if selected_inst != "ALL":
                        df_india = df_india[df_india["institution_type"] == selected_inst].copy()
                    st.write(f"Data points after Institution Type selection: {len(df_india)}")
                    selected_degree_level = dropdown_with_counts("Select Degree Level", df_india, "degree_level", "Select Degree Level", include_all=True)
                    if selected_degree_level is None:
                        st.write("Please select a Degree Level.")
                    else:
                        if selected_degree_level != "ALL":
                            df_india = df_india[df_india["degree_level"] == selected_degree_level].copy()
                        st.write(f"Data points after Degree Level selection: {len(df_india)}")
                        st.dataframe(df_india)
        
        # ----- USA Branch -----
        elif selected_country == "USA":
            selected_state = dropdown_with_counts("Select State", df_country, "state", "Select State", include_all=True)
            if selected_state is None:
                st.write("Please select a State to continue.")
                st.selectbox("Select Degree", ["Select Degree"], disabled=True)
            else:
                if selected_state != "ALL":
                    df_usa = df_country[df_country["state"] == selected_state].copy()
                else:
                    df_usa = df_country.copy()
                st.write(f"Data points after State selection: {len(df_usa)}")
                selected_degree = dropdown_with_counts("Select Degree", df_usa, "degree", "Select Degree", include_all=True)
                if selected_degree is None:
                    st.write("Please select a Degree.")
                else:
                    if selected_degree != "ALL":
                        df_usa = df_usa[df_usa["degree"] == selected_degree].copy()
                    st.write(f"Data points after Degree selection: {len(df_usa)}")
                    st.dataframe(df_usa)
        
        # ----- United Kingdom Branch (using degree_level) -----
        elif selected_country == "United Kingdom":
            df_uk = df_country.copy()
            df_uk["cost_int"] = pd.to_numeric(df_uk["cost_int"], errors='coerce').fillna(0)
            selected_degree_level = dropdown_with_counts("Select Degree Level", df_uk, "degree_level", "Select Degree Level", include_all=True)
            if selected_degree_level is None:
                st.write("Please select a Degree Level.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_degree_level != "ALL":
                    df_uk = df_uk[df_uk["degree_level"] == selected_degree_level].copy()
                st.write(f"Data points after Degree Level selection: {len(df_uk)}")
                if df_uk.empty:
                    st.write("No data available for cost selection.")
                else:
                    min_cost = int(df_uk["cost_int"].min())
                    max_cost = int(df_uk["cost_int"].max())
                    if min_cost >= max_cost:
                        st.write(f"Cost is fixed at {min_cost}")
                        selected_cost_range = (min_cost, max_cost)
                    else:
                        selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                    df_uk = df_uk[(df_uk["cost_int"] >= selected_cost_range[0]) & (df_uk["cost_int"] <= selected_cost_range[1])]
                    st.write(f"Data points after Cost Range selection: {len(df_uk)}")
                    st.dataframe(df_uk)
        
        # ----- Canada Branch -----
        elif selected_country == "Canada":
            df_ca = df_country.copy()
            df_ca["cost_int"] = pd.to_numeric(df_ca["cost_int"], errors='coerce').fillna(0)
            selected_degree_level = dropdown_with_counts("Select Degree Level", df_ca, "degree_level", "Select Degree Level", include_all=True)
            if selected_degree_level is None:
                st.write("Please select a Degree Level.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_degree_level != "ALL":
                    df_ca = df_ca[df_ca["degree_level"] == selected_degree_level].copy()
                st.write(f"Data points after Degree Level selection: {len(df_ca)}")
                if df_ca.empty:
                    st.write("No data available for cost selection.")
                else:
                    min_cost = int(df_ca["cost_int"].min())
                    max_cost = int(df_ca["cost_int"].max())
                    if min_cost >= max_cost:
                        st.write(f"Cost is fixed at {min_cost}")
                        selected_cost_range = (min_cost, max_cost)
                    else:
                        selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                    df_ca = df_ca[(df_ca["cost_int"] >= selected_cost_range[0]) & (df_ca["cost_int"] <= selected_cost_range[1])]
                    st.write(f"Data points after Cost Range selection: {len(df_ca)}")
                    st.dataframe(df_ca)
        
        # ----- Hong-kong Branch -----
        elif selected_country == "Hong-kong":
            df_hk = df_country.copy()
            df_hk["cost_int"] = pd.to_numeric(df_hk["cost_int"], errors='coerce').fillna(0)
            selected_degree = dropdown_with_counts("Select Degree", df_hk, "degree", "Select Degree", include_all=True)
            if selected_degree is None:
                st.write("Please select a Degree.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_degree != "ALL":
                    df_hk = df_hk[df_hk["degree"] == selected_degree].copy()
                st.write(f"Data points after Degree selection: {len(df_hk)}")
                if df_hk.empty:
                    st.write("No data available for cost selection.")
                else:
                    min_cost = int(df_hk["cost_int"].min())
                    max_cost = int(df_hk["cost_int"].max())
                    if min_cost >= max_cost:
                        st.write(f"Cost is fixed at {min_cost}")
                        selected_cost_range = (min_cost, max_cost)
                    else:
                        selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                    df_hk = df_hk[(df_hk["cost_int"] >= selected_cost_range[0]) & (df_hk["cost_int"] <= selected_cost_range[1])]
                    st.write(f"Data points after Cost Range selection: {len(df_hk)}")
                    st.dataframe(df_hk)
        
        # ----- Vietnam Branch -----
        elif selected_country == "Vietnam":
            df_vn = df_country.copy()
            df_vn["cost_int"] = pd.to_numeric(df_vn["cost_int"], errors='coerce').fillna(0)
            selected_degree = dropdown_with_counts("Select Degree", df_vn, "degree", "Select Degree", include_all=True)
            if selected_degree is None:
                st.write("Please select a Degree.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_degree != "ALL":
                    df_vn = df_vn[df_vn["degree"] == selected_degree].copy()
                st.write(f"Data points after Degree selection: {len(df_vn)}")
                if df_vn.empty:
                    st.write("No data available for cost selection.")
                else:
                    min_cost = int(df_vn["cost_int"].min())
                    max_cost = int(df_vn["cost_int"].max())
                    if min_cost >= max_cost:
                        st.write(f"Cost is fixed at {min_cost}")
                        selected_cost_range = (min_cost, max_cost)
                    else:
                        selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                    df_vn = df_vn[(df_vn["cost_int"] >= selected_cost_range[0]) & (df_vn["cost_int"] <= selected_cost_range[1])]
                    st.write(f"Data points after Cost Range selection: {len(df_vn)}")
                    st.dataframe(df_vn)
        
        # ----- Australia & New Zealand Branch -----
        elif selected_country == "Australia & New Zealand":
            merged_df = df_country.copy()
            merged_df["cost_int"] = pd.to_numeric(merged_df["cost_int"], errors='coerce').fillna(0)
            selected_state = dropdown_with_counts("Select State", merged_df, "state", "Select State", include_all=True)
            if selected_state is None:
                st.write("Please select a State to continue.")
                st.selectbox("Select Degree Level", ["Select Degree Level"], disabled=True)
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_state != "ALL":
                    merged_df = merged_df[merged_df["state"] == selected_state].copy()
                st.write(f"Data points after State selection: {len(merged_df)}")
                selected_degree_level = dropdown_with_counts("Select Degree Level", merged_df, "degree_level", "Select Degree Level", include_all=True)
                if selected_degree_level is None:
                    st.write("Please select a Degree Level.")
                    st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
                else:
                    if selected_degree_level != "ALL":
                        merged_df = merged_df[merged_df["degree_level"] == selected_degree_level].copy()
                    st.write(f"Data points after Degree Level selection: {len(merged_df)}")
                    if merged_df.empty:
                        st.write("No data available for cost selection.")
                    else:
                        min_cost = int(merged_df["cost_int"].min())
                        max_cost = int(merged_df["cost_int"].max())
                        if min_cost >= max_cost:
                            st.write(f"Cost is fixed at {min_cost}")
                            selected_cost_range = (min_cost, max_cost)
                        else:
                            selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                        merged_df = merged_df[(merged_df["cost_int"] >= selected_cost_range[0]) & (merged_df["cost_int"] <= selected_cost_range[1])]
                        st.write(f"Data points after Cost Range selection: {len(merged_df)}")
                        st.dataframe(merged_df)
        
        # ----- Bangladesh Branch -----
        elif selected_country == "Bangladesh":
            df_bd = df_country.copy()
            df_bd["cost_int"] = pd.to_numeric(df_bd["cost_int"], errors='coerce').fillna(0)
            selected_state = dropdown_with_counts("Select State", df_bd, "state", "Select State", include_all=True)
            if selected_state is None:
                st.write("Please select a State to continue.")
                st.selectbox("Select Institution Type", ["Select Institution Type"], disabled=True)
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_state != "ALL":
                    df_bd = df_bd[df_bd["state"] == selected_state].copy()
                st.write(f"Data points after State selection: {len(df_bd)}")
                selected_inst = dropdown_with_counts("Select Institution Type", df_bd, "institution_type", "Select Institution Type", include_all=True)
                if selected_inst is None:
                    st.write("Please select an Institution Type.")
                    st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
                else:
                    if selected_inst != "ALL":
                        df_bd = df_bd[df_bd["institution_type"] == selected_inst].copy()
                    st.write(f"Data points after Institution Type selection: {len(df_bd)}")
                    if df_bd.empty:
                        st.write("No data available for cost selection.")
                    else:
                        min_cost = int(df_bd["cost_int"].min())
                        max_cost = int(df_bd["cost_int"].max())
                        if min_cost >= max_cost:
                            st.write(f"Cost is fixed at {min_cost}")
                            selected_cost_range = (min_cost, max_cost)
                        else:
                            selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                        df_bd = df_bd[(df_bd["cost_int"] >= selected_cost_range[0]) & (df_bd["cost_int"] <= selected_cost_range[1])]
                        st.write(f"Data points after Cost Range selection: {len(df_bd)}")
                        st.dataframe(df_bd)
        
        # ----- Philippines Branch -----
        elif selected_country == "Philippines":
            df_ph = df_country.copy()
            df_ph["cost_int"] = pd.to_numeric(df_ph["cost_int"], errors='coerce').fillna(0)
            selected_inst = dropdown_with_counts("Select Institution Type", df_ph, "institution_type", "Select Institution Type", include_all=True)
            if selected_inst is None:
                st.write("Please select an Institution Type.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_inst != "ALL":
                    df_ph = df_ph[df_ph["institution_type"] == selected_inst].copy()
                st.write(f"Data points after Institution Type selection: {len(df_ph)}")
                if df_ph.empty:
                    st.write("No data available for cost selection.")
                else:
                    min_cost = int(df_ph["cost_int"].min())
                    max_cost = int(df_ph["cost_int"].max())
                    if min_cost >= max_cost:
                        st.write(f"Cost is fixed at {min_cost}")
                        selected_cost_range = (min_cost, max_cost)
                    else:
                        selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                    df_ph = df_ph[(df_ph["cost_int"] >= selected_cost_range[0]) & (df_ph["cost_int"] <= selected_cost_range[1])]
                    st.write(f"Data points after Cost Range selection: {len(df_ph)}")
                    st.dataframe(df_ph)
        
        # ----- Malaysia Branch -----
        elif selected_country == "Malaysia":
            df_my = df_country.copy()
            df_my["cost_int"] = pd.to_numeric(df_my["cost_int"], errors='coerce').fillna(0)
            selected_inst = dropdown_with_counts("Select Institution Type", df_my, "institution_type", "Select Institution Type", include_all=True)
            if selected_inst is None:
                st.write("Please select an Institution Type.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_inst != "ALL":
                    df_my = df_my[df_my["institution_type"] == selected_inst].copy()
                st.write(f"Data points after Institution Type selection: {len(df_my)}")
                if df_my.empty:
                    st.write("No data available for cost selection.")
                else:
                    min_cost = int(df_my["cost_int"].min())
                    max_cost = int(df_my["cost_int"].max())
                    if min_cost >= max_cost:
                        st.write(f"Cost is fixed at {min_cost}")
                        selected_cost_range = (min_cost, max_cost)
                    else:
                        selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                    df_my = df_my[(df_my["cost_int"] >= selected_cost_range[0]) & (df_my["cost_int"] <= selected_cost_range[1])]
                    st.write(f"Data points after Cost Range selection: {len(df_my)}")
                    st.dataframe(df_my)
        
        # ----- Singapore Branch -----
        elif selected_country == "Singapore":
            df_sg = df_country.copy()
            df_sg["cost_int"] = pd.to_numeric(df_sg["cost_int"], errors='coerce').fillna(0)
            selected_inst = dropdown_with_counts("Select Institution Type", df_sg, "institution_type", "Select Institution Type", include_all=True)
            if selected_inst is None:
                st.write("Please select an Institution Type.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0, 1), disabled=True)
            else:
                if selected_inst != "ALL":
                    df_sg = df_sg[df_sg["institution_type"] == selected_inst].copy()
                st.write(f"Data points after Institution Type selection: {len(df_sg)}")
                if df_sg.empty:
                    st.write("No data available for cost selection.")
                else:
                    min_cost = int(df_sg["cost_int"].min())
                    max_cost = int(df_sg["cost_int"].max())
                    if min_cost >= max_cost:
                        st.write(f"Cost is fixed at {min_cost}")
                        selected_cost_range = (min_cost, max_cost)
                    else:
                        selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
                    df_sg = df_sg[(df_sg["cost_int"] >= selected_cost_range[0]) & (df_sg["cost_int"] <= selected_cost_range[1])]
                    st.write(f"Data points after Cost Range selection: {len(df_sg)}")
                    st.dataframe(df_sg)
