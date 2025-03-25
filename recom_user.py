import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the datasets
file_path_degrees = "india_usa_whole_data.csv"
file_path_skills = "skill_score_data.csv"
degree_df = pd.read_csv(file_path_degrees)
skill_score_df = pd.read_csv(file_path_skills)

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

# Load the BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_similarity(degrees, reference_degrees):
    ref_embeddings = model.encode(reference_degrees)
    offered_embeddings = model.encode(degrees)
    similarity_matrix = cosine_similarity(offered_embeddings, ref_embeddings)
    return similarity_matrix

# Define the ideal skill vector
ideal_vector = np.array([1.0, 0.0, 0.0, 0.52381, 0.047619, 0.285714])

# Compute cosine similarity for each user
user_scores = skill_score_df[["COGNITIVE", "INTERACTIVE", "EMOTIVE", "ADAPTIVE", "CREATIVE", "MOTIVE"]].values
ideal_vector = ideal_vector.reshape(1, -1)  # Reshape for compatibility
cosine_similarities = cosine_similarity(user_scores, ideal_vector).flatten()
skill_score_df["Cosine_Similarity"] = cosine_similarities

# Create bins for user similarity scores
bins = np.linspace(min(cosine_similarities), max(cosine_similarities), num=5)
skill_score_df["Similarity_Bin"] = np.digitize(skill_score_df["Cosine_Similarity"], bins)

# Rank users by similarity (higher is better)
skill_score_df = skill_score_df.sort_values(by="Cosine_Similarity", ascending=False)

def rank_degrees():
    """
    Streamlit app to rank degrees and recommend courses based on user skill scores.
    """
    st.title("Degree Popularity Ranking & Course Recommendations")
    
    # Country selection
    countries = degree_df["country"].unique()
    selected_country = st.selectbox("Select Country", countries)

    # Learning Pathway selection
    learning_pathways = degree_df["Learning_Pathway"].unique()
    selected_learning_pathway = st.selectbox("Select Learning Pathway", learning_pathways)

    # College selection
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
        
        # Compute similarity between offered degrees and reference degrees
        similarity_matrix = compute_similarity(unique_degrees, reference_degrees)

        ranking_info = []
        for i, degree in enumerate(unique_degrees):
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

        # Sort degrees by reference match, type rank, and similarity score
        ranked_degrees = sorted(ranking_info, key=lambda x: (x[1], x[3], -x[2]))

        # Build a DataFrame to display the ranking
        ranked_df = pd.DataFrame(ranked_degrees, columns=["Degree", "Reference_Index", "Similarity_Score", "Type_Rank"])
        ranked_df["Matched_Reference"] = ranked_df["Reference_Index"].apply(lambda idx: reference_degrees[idx])
        ranked_df["Rank"] = range(1, len(ranked_df) + 1)
        ranked_df = ranked_df[["Rank", "Degree", "Matched_Reference", "Type_Rank", "Similarity_Score"]]

        st.write("### Ranked Degrees")
        st.dataframe(ranked_df)
        
        # User selection
        user_ids = skill_score_df["user_id"].unique()
        selected_user = st.selectbox("Select User ID", user_ids)
        
        if selected_user:
            user_row = skill_score_df[skill_score_df["user_id"] == selected_user].iloc[0]
            st.write(f"### User ID: {selected_user}")
            st.write(f"Cosine Similarity to Ideal: {user_row['Cosine_Similarity']:.4f}")
            
            # Personalized course recommendations based on similarity bin
            similarity_bin = int(user_row["Similarity_Bin"])
            num_courses = 3
            max_courses = len(ranked_df)

            recommendation_mapping = {i: list(range(max(0, max_courses - (i + 1) * num_courses), max_courses - i * num_courses)) for i in range(5)}
            
            course_indices = recommendation_mapping.get(similarity_bin, [0, 1, 2])
            print(similarity_bin)
            print(course_indices)
            print(recommendation_mapping) 
            recommended_courses = [ranked_df["Degree"].iloc[i] for i in course_indices if 0 <= i < len(ranked_df)]
            while len(recommended_courses) < num_courses and len(recommended_courses) < max_courses:
                recommended_courses.append(ranked_df["Degree"].iloc[len(recommended_courses)])
            
            st.write("### Recommended Courses")
            st.write(recommended_courses if recommended_courses else "No courses available")

if __name__ == "__main__":
    rank_degrees()