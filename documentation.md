# Plesk Checker Project Analysis

## Overview

This project is a GUI application built with `customtkinter` for checking Plesk logins. It allows users to input a list of Plesk URLs, usernames, and passwords from a file, and then checks the validity of these credentials against Plesk servers.

## Key Components

*   **GUI Structure:** The application features a main window with frames and widgets for input, progress display, and results presentation.
*   **Input:** The user provides a file containing Plesk login credentials in the format `URL|username|password`.
*   **Processing:** The application reads the input file, checks each login using the `check_plesk_login` function (located in `handlers/plesk_api.py`), and displays the results in a treeview.
*   **Threading:** The application uses threading to perform login checks in the background, preventing the GUI from freezing. A queue is used for communication between threads and updating the GUI.
*   **Output:** Results are displayed in two tabs: "All Results" and "List Valid cPanel." The "List Valid cPanel" tab includes pagination. A button enables automatic login for valid credentials.

## File Structure and Functionality

*   `main.py`: The main application file. It initializes the GUI, handles user input, starts the checking process, and updates the GUI with results.
*   `config.py`: Contains configuration settings such as the application title, window size, appearance settings, and output file paths.
*   `handlers/plesk_api.py`: Contains the `check_plesk_login` function, which handles the Plesk login attempt. It sends a POST request to the `/login_up.php` endpoint and checks the response for success.
*   `handlers/file_handler.py`: Provides functions for reading and writing data to files, as well as checking for duplicate entries. Includes functions like `is_duplicate`, `write_to_file`, and `read_lines_from_file`.
*   `utils.py`: Contains utility functions such as centering the window, creating the treeview, calculating ETA, and opening the web login page.

## Workflow

1.  The user selects an input file containing Plesk login credentials.
2.  The application reads the file and displays the total number of lines.
3.  The user starts the checking process.
4.  The application spawns a thread to perform the login checks in the background.
5.  For each line in the input file, the `check_plesk_login` function is called to verify the credentials.
6.  The results are added to a queue.
7.  The main thread processes the queue and updates the GUI with the results.
8.  The application displays the progress, including the number of valid, failed, timeout, and duplicate logins.
9.  Valid logins are displayed in the "List Valid cPanel" tab, with an option to automatically log in.

## Key Functions

*   `check_plesk_login(url, username, password)`: (In `handlers/plesk_api.py`) Checks the Plesk login credentials.
*   `is_duplicate(output_file, entry)`: (In `handlers/file_handler.py`) Checks if an entry already exists in the output file.
*   `create_treeview(parent_frame, columns)`: (In `utils.py`) Creates a styled treeview widget.
*   `open_web_login(url, username, password)`: (In `utils.py`) Opens a web browser with the Plesk login URL.

## Configuration

Important configuration options are stored in `config.py`, including:

*   `OUTPUT_FILE_STATUS`: Path to the file for saving login status results.
*   `OUTPUT_FILE_LOGINS`: Path to the file for saving valid login credentials.
*   `APP_TITLE`, `APP_GEOMETRY`, `APP_MINSIZE`: GUI-related settings.

## Summary

This project provides a user-friendly interface for checking Plesk logins, with features such as threading, progress tracking, and automatic login. It is well-structured and uses separate modules for different functionalities, making it relatively easy to understand and maintain.