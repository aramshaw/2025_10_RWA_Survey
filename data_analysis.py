from src.data_processing import load_data, load_column_mapping, apply_data_types
from src.visualization import (
    create_bar_chart,
    create_comparison_chart,
    create_reasons_summary_chart,
)

# Define the file path.
# Make sure the Excel file is in the same directory as this script,
# or provide the full path to the file.
file_path = "2025 End of Season Rower Survey - Responses (AR).xlsx"
mapping_file_path = "column_mapping.xlsx"


if __name__ == "__main__":
    # Load the data
    survey_data = load_data(file_path)

    # Load the column mapping dataframe
    mapping_df = load_column_mapping(mapping_file_path)

    # If data and mapping are loaded successfully, process the data
    if survey_data is not None and mapping_df is not None:
        # Create a dictionary for renaming
        column_mapping = dict(zip(mapping_df["old_name"], mapping_df["new_name"]))

        # Rename the columns
        survey_data.rename(columns=column_mapping, inplace=True)
        print("\nColumns renamed.")

        # Apply the recommended data types to the entire dataset
        survey_data = apply_data_types(survey_data, mapping_df)

        # Define the age categories for Masters rowers
        masters_age_categories = ["27-40", "41-60", "61+"]

        # Filter the DataFrame to include only Masters rowers
        masters_df = survey_data[
            survey_data["age_category"].isin(masters_age_categories)
        ].copy()

        print("\nFiltered for Masters rowers (age 27+).")
        print(
            f"Found {len(masters_df)} Masters rowers out of {len(survey_data)} total responses."
        )

        print("\nFirst 5 rows of the Masters survey data:")
        print(masters_df.head())

        print("\nMasters DataFrame Info (with updated data types):")
        masters_df.info()

        # Create and save the chart
        create_bar_chart(
            masters_df,
            "desired_masters_season_extension",
            chart_name="desired_masters_season_extension_distribution",
            title="Desired Masters Season Extension",
        )

        # Create charts for location preference
        create_bar_chart(
            masters_df,
            "prefer_canning_bridge_masters",
            chart_name="prefer_canning_bridge_masters_distribution",
            title="Preference for Canning Bridge for Masters Regattas",
        )

        create_bar_chart(
            masters_df,
            "prefer_champion_lakes_masters",
            chart_name="prefer_champion_lakes_masters_distribution",
            title="Preference for Champion Lakes for Masters Regattas",
        )

        create_bar_chart(
            masters_df,
            "support_1st_place_medals_masters",
            chart_name="support_1st_place_medals_masters_distribution",
            title="Support for 1st Place Medals for Masters",
        )

        # --- NEW: Create charts for the rating questions ---
        rating_columns = {
            "rating_promotion_governance": "Rating of Promotion and Governance",
            "rating_accessibility": "Rating of Accessibility",
            "rating_positive_experience": "Rating of Positive Experience",
            "rating_high_performance_pathways": "Rating of High-Performance Pathways",
        }

        for col, title in rating_columns.items():
            create_bar_chart(
                survey_data,  # Using the full dataset for these general ratings
                col,
                chart_name=f"{col}_distribution",
                title=title,
            )
        # --- END NEW ---

        # --- NEW: Analyze reasons for not competing among Masters ---
        reasons_columns = {
            "reason_recreational_time_commitment": "Time Commitment",
            "reason_recreational_skill_level": "Skill Level",
            "reason_recreational_cost": "Cost",
            "reason_recreational_social_aspect": "Prefer Social Aspect",
        }

        create_reasons_summary_chart(
            masters_df,
            reason_columns=reasons_columns,
            chart_name="masters_reasons_not_competing",
            title="Primary Reasons Masters Rowers Do Not Compete",
        )

        # Also, create a separate chart for the transition support question
        create_bar_chart(
            masters_df,
            "support_transition_to_competitive",
            chart_name="masters_support_transition_to_competitive",
            title="Support for Transitioning to Competitive Rowing (Masters)",
        )
        # --- END NEW ---

    elif survey_data is not None:
        # If only data is loaded, show original data
        print("\nFirst 5 rows of the survey data:")
        print(survey_data.head())

        print("\nDataframe Info:")
        survey_data.info()
