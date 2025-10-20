import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# Define the file path.
# Make sure the Excel file is in the same directory as this script,
# or provide the full path to the file.
file_path = "2025 End of Season Rower Survey - Responses (AR).xlsx"
mapping_file_path = "column_mapping.xlsx"


def load_column_mapping(path):
    """
    Loads column mapping from an Excel file.

    Args:
        path (str): The path to the Excel file.

    Returns:
        pandas.DataFrame: The mapping DataFrame, or None.
    """
    try:
        mapping_df = pd.read_excel(path)
        print("Column mapping loaded successfully.")
        return mapping_df
    except FileNotFoundError:
        print(f"Error: The mapping file '{path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the mapping file: {e}")
        return None


def apply_data_types(df, mapping_df):
    """
    Applies data types to the DataFrame based on the mapping file.

    Args:
        df (pandas.DataFrame): The DataFrame to modify.
        mapping_df (pandas.DataFrame): DataFrame with 'new_name' and 'recommended_type'.
    """
    type_mapping = dict(zip(mapping_df["new_name"], mapping_df["recommended_type"]))

    for col_name, dtype in type_mapping.items():
        if col_name in df.columns:
            try:
                # Handle special cases first
                if pd.api.types.is_string_dtype(dtype) and dtype.startswith("Int"):
                    # For nullable integers like 'Int8'
                    df[col_name] = pd.to_numeric(df[col_name], errors="coerce").astype(
                        dtype
                    )
                elif dtype == "float64":
                    df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
                else:
                    # For standard types like 'category', 'int8', etc.
                    df[col_name] = df[col_name].astype(dtype)
            except Exception as e:
                print(f"Could not convert column '{col_name}' to '{dtype}': {e}")
    print("\nData types applied successfully.")
    return df


def load_data(path):
    """
    Loads data from an Excel file into a pandas DataFrame.

    Args:
        path (str): The path to the Excel file.

    Returns:
        pandas.DataFrame: The loaded data, or None if an error occurs.
    """
    try:
        df = pd.read_excel(path)
        print("Data loaded successfully.")
        return df
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def get_brand_colors(file_path="BrandColours.md"):
    """
    Parses a markdown file to extract brand color hex codes for charts.
    It prioritizes Primary and Accent colors.
    """
    colors = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if "HEX:" in line:
                    match = re.search(r"#(?:[0-9a-fA-F]{3}){1,2}", line)
                    if match:
                        colors.append(match.group(0))
    except FileNotFoundError:
        print(
            f"Warning: Brand color file '{file_path}' not found. Using default colors."
        )
        return None
    # Return the first 5 colors (Primary and Accent) as the main palette
    return colors[:5] if colors else None


def create_bar_chart(
    df,
    column_name,
    chart_path="charts",
    brand_colors_file="BrandColours.md",
    highlight_bar=None,
):
    """
    Creates and saves a bar chart for a given column using a primary brand color,
    with an option to highlight a specific bar.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        column_name (str): The name of the column to plot.
        chart_path (str): The directory to save the chart in.
        brand_colors_file (str): Path to the markdown file with brand colors.
        highlight_bar (str, optional): The label of the bar to highlight. Defaults to None.
    """
    if column_name not in df.columns:
        print(f"Column '{column_name}' not found in the DataFrame.")
        return

    # Create the directory if it doesn't exist
    if not os.path.exists(chart_path):
        os.makedirs(chart_path)

    # Get brand colors and set default and highlight colors
    brand_colors = get_brand_colors(brand_colors_file)
    default_color = brand_colors[0] if brand_colors else "#003E7E"  # Deep Ocean Blue
    highlight_color = (
        brand_colors[2] if brand_colors and len(brand_colors) > 2 else "#FFB81C"
    )  # Championship Gold

    # Determine the order of bars
    order = df[column_name].value_counts().index

    # Create a color palette for the bars
    if highlight_bar and highlight_bar in order:
        palette = [
            highlight_color if bar == highlight_bar else default_color for bar in order
        ]
    else:
        # Use a single color if no highlight is specified
        palette = [default_color] * len(order)

    plt.figure(figsize=(10, 6))
    sns.countplot(y=df[column_name].dropna(), order=order, palette=palette)

    plt.title(f'Distribution of Responses for "{column_name}"')
    plt.xlabel("Count")
    plt.ylabel("Response")
    plt.tight_layout()

    # Save the figure
    file_path = os.path.join(chart_path, f"{column_name}_distribution.png")
    plt.savefig(file_path)
    print(f"\nChart saved to '{file_path}'")
    plt.close()


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
        create_bar_chart(masters_df, "desired_masters_season_extension")

    elif survey_data is not None:
        # If only data is loaded, show original data
        print("\nFirst 5 rows of the survey data:")
        print(survey_data.head())

        print("\nDataframe Info:")
        survey_data.info()
