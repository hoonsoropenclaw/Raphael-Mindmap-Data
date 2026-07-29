# System Process Management

## Overview
The **system_process_management** skill focuses on resolving port allocation conflicts and managing and optimizing background processes within a system. This ensures smooth application operation and efficient resource utilization.

---

## Port Conflict Resolution

### Description
This component detects when an application attempts to bind to a port that is already in use and selects a new available port to prevent startup failures.

### Key Techniques and Code Snippets
- **Check if a port is in use**:
  ```bash
  ss -ltnp 2>/dev/null | grep 8765 || netstat -ltnp 2>/dev/null | grep 8765
  ```
- **Identify processes using a specific port**:
  ```bash
  echo "---"
  ps -ef | grep -E "uvicorn|8765" | grep -v grep | head -10
  echo "---"
  ```

### Common Errors and Prevention
- **Error**: Failing to check if a port is in use, leading to application startup failure.
  - **Prevention**: Before starting the application, use the `ss` or `netstat` command to verify the port's status.
    ```bash
    if ss -ltn | grep -q ":8765 "; then
      echo "Port 8765 is already in use."
    else
      # Proceed to start the application
    fi
    ```
- **Error**: The selected port is still occupied.
  - **Prevention**: Implement a loop to repeatedly check for port availability until a free port is found.
    ```bash
    available_port=0
    while [ $available_port -eq 0 ]; do
      PORT=8765
      if ss -ltn | grep -q ":$PORT "; then
        PORT=$((PORT + 1))
      else
        available_port=1
      fi
    done
    echo "Selected port: $PORT"
    ```

---

## Background Process Management

### Description
This component handles the lifecycle of background processes, including starting, stopping, and checking the status of processes to ensure applications run smoothly.

### Key Techniques and Code Snippets
- **List processes related to a specific application**:
  ```bash
  ps aux | grep -E "uvicorn calendar_reminder" | grep -v grep
  ```
- **Identify processes using a range of ports**:
  ```bash
  echo "---"
  ss -ltn 2>/dev/null | grep -E "87(65|66|67|68|69|70)"
  ```
- **Retrieve process ID for a specific application**:
  ```bash
  process_id=$(pgrep -f "uvicorn calendar_reminder")
  ```

### Common Errors and Prevention
- **Error**: Attempting to stop a non-existent process, resulting in an error message.
  - **Prevention**: Before stopping a process, verify its existence.
    ```bash
    if ps -p $process_id > /dev/null; then
      kill $process_id
    else
      echo "Process $process_id does not exist."
    fi
    ```
- **Error**: The process fails to stop.
  - **Prevention**: Use the `kill` command with appropriate permissions and, if necessary, forcefully terminate the process.
    ```bash
    kill -9 $process_id
    ```
  - **Note**: Use `kill -9` sparingly, as it does not allow the process to perform cleanup operations.

---

## Best Practices

### Port Management
- **Dynamic Port Allocation**: Use dynamic port allocation to minimize conflicts.
- **Port Range Specification**: Define a range of ports for the application to use, making it easier to manage and predict port usage.

### Process Management
- **Process Monitoring**: Implement monitoring to track the status of critical processes and automatically restart them if they fail.
- **Logging**: Maintain logs of process startups, shutdowns, and errors to aid in troubleshooting.
- **Resource Limits**: Set resource limits to prevent runaway processes from consuming excessive system resources.

### Error Handling
- **Graceful Degradation**: Design the system to handle failures gracefully, ensuring that one component's failure does not bring down the entire system.
- **Retry Mechanisms**: Implement retry mechanisms for transient errors, such as temporary port unavailability.

---

By integrating these strategies and techniques, the **system_process_management** skill ensures efficient and reliable management of system processes and ports, contributing to the overall stability and performance of the system.