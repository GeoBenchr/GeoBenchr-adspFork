import pandas as pd
import matplotlib.pyplot as plt

# Relative path to the CSV file
csv_file = "mobilitydb-simra-durations-single.csv"  # Adjust this path as needed

try:
    dataframe = pd.read_csv(csv_file, header=None, names=["operation", "count", "start_time", "end_time", "duration"])

    dataframe["leading_attribute"] = dataframe["operation"].str.split("_").str[0]

    average_durations = dataframe.groupby("leading_attribute")["duration"].mean().reset_index()

    plt.figure(figsize=(8, 6))
    plt.bar(average_durations["leading_attribute"], average_durations["duration"], color="lightcoral")
    plt.ylabel("Average Duration (s)", fontsize=14)
    plt.title("Average Duration by Attribute", fontsize=16)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

except FileNotFoundError:
    print(f"Error: The file '{csv_file}' was not found. Please check the file path and try again.")
except Exception as e:
    print(f"An error occurred: {e}")
