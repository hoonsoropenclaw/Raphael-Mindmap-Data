# Python Automation and Server Management

## Overview
This micro-skill focuses on leveraging Python for scripting, automation tasks, and setting up local servers using Python's built-in `http.server` module. It covers essential aspects such as command-line interface (CLI) creation, server setup, and troubleshooting common issues.

---

## Python Scripting for Automation

### Description
This section provides guidance on writing Python scripts for automation, including command-line interfaces (CLI) with argument parsing, help messages, and subcommand handling.

### Key Code Snippets

#### Argument Parsing with `argparse`
```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='Calendar Reminder Workflow')
    parser.add_argument('--source', choices=['google', 'fixture'], default='fixture', help='Source of the calendar data')
    parser.add_argument('--rules', type=str, required=True, help='Rules for processing calendar events')
    parser.add_argument('--state', type=str, required=True, help='Current state of the workflow')
    parser.add_argument('--lookahead-seconds', type=int, default=60, help='Lookahead time in seconds for reminders')
    parser.add_argument('--webhook-url', type=str, default=None, help='Webhook URL for notifications')
    parser.add_argument('--webhook-timeout', type=int, default=10, help='Timeout for webhook requests in seconds')
    args = parser.parse_args()
    # Additional logic using args
    ...
```

### Common Errors and Solutions

- **Parameter Parsing Errors**: 
  - **Issue**: Missing required arguments or invalid input values.
  - **Solution**: Ensure all required parameters have default values or prompt the user for input. Validate input values and provide clear error messages.

- **Subcommand Conflicts**:
  - **Issue**: Subcommands overlapping or not clearly defined.
  - **Solution**: Clearly define subcommands and ensure they do not overlap. Provide comprehensive help messages using `argparse` to guide users.

---

## Setting Up a Local HTTP Server

### Description
This section explains how to use Python's built-in `http.server` module to set up a simple local HTTP server for serving static files.

### Key Code Snippets

#### Basic Server Setup
```bash
python3 -m http.server 8765 --bind 127.0.0.1
```
This command starts a server on `localhost` (127.0.0.1) at port `8765`.

#### Specifying a Directory
If you need to serve files from a specific directory, use the `--directory` parameter:
```bash
python3 -m http.server 8766 --bind 127.0.0.1 --directory /path/to/directory
```

### Common Errors and Solutions

- **Port Already in Use**:
  - **Issue**: Attempting to bind to a port that is already occupied.
  - **Solution**: Choose a different port number or terminate the process currently using the port. For example:
    ```bash
    lsof -i :8765
    kill -9 <PID>
    ```
    Replace `<PID>` with the actual process ID.

- **Directory Not Found**:
  - **Issue**: The specified directory does not exist or the path is incorrect.
  - **Solution**: Verify the directory path and ensure it exists. Use absolute paths to avoid confusion.

- **Permission Issues**:
  - **Issue**: Lack of permissions to bind to the desired port or access the specified directory.
  - **Solution**: Run the command with appropriate permissions (e.g., using `sudo` if necessary) or choose a different port or directory.

---

## Best Practices for Python Automation and Server Management

- **Error Handling**: Always include error handling in your scripts to manage unexpected situations gracefully.
- **Logging**: Implement logging to track the behavior of your scripts and servers. This aids in debugging and monitoring.
- **Security**: When setting up servers, ensure that sensitive information is not exposed. Use secure configurations and validate all inputs.
- **Documentation**: Maintain clear documentation for your scripts and server setups to facilitate maintenance and onboarding of new team members.

---

By mastering these aspects, you can effectively use Python for automation tasks and manage local servers with ease, ensuring robust and maintainable solutions.