import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import pandas as pd


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
    chart_name=None,
    title=None,
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
        chart_name (str, optional): The filename for the saved chart. Defaults to column name.
        title (str, optional): The title of the chart. Defaults to a generic title.
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

    # --- MODIFICATION FOR ORDERED CATEGORIES ---
    # Check if the column is of a categorical type with a defined order
    if pd.api.types.is_categorical_dtype(df[column_name]) and df[
        column_name
    ].cat.ordered:
        order = df[column_name].cat.categories
        print(f"Using ordered categories for '{column_name}': {list(order)}")
    else:
        # Default behavior: order by frequency
        order = df[column_name].value_counts().index
    # --- END MODIFICATION ---

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

    if title:
        plt.title(title)
    else:
        plt.title(f'Distribution of Responses for "{column_name}"')
    plt.xlabel("Count")
    plt.ylabel("Response")
    plt.tight_layout()

    # Save the figure
    if chart_name:
        file_name = f"{chart_name}.png"
    else:
        file_name = f"{column_name}_distribution.png"
    file_path = os.path.join(chart_path, file_name)
    plt.savefig(file_path)
    print(f"\nChart saved to '{file_path}'")
    plt.close()
