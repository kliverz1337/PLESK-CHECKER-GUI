# Plesk Checker

This Python script is designed to automate the process of checking login credentials for multiple Plesk control panel instances. It reads a list of Plesk URLs, usernames, and passwords from an input file, attempts to log in to each instance concurrently, and reports the login status along with the subscription status (active, no subscriptions, or suspended).

## Features

*   **Concurrent Checking**: Utilizes multithreading to check multiple Plesk instances simultaneously, significantly speeding up the process.
*   **Retry Mechanism**: Implements retry logic for HTTP requests to handle transient network issues or temporary server unavailability.
*   **Status Reporting**: Provides detailed feedback on each login attempt, indicating whether it was successful, failed, or timed out.
*   **Subscription Status Detection**: Identifies the subscription status of valid Plesk accounts (Active, No Subscriptions, Suspended).
*   **Duplicate Prevention**: Ensures that successful login entries are not duplicated in the output files.
*   **Console Progress**: Updates the console title to show the real-time progress of the checking process.
*   **Colored Output**: Uses `colorama` for enhanced readability of console messages.

## Requirements

*   Python 3.x
*   `requests` library
*   `colorama` library

You can install the required libraries using pip:
```bash
pip install requests colorama
```

## Usage

1.  **Prepare your input file**: Create a text file (e.g., `plesk_list.txt`) containing the Plesk URLs and credentials. Each line in the file should follow one of these formats:
    *   `url|username:password`
    *   `url|username|password`

    **Example `plesk_list.txt`:**
    ```
    https://plesk1.example.com|admin:password123
    http://plesk2.example.org|user1|pass456
    https://plesk3.example.net|root:securepass
    ```

2.  **Run the script**: Execute the script from your terminal:
    ```bash
    python plesk_checker.py
    ```

3.  **Enter the input file path**: When prompted, enter the full path or relative path to your input file (e.g., `plesk_list.txt`).

The script will then start processing the list, displaying real-time updates in the console.

## Output Files

The script generates two output files in the same directory where it is executed:

*   `valid_plesk_status.txt`: Contains successful logins with their detected subscription status.
    **Format**: `url|username:password | STATUS`
    **Example**:
    ```
    https://plesk1.example.com|admin:password123 | ACTIVE
    http://plesk2.example.org|user1:pass456 | NO SUBSCRIPTIONS
    ```

*   `valid_plesk_logins.txt`: Contains only the successful login credentials, without the status.
    **Format**: `url|username:password`
    **Example**:
    ```
    https://plesk1.example.com|admin:password123
    http://plesk2.example.org|user1:pass456
    ```

## Functions

### `print_banner()`
Displays an ASCII art banner for "PLESK CHECKER" in the console.

### `get_session_with_retries(retries: int, backoff_factor: float, status_forcelist: list)`
*   **Purpose**: Configures and returns a `requests.Session` object with built-in retry logic for HTTP requests.
*   **Parameters**:
    *   `retries` (`int`): The total number of retries to allow.
    *   `backoff_factor` (`float`): A backoff factor to apply between attempts.
    *   `status_forcelist` (`list` of `int`): A list of HTTP status codes that should trigger a retry.
*   **Returns**: `requests.Session` - A session object configured for retries.

### `check_plesk_login(url: str, username: str, password: str)`
*   **Purpose**: Attempts to log in to a Plesk instance and determines its status.
*   **Parameters**:
    *   `url` (`str`): The base URL of the Plesk panel.
    *   `username` (`str`): The username for login.
    *   `password` (`str`): The password for login.
*   **Returns**:
    *   `tuple` (`url`, `username`, `password`, `status_message`): If login is successful. `status_message` can be "ACTIVE", "NO SUBSCRIPTIONS", or "SUSPENDED".
    *   `str` "FAILED": If login credentials are incorrect or the response does not indicate a successful login.
    *   `str` "TIMEOUT": If the request times out.

### `is_duplicate(output_file: str, entry: str)`
*   **Purpose**: Checks if a given entry string already exists in the specified output file to prevent duplicates.
*   **Parameters**:
    *   `output_file` (`str`): The path to the file to check.
    *   `entry` (`str`): The string to search for.
*   **Returns**: `bool` - `True` if the entry is found, `False` otherwise.

### `set_console_title(title: str)`
*   **Purpose**: Sets the title of the console window to display progress.
*   **Parameters**:
    *   `title` (`str`): The string to set as the console title.
*   **Returns**: `None`

### `process_line(line: str, output_file: str, output_file2: str, total_list: int, i: int, result_counts: dict)`
*   **Purpose**: Parses a single line from the input file, performs the Plesk login check, and updates global results and console progress. This function is designed to be executed by a thread.
*   **Parameters**:
    *   `line` (`str`): A single line from the input file containing URL and credentials.
    *   `output_file` (`str`): Path to the `valid_plesk_status.txt` file.
    *   `output_file2` (`str`): Path to the `valid_plesk_logins.txt` file.
    *   `total_list` (`int`): The total number of entries in the input file.
    *   `i` (`int`): The current index of the line being processed (for progress display).
    *   `result_counts` (`dict`): A dictionary to store the counts of valid, failed, timeout, active, suspended, and no subscriptions.
*   **Returns**: `None`

### `main()`
*   **Purpose**: The main entry point of the script. It handles user input for the list file, orchestrates the concurrent checking process, and displays the final summary of results.
*   **Parameters**: None
*   **Returns**: `None`

## Optimization Suggestions

*   **Security Enhancement**: The current implementation disables SSL certificate verification (`verify=False`). For production use or sensitive environments, it is highly recommended to enable SSL verification and properly handle trusted certificates.
*   **Asynchronous I/O**: For even greater performance with I/O-bound tasks like network requests, consider refactoring the script to use Python's `asyncio` library with an asynchronous HTTP client like `aiohttp`. This can improve efficiency by managing concurrent connections more effectively without the overhead of threads.
*   **Command-Line Arguments**: Implement `argparse` to allow users to specify the input file, output file names, and thread count via command-line arguments, making the script more flexible and user-friendly.
*   **Structured Logging**: Replace simple `print()` statements with Python's `logging` module for more robust and configurable logging, allowing for different log levels and output destinations (console, file).
*   **Configuration File**: Externalize configurable parameters (e.g., thread count, timeout, retry settings) into a separate configuration file (e.g., `config.ini` or `config.json`).