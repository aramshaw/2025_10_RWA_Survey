import pandas as pd


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

    # --- NEW: Define columns that are ordered Likert scales ---
    ordered_likert_columns = [
        "support_1st_place_medals_masters",
        "rating_promotion_governance",
        "rating_accessibility",
        "rating_positive_experience",
        "rating_high_performance_pathways",
    ]
    # Define the ordered categories from disagree to agree
    category_order = [
        "Strongly Disagree",
        "Disagree",
        "Neutral",
        "Agree",
        "Strongly Agree",
    ]
    # Create an ordered categorical type
    cat_dtype = pd.api.types.CategoricalDtype(categories=category_order, ordered=True)
    # Assuming 1:Strongly Disagree, 2:Disagree, etc.
    mapping = {i + 1: label for i, label in enumerate(category_order)}
    # --- END NEW ---

    for col_name, dtype in type_mapping.items():
        if col_name in df.columns:
            try:
                # --- MODIFIED: Handle ordered categorical data for Likert scales ---
                if col_name in ordered_likert_columns:
                    df[col_name] = df[col_name].map(mapping).astype(cat_dtype)
                    print(f"Applied ordered categorical type to '{col_name}'.")
                    continue  # Skip to the next column
                # --- END MODIFIED ---

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
