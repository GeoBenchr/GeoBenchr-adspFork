import pandas as pd
import matplotlib.pyplot as plt

# Relative path to the CSV file
csv_file = "mobilitydb-simra-durations.csv"  # Adjust this path as needed

try:
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file, header=None, names=["query_type", "limit", "start_time", "end_time", "duration"])

    # Calculate average durations for each query type
    avg_durations = df.groupby("query_type")["duration"].mean()

    # Plot the results
    plt.figure(figsize=(10, 6))
    avg_durations.plot(kind="bar", color="lightcoral", edgecolor="black")

    plt.title("Average Query Execution Time by Query Type", fontsize=16)
    plt.ylabel("Duration (seconds)", fontsize=14)
    plt.xlabel("Query Type", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.show()

except FileNotFoundError:
    print(f"Error: The file '{csv_file}' was not found. Please check the file path and try again.")
except Exception as e:
    print(f"An error occurred: {e}")
