import pandas as pd
import matplotlib.pyplot as plt

# Benchmark data
data = """
surrounding,50,1739368292.0207624,1739368292.061566,0.04080367088317871
surrounding,50,1739368292.0206625,1739368292.4745865,0.45392394065856934
"""

# Load the data into a pandas DataFrame
from io import StringIO
df = pd.read_csv(StringIO(data), header=None, names=["query_type", "limit", "start_time", "end_time", "duration"])

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
