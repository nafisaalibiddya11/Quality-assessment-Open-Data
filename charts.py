import json
import matplotlib.pyplot as plt
import seaborn as sns

# Define variables from report.txt (based on your provided info)
null_values_percentage = 3.43
invalid_data_types_percentage = 32.6
missing_values_percentage = 3.43
unique_identifier_check_percentage = 1.44

# Extract data for pie and bar charts
categories = {
    "Null Values": null_values_percentage,
    "Invalid Data Types": invalid_data_types_percentage,
    "Missing Values": missing_values_percentage,
    "Unique Identifier Check": unique_identifier_check_percentage,
}


# Pie chart
def create_pie_chart(data):
    plt.figure(figsize=(8, 8))
    plt.pie(
        data.values(),
        labels=data.keys(),
        autopct="%1.1f%%",
        colors=sns.color_palette("pastel"),
        startangle=140,
    )
    plt.title("Data Quality Issues Distribution")
    plt.savefig("pie_chart.png")
    plt.show()


# Bar chart
def create_bar_chart(data):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(data.keys()), y=list(data.values()), palette="Blues_d")
    plt.title("Percentage of Different Data Quality Issues")
    plt.xlabel("Issue Type")
    plt.ylabel("Percentage")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig("bar_chart.png")
    plt.show()


# Generate charts
create_pie_chart(categories)
create_bar_chart(categories)
