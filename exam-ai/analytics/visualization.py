import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.patches as mpatches
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "reports", "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
})

QUALITY_COLORS = {
    "Excellent": "#2ca02c",
    "Acceptable": "#1f77b4",
    "Confusing / Poor Discrimination": "#d62728",
    "Too Easy": "#ff7f0e",
    "Too Hard": "#9467bd"
}

def plot_question_performance(result_df):
    plt.figure(figsize=(12, 6))

    result_df_sorted = result_df.sort_index(
        key=lambda x: x.str.extract(r'(\d+)').astype(int)[0]
    )

    colors = result_df_sorted["quality"].map(QUALITY_COLORS)
    result_df_sorted["avg_score"].plot(kind="bar", color=colors)

    plt.title("Average Score per Question (Colored by Quality)")
    plt.xlabel("Question")
    plt.ylabel("Average Score")
    plt.xticks(rotation=45)

    present_categories = result_df_sorted["quality"].unique()
    legend_patches = [
        mpatches.Patch(color=QUALITY_COLORS[q], label=q)
        for q in present_categories
    ]
    plt.legend(handles=legend_patches, title="Question Quality")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "avg_score_per_question.png"))
    plt.show()
    plt.close()

def plot_quality_distribution(result_df):
    plt.figure(figsize=(8, 5))

    quality_order = [
        "Excellent",
        "Acceptable",
        "Confusing / Poor Discrimination",
        "Too Easy",
        "Too Hard"
    ]

    quality_counts = result_df["quality"].value_counts()
    quality_counts = quality_counts.reindex(
        [q for q in quality_order if q in quality_counts.index]
    )

    sns.barplot(
        x=quality_counts.index,
        y=quality_counts.values,
        palette=[QUALITY_COLORS[q] for q in quality_counts.index]
    )

    plt.title("Question Quality Distribution")
    plt.xlabel("Quality Category")
    plt.ylabel("Number of Questions")
    plt.xticks(rotation=25)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "quality_distribution.png"))
    plt.show()
    plt.close()

def plot_score_distribution(df):
    plt.figure(figsize=(8, 5))

    sns.histplot(
        df["marks"],
        bins=6,
        kde=True,
        color="#4c72b0",
        edgecolor="black"
    )

    plt.title("Overall Student Score Distribution")
    plt.xlabel("Marks")
    plt.ylabel("Frequency")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "score_distribution.png"))
    plt.show()
    plt.close()

def plot_di_vs_pass(result_df):
    plt.figure(figsize=(8, 6))

    sns.scatterplot(
        x=result_df["pass_rate"],
        y=result_df["discrimination_index"],
        hue=result_df["quality"],
        palette=QUALITY_COLORS,
        s=120,
        edgecolor="black"
    )

    plt.axhline(0.2, linestyle="--", color="gray")
    plt.axvline(0.5, linestyle="--", color="gray")

    plt.text(0.72, 0.36, "Good Questions", fontsize=10)
    plt.text(0.72, 0.05, "Too Easy / Poor DI", fontsize=10)
    plt.text(0.52, 0.05, "Needs Review", fontsize=10)

    plt.title("Pass Rate vs Discrimination Index")
    plt.xlabel("Pass Rate")
    plt.ylabel("Discrimination Index")

    plt.legend(title="Quality", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "pass_vs_discrimination.png"))
    plt.show()
    plt.close()