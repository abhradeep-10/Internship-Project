import streamlit as st
import pandas as pd

# Load the dataset
file_path = "All_country_data.csv"
df = pd.read_csv(file_path)

st.title("Higher Education Filtering System")

# ---------------------------
# 1. Learning Pathway Filter
lp_options = ["Select Learning Pathway"] + sorted(df["Learning_Pathway"].unique().tolist())
selected_lp = st.selectbox("Select Learning Pathway", lp_options)

if selected_lp == "Select Learning Pathway":
    st.write("Please select a Learning Pathway to enable further filters.")
else:
    # Filter dataframe based on Learning Pathway.
    df_lp = df[df["Learning_Pathway"] == selected_lp].copy()
    st.write(f"Data points after Learning Pathway selection: {len(df_lp)}")
    
    # ---------------------------
    # 2. Country Filter
    # Merge Australia and New Zealand into one option if present.
    country_list = df_lp["country"].unique().tolist()
    if "Australia" in country_list or "New Zealand" in country_list:
        country_list = [c for c in country_list if c not in ["Australia", "New Zealand"]]
        country_list.append("Australia & New Zealand")
    country_options = ["Select Country"] + sorted(country_list)
    
    selected_country = st.selectbox("Select Country", country_options)
    if selected_country == "Select Country":
        st.write("Please select a Country to continue.")
        st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
        st.selectbox("Select Degree", ["Select Degree"], disabled=True)
    else:
        # Filter by selected country. If merged option, include both.
        if selected_country == "Australia & New Zealand":
            df_country = df_lp[df_lp["country"].isin(["Australia", "New Zealand"])].copy()
        else:
            df_country = df_lp[df_lp["country"] == selected_country].copy()
        st.write(f"Data points available for **{selected_country}**: {len(df_country)}")
        
        # ---------------------------
        # Country-Specific Filtering Logic
        
        # ----- Indonesia Branch -----
        if selected_country == "Indonesia":
            df_country["cost"] = pd.to_numeric(df_country["cost"], errors='coerce')
            df_country = df_country.fillna(0)
            min_cost = int(df_country["cost"].min())
            max_cost = int(df_country["cost"].max())
            if min_cost >= max_cost:
                st.write(f"Cost is fixed at {min_cost}")
                selected_cost_range = (min_cost, max_cost)
            else:
                selected_cost_range = st.slider("Select Cost Range", min_value=min_cost, max_value=max_cost, value=(min_cost, max_cost))
            df_filtered = df_country[(df_country["cost"] >= selected_cost_range[0]) & (df_country["cost"] <= selected_cost_range[1])]
            st.write(f"Data points after Cost Range selection: {len(df_filtered)}")
            
            degree_options = ["Select Degree", "All"] + sorted(df_filtered["degree"].dropna().unique().tolist())
            selected_degree = st.selectbox("Select Degree", degree_options)
            if selected_degree == "Select Degree":
                st.write("Please select a Degree.")
            else:
                if selected_degree != "All":
                    df_filtered = df_filtered[df_filtered["degree"] == selected_degree]
                st.write(f"Data points after Degree selection: {len(df_filtered)}")
                st.dataframe(df_filtered)
        
        # ----- India Branch -----
        elif selected_country == "India":
            df_india = df_country.copy()
            state_options = ["Select State", "All"] + sorted(df_india["state"].dropna().unique().tolist())
            selected_state = st.selectbox("Select State", state_options)
            if selected_state == "Select State":
                st.write("Please select a State to continue.")
                st.selectbox("Select Institution Type", ["Select Institution Type"], disabled=True)
                st.selectbox("Select Degree Level", ["Select Degree Level"], disabled=True)
            else:
                if selected_state != "All":
                    df_india = df_india[df_india["state"] == selected_state]
                st.write(f"Data points after State selection: {len(df_india)}")
                
                inst_options = ["Select Institution Type", "All"] + sorted(df_india["institution_type"].dropna().unique().tolist())
                selected_inst = st.selectbox("Select Institution Type", inst_options)
                if selected_inst == "Select Institution Type":
                    st.write("Please select an Institution Type.")
                    st.selectbox("Select Degree Level", ["Select Degree Level"], disabled=True)
                else:
                    if selected_inst != "All":
                        df_india = df_india[df_india["institution_type"] == selected_inst]
                    st.write(f"Data points after Institution Type selection: {len(df_india)}")
                    
                    degree_options = ["Select Degree Level", "All"] + sorted(df_india["degree_level"].dropna().unique().tolist())
                    selected_degree_level = st.selectbox("Select Degree Level", degree_options)
                    if selected_degree_level == "Select Degree Level":
                        st.write("Please select a Degree Level.")
                    else:
                        if selected_degree_level != "All":
                            df_india = df_india[df_india["degree_level"] == selected_degree_level]
                        st.write(f"Data points after Degree Level selection: {len(df_india)}")
                        st.dataframe(df_india)
        
        # ----- USA Branch -----
        elif selected_country == "USA":
            df_usa = df_country.copy()
            state_options = ["Select State", "All"] + sorted(df_usa["state"].dropna().unique().tolist())
            selected_state = st.selectbox("Select State", state_options)
            if selected_state == "Select State":
                st.write("Please select a State to continue.")
                st.selectbox("Select Degree", ["Select Degree"], disabled=True)
            else:
                if selected_state != "All":
                    df_usa = df_usa[df_usa["state"] == selected_state]
                st.write(f"Data points after State selection: {len(df_usa)}")
                
                degree_options = ["Select Degree", "All"] + sorted(df_usa["degree"].dropna().unique().tolist())
                selected_degree = st.selectbox("Select Degree", degree_options)
                if selected_degree == "Select Degree":
                    st.write("Please select a Degree.")
                else:
                    if selected_degree != "All":
                        df_usa = df_usa[df_usa["degree"] == selected_degree]
                    st.write(f"Data points after Degree selection: {len(df_usa)}")
                    st.dataframe(df_usa)
        
        # ----- United Kingdom Branch -----
        elif selected_country == "United Kingdom":
            df_uk = df_country.copy()
            df_uk["cost_int"] = pd.to_numeric(df_uk["cost_int"], errors='coerce')
            df_uk = df_uk.fillna(0)
            
            degree_options = ["Select Degree", "All"] + sorted(df_uk["degree"].dropna().unique().tolist())
            selected_degree = st.selectbox("Select Degree", degree_options)
            if selected_degree == "Select Degree":
                st.write("Please select a Degree.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_degree != "All":
                    df_uk = df_uk[df_uk["degree"] == selected_degree]
                st.write(f"Data points after Degree selection: {len(df_uk)}")
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
            df_ca["cost_int"] = pd.to_numeric(df_ca["cost_int"], errors='coerce')
            df_ca = df_ca.fillna(0)
            
            degree_level_options = ["Select Degree Level", "All"] + sorted(df_ca["degree_level"].dropna().unique().tolist())
            selected_degree_level = st.selectbox("Select Degree Level", degree_level_options)
            if selected_degree_level == "Select Degree Level":
                st.write("Please select a Degree Level.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_degree_level != "All":
                    df_ca = df_ca[df_ca["degree_level"] == selected_degree_level]
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
        elif selected_country == "Hong Kong":
            df_hk = df_country.copy()
            df_hk["cost_int"] = pd.to_numeric(df_hk["cost_int"], errors='coerce')
            df_hk = df_hk.fillna(0)
            degree_options = ["Select Degree", "All"] + sorted(df_hk["degree"].dropna().unique().tolist())
            selected_degree = st.selectbox("Select Degree", degree_options)
            if selected_degree == "Select Degree":
                st.write("Please select a Degree.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_degree != "All":
                    df_hk = df_hk[df_hk["degree"] == selected_degree]
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
            df_vn["cost_int"] = pd.to_numeric(df_vn["cost_int"], errors='coerce')
            df_vn = df_vn.fillna(0)
            degree_options = ["Select Degree", "All"] + sorted(df_vn["degree"].dropna().unique().tolist())
            selected_degree = st.selectbox("Select Degree", degree_options)
            if selected_degree == "Select Degree":
                st.write("Please select a Degree.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_degree != "All":
                    df_vn = df_vn[df_vn["degree"] == selected_degree]
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
            merged_df["cost_int"] = pd.to_numeric(merged_df["cost_int"], errors='coerce')
            merged_df = merged_df.fillna(0)
            # (No duplicate printing here as the overall count was printed earlier.)
            state_options = ["Select State", "All"] + sorted(merged_df["state"].dropna().unique().tolist())
            selected_state = st.selectbox("Select State", state_options)
            if selected_state == "Select State":
                st.write("Please select a State to continue.")
                st.selectbox("Select Degree Level", ["Select Degree Level"], disabled=True)
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_state != "All":
                    merged_df = merged_df[merged_df["state"] == selected_state]
                st.write(f"Data points after State selection: {len(merged_df)}")
                degree_level_options = ["Select Degree Level", "All"] + sorted(merged_df["degree_level"].dropna().unique().tolist())
                selected_degree_level = st.selectbox("Select Degree Level", degree_level_options)
                if selected_degree_level == "Select Degree Level":
                    st.write("Please select a Degree Level.")
                    st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
                else:
                    if selected_degree_level != "All":
                        merged_df = merged_df[merged_df["degree_level"] == selected_degree_level]
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
            df_bd["cost_int"] = pd.to_numeric(df_bd["cost_int"], errors='coerce')
            df_bd = df_bd.fillna(0)
            state_options = ["Select State", "All"] + sorted(df_bd["state"].dropna().unique().tolist())
            selected_state = st.selectbox("Select State", state_options)
            if selected_state == "Select State":
                st.write("Please select a State to continue.")
                st.selectbox("Select Institution Type", ["Select Institution Type"], disabled=True)
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_state != "All":
                    df_bd = df_bd[df_bd["state"] == selected_state]
                st.write(f"Data points after State selection: {len(df_bd)}")
                inst_options = ["Select Institution Type", "All"] + sorted(df_bd["institution_type"].dropna().unique().tolist())
                selected_inst = st.selectbox("Select Institution Type", inst_options)
                if selected_inst == "Select Institution Type":
                    st.write("Please select an Institution Type.")
                    st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
                else:
                    if selected_inst != "All":
                        df_bd = df_bd[df_bd["institution_type"] == selected_inst]
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
            df_ph["cost_int"] = pd.to_numeric(df_ph["cost_int"], errors='coerce')
            df_ph = df_ph.fillna(0)
            inst_options = ["Select Institution Type", "All"] + sorted(df_ph["institution_type"].dropna().unique().tolist())
            selected_inst = st.selectbox("Select Institution Type", inst_options)
            if selected_inst == "Select Institution Type":
                st.write("Please select an Institution Type.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_inst != "All":
                    df_ph = df_ph[df_ph["institution_type"] == selected_inst]
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
            df_my["cost_int"] = pd.to_numeric(df_my["cost_int"], errors='coerce')
            df_my = df_my.fillna(0)
            inst_options = ["Select Institution Type", "All"] + sorted(df_my["institution_type"].dropna().unique().tolist())
            selected_inst = st.selectbox("Select Institution Type", inst_options)
            if selected_inst == "Select Institution Type":
                st.write("Please select an Institution Type.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_inst != "All":
                    df_my = df_my[df_my["institution_type"] == selected_inst]
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
            df_sg["cost_int"] = pd.to_numeric(df_sg["cost_int"], errors='coerce')
            df_sg = df_sg.fillna(0)
            inst_options = ["Select Institution Type", "All"] + sorted(df_sg["institution_type"].dropna().unique().tolist())
            selected_inst = st.selectbox("Select Institution Type", inst_options)
            if selected_inst == "Select Institution Type":
                st.write("Please select an Institution Type.")
                st.slider("Select Cost Range", min_value=0, max_value=1, value=(0,1), disabled=True)
            else:
                if selected_inst != "All":
                    df_sg = df_sg[df_sg["institution_type"] == selected_inst]
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
