import csv
from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth
import json
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


class TestRailAPI:
    def __init__(self, base_url, username, api_key):
        """Initialize the TestRail API client."""
        self.base_url = base_url
        self.username = username
        self.api_key = api_key
        self.auth = HTTPBasicAuth(self.username, self.api_key)

    def _make_request(self, endpoint, params=None):
        """Helper method to make GET requests to the TestRail API."""
        url = self.base_url + endpoint
        response = requests.get(url, params=params, auth=self.auth)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def get_plans(self, project_id, milestone_id):
        """Get all test plans for a given project and milestone."""
        endpoint = f"get_plans/{project_id}"
        params = {'milestone_id': milestone_id}
        return self._make_request(endpoint, params)

    def get_plan(self, plan_id):
        """Get details of a specific test plan."""
        endpoint = f"get_plan/{plan_id}"
        return self._make_request(endpoint)

    def get_tests(self, run_id):
        """Get test cases associated with a test run."""
        endpoint = f"get_tests/{run_id}"
        return self._make_request(endpoint)

    def get_all_tests(self, run_id):
        all_tests = []
        url = f"get_tests/{run_id}&limit=250"
        while url:
            # Make the API call
            response = requests.get(self.base_url + url, auth=self.auth)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

            data = response.json()
            # Append tests to the result list
            all_tests.extend(data.get("tests", []))

            # Check if there's a next page
            next_url = data["_links"].get("next")
            url = next_url.replace("/api/v2/", "") if next_url else None

        return all_tests

    def get_run_details(self, run_id):
        """Get details of a specific test run (including the name)."""
        endpoint = f"get_run/{run_id}"
        return self._make_request(endpoint)

    def get_runs(self, project_id, milestone_id):
        """Get all test runs for a given project and milestone."""
        endpoint = f"get_runs/{project_id}"
        params = {'milestone_id': milestone_id}
        return self._make_request(endpoint, params)

    def get_test_cases(self, project_id, suite_id):
        """Get all test cases for a given project and test suite."""
        endpoint = f"get_cases/{project_id}"
        params = {'suite_id': suite_id}
        return self._make_request(endpoint, params)

    def get_test_results(self, run_id):
        """Get test results for a specific test run."""
        endpoint = f"get_results_for_run/{run_id}"
        return self._make_request(endpoint)


