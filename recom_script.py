import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the dataset
file_path = "india_usa_whole_data.csv"
degree_df = pd.read_csv(file_path)

# Define the reference sorted list of engineering degrees
reference_degrees = [
    "Computer Science Engineering (CSE)",
    "Electronics and Communication Engineering (ECE)",
    "Information Technology (IT)",
    "Mechanical Engineering",
    "Civil Engineering",
    "Electrical Engineering",
    "Chemical Engineering",
    "Biotechnology/Biomedical Engineering",
    "Aerospace/Aeronautical Engineering",
    "Other Specialized Fields (e.g., Industrial, Agricultural, Metallurgical Engineering)"
]

# Load the BERT model from SentenceTransformers
model = SentenceTransformer('all-MiniLM-L6-v2')

def rank_degrees():
    """
    Streamlit-based function to rank degrees based on college selection.
    The ranking uses BERT embeddings to compute similarity with a reference sorted list,
    filters out degrees with zero similarity, and further refines ordering based on degree type:
    B.Tech > B.E > Diploma.
    """
    st.title("Degree Popularity Ranking using BERT")

    # Country Selection Dropdown
    countries = degree_df["country"].unique()
    selected_country = st.selectbox("Select Country", countries)

    # Learning Pathway Dropdown
    learning_pathways = degree_df["Learning_Pathway"].unique()
    selected_learning_pathway = st.selectbox("Select Learning Pathway", learning_pathways)

    # College Selection Dropdown
    filtered_colleges = degree_df[
        (degree_df["country"] == selected_country) &
        (degree_df["Learning_Pathway"] == selected_learning_pathway)
    ]["name"].unique()
    selected_college = st.selectbox("Select College", filtered_colleges)

    if selected_college:
        # Get unique degrees offered by the selected college
        unique_degrees = degree_df[
            (degree_df["name"] == selected_college) &
            (degree_df["country"] == selected_country)
        ]["degree"].dropna().unique()

        st.write("### Unique Degrees Offered")
        st.write(unique_degrees)

        # Compute BERT embeddings for the reference degrees and the offered degrees
        ref_embeddings = model.encode(reference_degrees)
        offered_embeddings = model.encode(unique_degrees)

        # Compute cosine similarity between each offered degree and each reference degree
        similarity_matrix = cosine_similarity(offered_embeddings, ref_embeddings)

        ranking_info = []
        for i, degree in enumerate(unique_degrees):
            # Determine the best matching reference degree for the offered degree
            best_match_idx = np.argmax(similarity_matrix[i])
            best_similarity = similarity_matrix[i][best_match_idx]

            # Skip degrees with zero similarity
            if best_similarity == 0:
                continue

            # Determine degree type ranking based on keywords (case-insensitive)
            lower_degree = degree.lower()
            if "b.tech" in lower_degree:
                type_rank = 1
            elif "b.e" in lower_degree:
                type_rank = 2
            elif "diploma" in lower_degree:
                type_rank = 3
            else:
                type_rank = 4  # Other degrees ranked lower than B.Tech, B.E, or Diploma

            ranking_info.append((degree, best_match_idx, best_similarity, type_rank))

        # Sort by:
        # 1. The order of the matched reference degree (lower index is higher priority)
        # 2. The degree type ranking (B.Tech (1) > B.E (2) > Diploma (3) > others (4))
        # 3. Similarity score (higher is better)
        ranked_degrees = sorted(ranking_info, key=lambda x: (x[1], x[3], -x[2]))

        # Build a DataFrame to display the ranking
        ranked_df = pd.DataFrame(ranked_degrees, columns=["Degree", "Reference_Index", "Similarity_Score", "Type_Rank"])
        ranked_df["Matched_Reference"] = ranked_df["Reference_Index"].apply(lambda idx: reference_degrees[idx])
        ranked_df["Rank"] = range(1, len(ranked_df) + 1)
        ranked_df = ranked_df[["Rank", "Degree", "Matched_Reference", "Type_Rank", "Similarity_Score"]]

        st.write("### Ranked Degrees")
        st.dataframe(ranked_df)

# Run the Streamlit app
if __name__ == "__main__":
    rank_degrees()
