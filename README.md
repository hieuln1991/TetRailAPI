
# TestRail Data Processor

This project processes and analyzes TestRail test data to generate reports that include details about test runs, test assignments, and total test cases per tester. The project also integrates user data to replace `Assigned To ID` with `Tester Name` for better readability.

## Features
- Fetches and processes test data from TestRail APIs.
- Merges test run data with user information for detailed reporting.
- Handles unassigned test cases and assigns them to "Unassigned".
- Generates summary reports, including total test cases per tester.
- Supports appending data to existing CSV files without overwriting.

## Prerequisites
- Python 3.7 or later.
- Required Python libraries: `pandas`, `requests`.

Install the required dependencies using pip:
```bash
pip install pandas requests
```

## Project Structure
```
.
├── assigned_tests_count_with_run_name.csv  # Input CSV with test run details
├── tester_name.csv                         # Input CSV with tester names
├── merged_output.csv                       # Output CSV with merged test data
├── tester_summary.csv                      # Output CSV with summary per tester
├── main.py                                 # Main script
├── README.md                               # Project documentation
```

## Usage

### Step 1: Fetch Test Data
Use the TestRail API to fetch test data for each run. Store the responses in a CSV file (`assigned_tests_count_with_run_name.csv`) with the following format:
| Run Name        | Assigned To ID | Total Cases |
|-----------------|----------------|-------------|
| Run A           | 23             | 10          |
| Run B           | 30             | 5           |
| Run C           | unassigned     | 8           |

### Step 2: Fetch User Data
Fetch all TestRail users using the API and save them in a CSV file (`tester_name.csv`) with the following format:
| id  | name           |
|-----|----------------|
| 23  | Tom            |
| 30  | Jerry          |

### Step 3: Process and Merge Data
Run the `main.py` script to process and merge the data:
```bash
python main.py
```
This script:
1. Merges test data (`assigned_tests_count_with_run_name.csv`) with user data (`tester_name.csv`).
2. Replace `Assigned To ID` with `Tester Name` and handle unassigned cases.
3. Saves the merged data to `merged_output.csv`.
4. Generates a summary of total test cases per tester and saves it to `tester_summary.csv`.

### Step 4: Analyze Output
#### Merged Data (`merged_output.csv`):
| Run Name        | Total Cases | Tester Name |
|-----------------|-------------|-------------|
| Run A           | 10          | Jerry       |
| Run B           | 5           | Tom         |
| Run C           | 8           | Unassigned  |

#### Summary Report (`tester_summary.csv`):
| Tester Name    | Total Cases |
|----------------|-------------|
| Tom            | 5           |
| Jerry          | 10          |
| Unassigned     | 8           |


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions
Contributions are welcome! Please submit issues or pull requests to improve the project.

## Contact
For further information or support, contact:
- **Project Owner**: Peter
- **Email**: hieuln1991@gmail.com
