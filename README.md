# Customer Call Analysis

This project processes call records for customers, calculates the maximum number of concurrent calls for each customer on a given day, and posts the results to a specified API.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [API Reference](#api-reference)
- [License](#license)

## Installation

To set up the project, clone this repository and install the required dependencies:

```bash
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt
```

## Usage

1. Run the script to fetch call records from the API, process the data, and post the results:
   
   ```bash
   python call_analysis.py
   ```

2. Ensure that you have the necessary permissions and a valid user key to access the API.

## Dependencies

The project requires the following Python packages:

- `requests`: For making HTTP requests.
- `pytz`: For timezone handling.

You can install these dependencies using:

```bash
pip install -r requirements.txt
```

## API Reference

### Fetch Data API

- **Endpoint**: `https://candidate.hubteam.com/candidateTest/v3/problem/dataset?userKey=<your-user-key>`
- **Method**: GET
- **Description**: Fetches the call records for customers.

### Post Results API

- **Endpoint**: `https://candidate.hubteam.com/candidateTest/v3/problem/result?userKey=<your-user-key>`
- **Method**: POST
- **Description**: Posts the results of maximum concurrent calls.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
