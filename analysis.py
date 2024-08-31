import json
from tqdm import tqdm
from pprint import pprint
import pandas as pd
import os
import sys
import logging
import concurrent.futures
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import numpy as np

DEBUG = False

# Suppress specific FutureWarnings related to dtype in NumPy
warnings.filterwarnings("ignore", category=FutureWarning, module="numpy")


logging.basicConfig(
    filename="analysis_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Analysis:
    def __init__(self):
        self.results = []
        self.dataset_count = 0

    def check_missing_values(self, df):
        missing_values = df.isnull().sum().sum()
        total_values = df.size
        return {
            "check": "Missing Values",
            "count": int(missing_values),
            "total": int(total_values),
            "percentage": (
                float((missing_values / total_values) * 100) if total_values else 0.0
            ),
            # 'count': missing_values,
            # 'total': total_values,
            # 'percentage': (missing_values / total_values) * 100 if total_values else 0
        }

    def check_null_values(self, df):
        null_values = df.isna().sum().sum()
        total_values = df.size
        return {
            "check": "Null Values",
            "count": int(null_values),
            "total": int(total_values),
            "percentage": (
                float((null_values / total_values) * 100) if total_values else 0.0
            ),
            # 'count': null_values,
            # 'total': total_values,
            # 'percentage': (null_values / total_values) * 100 if total_values else 0
        }

    def check_data_types(self, df):
        invalid_data_count = 0
        total_values = df.size
        for col, col_type in df.dtypes.items():
            try:
                invalid_data_count += (
                    ~df[col].apply(pd.api.types.is_dtype_equal, args=(col_type,))
                ).sum()
            except:
                invalid_data_count += len(df)
        return {
            "check": "Invalid Data Types",
            "count": int(invalid_data_count),
            "total": int(total_values),
            "percentage": (
                float((invalid_data_count / total_values) * 100)
                if total_values
                else 0.0
            ),
            # 'count': invalid_data_count,
            # 'total': total_values,
            # 'percentage': (invalid_data_count / total_values) * 100 if total_values else 0
        }

    def check_unique_identifier(self, df):
        identifier_col = df.columns[0]
        unique_values = df[identifier_col].nunique()
        total_values = len(df[identifier_col])
        return {
            "check": "Unique Identifier Check",
            "count": int(total_values - unique_values),
            "total": int(total_values),
            "percentage": (
                float(((total_values - unique_values) / total_values) * 100)
                if total_values
                else 0.0
            ),
            # 'count': total_values - unique_values,
            # 'total': total_values,
            # 'percentage': ((total_values - unique_values) / total_values) * 100 if total_values else 0
        }

    def analyze(self, df):
        return [
            self.check_missing_values(df),
            self.check_null_values(df),
            self.check_data_types(df),
            self.check_unique_identifier(df),
        ]

    """ 
    def generate_report(self, individual_reports):
        combined_results = pd.DataFrame([res for report in individual_reports for res in report['analysis_results']])
        
        logging.info("--- Final Analysis Report ---")
        number_of_dataset_analyzed = len(individual_reports)
        print("\n--- Final Analysis Report ---")
        print(f"Number of datasets analyzed: {number_of_dataset_analyzed}")
        logging.info(f"Number of datasets analyzed: {number_of_dataset_analyzed}")
        print("Combined results ")
        null_values = 
        invalid_data_types = 
        missing_values = 
        unique_identifier_check =  
        combined_summary = {
        "null_values"
        "invalid_data_types"    
        "unique_identifier_check"
        "missing_values":""  
        }

        
        combined_summary = combined_results.groupby('check').sum()

        for check, row in combined_summary.iterrows():
            print(f"{check}: {row['percentage']:.2f}% ({row['count']}/{row['total']})")
            logging.info(f"{check}: {row['percentage']:.2f}% ({row['count']}/{row['total']})")

        return combined_summary
    """

    def generate_report(self, individual_reports):
        combined_results = pd.DataFrame(
            [res for report in individual_reports for res in report["analysis_results"]]
        )

        logging.info("--- Final Analysis Report ---")
        number_of_dataset_analyzed = len(individual_reports)
        print("\n--- Final Analysis Report ---")
        print(f"Number of datasets analyzed: {number_of_dataset_analyzed}")
        logging.info(f"Number of datasets analyzed: {number_of_dataset_analyzed}")
        print("Combined results ")

        # Calculate total records
        total_records = combined_results["total"].sum()

        # Calculate percentages for each category
        summary = (
            combined_results.groupby("check")
            .agg({"count": "sum", "total": "sum"})
            .reset_index()
        )
        summary["percentage"] = (summary["count"] / total_records) * 100

        # Create the combined summary dictionary
        combined_summary = {
            "null_values": round(
                summary[summary["check"] == "Null Values"]["percentage"].iloc[0], 2
            ),
            "invalid_data_types": round(
                summary[summary["check"] == "Invalid Data Types"]["percentage"].iloc[0],
                2,
            ),
            "missing_values": round(
                summary[summary["check"] == "Missing Values"]["percentage"].iloc[0], 2
            ),
            "unique_identifier_check": round(
                summary[summary["check"] == "Unique Identifier Check"][
                    "percentage"
                ].iloc[0],
                2,
            ),
        }

        # Print and log the combined summary
        for check, percentage in combined_summary.items():
            print(f"{check.replace('_', ' ').title()}: {percentage:.2f}%")
            logging.info(f"{check.replace('_', ' ').title()}: {percentage:.2f}%")

        # Print summary by check type
        print("\nSummary by check type:")
        for _, row in summary.iterrows():
            print(
                f"{row['check']}: {row['percentage']:.2f}% ({row['count']}/{row['total']})"
            )
            logging.info(
                f"{row['check']}: {row['percentage']:.2f}% ({row['count']}/{row['total']})"
            )

        return combined_summary

    def generate_charts(self, combined_summary):
        sns.set(style="whitegrid")

        # Create combined bar chart for all checks
        self.create_combined_bar_chart(combined_summary)

    def create_combined_bar_chart(self, combined_summary):
        df = pd.DataFrame(
            list(combined_summary.items()), columns=["Check Type", "Percentage"]
        )

        plt.figure(figsize=(10, 6))
        sns.barplot(
            x=combined_summary.index,
            y=combined_summary["percentage"],
            palette="Blues_d",
        )
        plt.title(f"Combined Data Quality Analysis Across All Datasets")
        plt.xlabel("Check Type")
        plt.ylabel("Percentage of Issues")
        plt.xticks(rotation=45, ha="right")
        plt.ylim(0, 100)
        plt.tight_layout()
        plt.savefig("combined_bar_chart.png")
        plt.show()


def load_dataset(file_name, chunk_size=10000):
    file_ext = os.path.splitext(file_name)[1]
    encodings_to_try = ["utf-8", "ISO-8859-1", "Windows-1252"]

    if file_ext == ".csv":
        for encoding in encodings_to_try:
            try:
                return pd.concat(
                    pd.read_csv(file_name, encoding=encoding, chunksize=chunk_size)
                )
            except UnicodeDecodeError:
                logging.warning(
                    f"Failed to load {file_name} with {encoding} encoding. Trying next encoding..."
                )
        raise ValueError(f"Unable to decode file {file_name} with known encodings.")

    elif file_ext == ".xlsx":
        return pd.read_excel(file_name)

    elif file_ext == ".json":
        return pd.read_json(file_name)

    else:
        raise ValueError(f"Unsupported file type: {file_ext}")


def process_dataset(dataset, analysis):
    display_name = dataset.get("dataset_display_name")
    file_name = dataset.get("dataset_file_name")

    logging.info(f"Loading dataset: {display_name}")
    try:
        df = load_dataset(file_name)
        analysis_results = analysis.analyze(df)
        # return json.dumps({"dataset_name": display_name, "dataset_file_path": file_name, "analysis_results": analysis_results})
        return {
            "dataset_name": display_name,
            "dataset_file_path": file_name,
            "analysis_results": analysis_results,
        }
    except Exception as e:
        logging.error(f"Failed to load {file_name}: {e}")
        return {
            "dataset_name": display_name,
            "dataset_file_path": file_name,
            "analysis_results": [],
            "error": str(e),
        }


def process_datasets(json_file):
    analysis = Analysis()
    individual_reports = []

    with open(json_file, "r") as f:
        datasets = json.load(f)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_dataset, dataset, analysis) for dataset in datasets
        ]
        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(datasets)
        ):
            individual_reports.append(future.result())

    # Save individual dataset analysis report
    print("=" * 80)
    print("Individual Report")
    print("=" * 80)
    print("*" * 80)
    pprint(individual_reports)
    print("*" * 80)
    individual_dataset_analysis_report_file_name = (
        "individual_dataset_analysis_report.json"
    )
    if DEBUG:
        individual_dataset_analysis_report_file_name = (
            "individual_dataset_analysis_report_debug.json"
        )

    with open(individual_dataset_analysis_report_file_name, "w") as f:
        json.dump(individual_reports, f, indent=4)

    # Generate and save combined analysis report
    combined_summary = analysis.generate_report(individual_reports)
    print("=" * 80)
    print("Combined summery  Report")
    print("=" * 80)
    print("$" * 80)
    pprint(combined_summary)
    print("$" * 80)
    # combined_summary.to_json(f, orient="index")
    combined_dataset_analysis_report_file_name = "combined_dataset_analysis_report.json"
    if DEBUG:
        combined_dataset_analysis_report_file_name = (
            "combined_dataset_analysis_report.json"
        )

    with open(combined_dataset_analysis_report_file_name, "w") as f:
        json.dump(combined_summary, f, indent=4)

        # combined_summary.to_json(f, orient="index")

    # analysis.generate_charts(combined_summary)


def main():
    if len(sys.argv) != 3:
        print("Usage: python analysis.py <path_to_json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    debug_flag = str(sys.argv[2])
    if debug_flag == "-d":
        print("IN DEBUG MODE")
        DEBUG = True

    if not os.path.isfile(json_file):
        print(f"File not found: {json_file}")
        sys.exit(1)

    process_datasets(json_file)


if __name__ == "__main__":
    main()