def merge_data(assigned_tests_file, tester_name_file, output_file):
    # Load tester_name.csv into a dictionary for quick lookup
    tester_name_map = {}
    with open(tester_name_file, mode='r', newline='', encoding='utf-8') as tester_file:
        reader = csv.DictReader(tester_file)
        for row in reader:
            tester_name_map[row['id']] = row['name']

    # Process assigned_tests_count_with_run_name.csv and merge data
    output_rows = []
    with open(assigned_tests_file, mode='r', newline='', encoding='utf-8') as assigned_file:
        reader = csv.DictReader(assigned_file)
        headers = reader.fieldnames + ['Tester Name']  # Add "Tester Name" column to the output headers

        for row in reader:
            assigned_to_id = row['Assigned To ID']
            if assigned_to_id == "null" or not assigned_to_id:  # Handle unassigned cases
                row['Tester Name'] = "Unassigned"
            else:
                row['Tester Name'] = tester_name_map.get(assigned_to_id,
                                                         "Unknown Tester")  # Default to "Unknown Tester"
            output_rows.append(row)

    # Write the merged data to output CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as output_csv:
        writer = csv.DictWriter(output_csv, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Merged data saved to {output_file}")


def merge_file(tests_csv_path, users_csv_path, output_csv_path, summary_csv_path):
    """
    Merge test data with user data, add Tester Name, and remove Assigned To ID column.
    Save the final output to a CSV file.

    :param tests_csv_path: Path to the CSV file containing test data with Assigned To ID.
    :param users_csv_path: Path to the CSV file containing user data with IDs and names.
    :param output_csv_path: Path to save the merged output CSV.
    :param summary_csv_path Path to save summary
    """
    # Read the CSV files
    tests_df = pd.read_csv(tests_csv_path)
    users_df = pd.read_csv(users_csv_path)

    # Merge on Assigned To ID
    merged_df = tests_df.merge(
        users_df, left_on="Assigned To ID", right_on="id", how="left"
    )

    # Rename "name" column from users_df to "Tester Name"
    merged_df.rename(columns={"name": "Tester Name"}, inplace=True)

    # Drop the "Assigned To ID" column
    merged_df.drop(columns=["Assigned To ID"], inplace=True)

    # Drop the "id" column
    merged_df.drop(columns=["id"], inplace=True)

    # Save the result to a new CSV file
    merged_df.to_csv(output_csv_path, index=False)

    print(f"Data merged and saved to {output_csv_path}")

    # Count total test cases per tester
    summary_df = merged_df.groupby("Tester Name", as_index=False).agg(
        {"Total Case Count": "sum"}
    )
    # Save the summary data to a CSV file
    summary_df.to_csv(summary_csv_path, index=False)

    print(f"Merged data saved to {output_csv_path}")
    print(f"Summary data saved to {summary_csv_path}")
# Example Usage


if __name__ == "__main__":
    # Load credentials from environment variables

    BASE_URL = os.getenv('BASE_URL')
    USERNAME = os.getenv('TESTRAIL_USERNAME')  # Fetch from .env file
    API_KEY = os.getenv('TESTRAIL_API_KEY')  # Fetch from .env file
    project_id = 4
    milestone_id = 278
    # Input and output file names
    input_csv = 'assigned_tests_count_with_run_name.csv'  # Existing file
    output_csv = 'assigned_tests_count_with_tester_name.csv'  # Updated file
    summary_csv_path = 'summary.csv'
    tester_name_csv = 'tester_name.csv'
    merge_file(input_csv, tester_name_csv, output_csv,summary_csv_path)

    # Ensure credentials are set
    if not USERNAME or not API_KEY:
        print("Error: TestRail credentials are not set in the .env file.")
    else:
        # Initialize the API client
        testrail = TestRailAPI(BASE_URL, USERNAME, API_KEY)

        # Example: Get plans for project 4 with milestone 278

        plans = testrail.get_plans(project_id, milestone_id)

        if plans:
            print("Plan IDs:")
            plan_ids = [plan['id'] for plan in plans.get('plans', [])]
            print(plan_ids)

            # Loop through plan_ids and call the get_plan API for each plan_id
            for plan_id in plan_ids:
                print(f"Fetching details for Plan ID: {plan_id}")
                plan_details = testrail.get_plan(plan_id)

                if plan_details:
                    print(f"Details for Plan ID {plan_id}:")
                    print(json.dumps(plan_details, indent=4))
                    # Extract all run IDs from the response
                    run_ids = []
                    for entry in plan_details.get('entries', []):
                        for run in entry.get('runs', []):
                            run_ids.append(run['id'])

                    print(f"Run IDs for Plan ID {plan_id}: {run_ids}")
                    # Loop through each run_id and fetch test cases using get_tests API
                    for run_id in run_ids:
                        # Initialize a dictionary to store the count of case_id for each assignedto_id
                        assigned_to_counts = defaultdict(int)
                        unassigned_count = 0  # Counter for unassigned cases
                        # List to store the rows to write to the CSV
                        csv_data = []
                        print(f"Fetching test cases for Run ID: {run_id}")
                        tests = testrail.get_all_tests(run_id)

                        # Get the run details to fetch the name
                        run_details = testrail.get_run_details(run_id)
                        run_name = run_details.get('name') if run_details else 'Unknown Run Name'
                        config = run_details.get('config', '')
                        if config:
                            run_name += f" ({config})"

                        if tests:
                            # Loop through tests and count case_id per assignedto_id
                            for test in tests:
                                assignedto_id = test.get('assignedto_id')
                                if assignedto_id is None:
                                    unassigned_count += 1  # Increment unassigned count
                                else:
                                    assigned_to_counts[assignedto_id] += 1
                            # Prepare data for CSV
                            for assignedto_id, count in assigned_to_counts.items():
                                csv_data.append([run_id, run_name, assignedto_id, count])
                            # Append unassigned count if there are unassigned cases
                            if unassigned_count > 0:
                               csv_data.append([run_id, run_name, "Unassigned", unassigned_count])

                            # Print the counts of case_id for each assignedto_id
                            print(f"Total case counts by assignedto_id for Run ID {run_id}:")
                            for assignedto_id, count in assigned_to_counts.items():
                                print(f"Assigned to ID {assignedto_id}: {count} case(s)")
                        else:
                            print(f"Failed to fetch test cases for Run ID {run_id}")
                        # Save the data to a CSV file
                        csv_filename = 'assigned_tests_count_with_run_name.csv'
                        with open(csv_filename, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            # writer.writerow(['Run ID', 'Run Name', 'Assigned To ID', 'Total Case Count'])  # CSV header
                            writer.writerows(csv_data)  # Write the data
                        print(f"CSV file '{csv_filename}' created with the test case counts.")

                else:
                    print(f"Failed to fetch details for Plan ID {plan_id}")
        else:
            print("No test plans found.")
    # Update the CSV with user names
    merge_file(input_csv, tester_name_csv, output_csv,summary_csv_path)
