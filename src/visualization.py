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
    if (
        pd.api.types.is_categorical_dtype(df[column_name])
        and df[column_name].cat.ordered
    ):
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


def create_comparison_chart(
    df,
    column1,
    column2,
    chart_path="charts",
    brand_colors_file="BrandColours.md",
    chart_name=None,
    title=None,
):
    """
    Creates and saves a comparison bar chart for two columns using brand colors.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        column1 (str): The name of the first column to plot.
        column2 (str): The name of the second column to plot.
        chart_path (str): The directory to save the chart in.
        brand_colors_file (str): Path to the markdown file with brand colors.
        chart_name (str, optional): The filename for the saved chart. Defaults to a combination of column names.
        title (str, optional): The title of the chart. Defaults to a generic title.
    """
    if column1 not in df.columns or column2 not in df.columns:
        print(
            f"One of the columns '{column1}' or '{column2}' not found in the DataFrame."
        )
        return

    # Create the directory if it doesn't exist
    if not os.path.exists(chart_path):
        os.makedirs(chart_path)

    # Get brand colors
    brand_colors = get_brand_colors(brand_colors_file)
    default_color = brand_colors[0] if brand_colors else "#003E7E"
    secondary_color = (
        brand_colors[1] if brand_colors and len(brand_colors) > 1 else "#D9EAD3"
    )  # Light Greenish

    # Calculate counts for each category in both columns
    column1_counts = df[column1].value_counts().sort_index()
    column2_counts = df[column2].value_counts().sort_index()

    # Reindex to ensure both series have the same index (categories)
    all_categories = column1_counts.index.union(column2_counts.index)
    column1_counts = column1_counts.reindex(all_categories, fill_value=0)
    column2_counts = column2_counts.reindex(all_categories, fill_value=0)

    width = 0.35  # Width of the bars
    x = range(len(all_categories))  # The label locations

    plt.figure(figsize=(12, 8))
    # Bar plots for both columns
    bars1 = plt.bar(x, column1_counts, width, label=column1, color=default_color)
    bars2 = plt.bar(
        [i + width for i in x],
        column2_counts,
        width,
        label=column2,
        color=secondary_color,
    )

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if title:
        plt.title(title)
    else:
        plt.title(f"Comparison of '{column1}' and '{column2}' Responses")
    plt.xlabel("Response Categories")
    plt.ylabel("Count")
    plt.xticks([i + width / 2 for i in x], all_categories)
    plt.legend()

    # Save the figure
    if chart_name:
        file_name = f"{chart_name}.png"
    else:
        file_name = f"{column1}_{column2}_comparison.png"

    file_path = os.path.join(chart_path, file_name)
    plt.savefig(file_path)
    print(f"\nComparison chart saved to '{file_path}'")
    plt.close()


def create_reasons_summary_chart(
    df,
    reason_columns,
    chart_path="charts",
    brand_colors_file="BrandColours.md",
    chart_name=None,
    title=None,
):
    """
    Creates a summary bar chart for multiple boolean-like reason columns.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data.
        reason_columns (dict): A dictionary mapping column names to friendly labels.
        chart_path (str): The directory to save the chart in.
        brand_colors_file (str): Path to the markdown file with brand colors.
        chart_name (str, optional): The filename for the saved chart.
        title (str, optional): The title of the chart.
    """
    # Calculate the sum of 'True' responses for each reason column
    # Assumes the columns are boolean or 1/0
    reason_counts = df[reason_columns.keys()].sum().sort_values(ascending=False)

    # Map the column names to the friendly labels for plotting
    reason_counts.index = reason_counts.index.map(reason_columns)

    # Get brand colors
    brand_colors = get_brand_colors(brand_colors_file)
    default_color = brand_colors[0] if brand_colors else "#003E7E"

    plt.figure(figsize=(10, 7))
    sns.barplot(x=reason_counts.values, y=reason_counts.index, color=default_color)

    if title:
        plt.title(title)
    plt.xlabel("Number of Rowers Citing Reason")
    plt.ylabel("Reason")
    plt.tight_layout()

    # Save the figure
    if chart_name:
        file_name = f"{chart_name}.png"
    else:
        file_name = "reasons_summary.png"

    file_path = os.path.join(chart_path, file_name)
    if not os.path.exists(chart_path):
        os.makedirs(chart_path)
    plt.savefig(file_path)
    print(f"\nSummary chart saved to '{file_path}'")
    plt.close()
