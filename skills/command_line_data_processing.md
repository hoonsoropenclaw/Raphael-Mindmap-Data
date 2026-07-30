# Command Line Data Processing

## Overview
This micro-skill focuses on performing data processing tasks using command line tools, specifically sending HTTP requests with `curl` and counting keyword occurrences with `grep`. It covers essential commands, best practices, and troubleshooting tips to ensure efficient and error-free execution.

---

## 1. Sending HTTP Requests with `curl`

### 1.1. Description
Use the `curl` command to send HTTP requests, save the response content to a file, and output relevant metadata such as the HTTP status code and the number of bytes downloaded.

### 1.2. Key Command Pattern
```bash
curl -sS -o /path/to/output_file -w "HTTP=%{http_code} BYTES=%{size_download}\n" http://example.com/page.html
```
- `-sS`: Runs `curl` in silent mode, suppressing progress meters and error messages but allowing error codes to be displayed.
- `-o /path/to/output_file`: Specifies the file path where the response content will be saved.
- `-w "FORMAT"`: Defines the format for the output metadata. In this case, it outputs the HTTP status code and the number of bytes downloaded.
- `http://example.com/page.html`: The URL to which the HTTP request is sent.

### 1.3. Example Usage
```bash
curl -sS -o /tmp/served.html -w "HTTP=%{http_code} BYTES=%{size_download}\n" http://127.0.0.1:8766/web_output.html
```
This command sends an HTTP GET request to `http://127.0.0.1:8766/web_output.html`, saves the response to `/tmp/served.html`, and outputs the HTTP status code and the number of bytes downloaded.

### 1.4. Common Errors and Prevention

#### 1.4.1. CORS Issues
- **Problem**: The request may be blocked by the browser's CORS policy if the server does not have the appropriate CORS headers.
- **Solution**: 
  - Ensure the server is configured with the correct CORS headers.
  - Use a CDN or proxy that supports CORS.
  - If using `curl` from the command line, CORS is generally not an issue as it bypasses browser restrictions.

#### 1.4.2. Network Timeouts
- **Problem**: The request may take too long to complete, resulting in a timeout.
- **Solution**: Use the `--max-time` parameter to set a timeout limit (in seconds).
  ```bash
  curl -sS -o /tmp/served.html -w "HTTP=%{http_code} BYTES=%{size_download}\n" http://127.0.0.1:8766/web_output.html --max-time 10
  ```
  This sets the timeout to 10 seconds.

---

## 2. Counting Keyword Occurrences with `grep`

### 2.1. Description
Use the `grep` command to search for specific keywords within a file and count the number of times each keyword appears.

### 2.2. Key Command Pattern
```bash
for kw in 'ReactFlow' 'authorize' 'RBAC_MATRIX'; do
  n=$(grep -F "$kw" /path/to/input_file | wc -l)
  printf "%s %d\n" "$kw" "$n"
done
```
- `for kw in 'keyword1' 'keyword2' ...; do`: Iterates over a list of keywords.
- `grep -F "$kw" /path/to/input_file`: Searches for the exact keyword (`-F` for fixed strings) in the specified file.
- `wc -l`: Counts the number of lines where the keyword appears.
- `printf "%s %d\n" "$kw" "$n"`: Prints the keyword and the count in a formatted manner.

### 2.3. Example Usage
```bash
for kw in 'ReactFlow' 'authorize' 'RBAC_MATRIX'; do
  n=$(grep -F "$kw" /tmp/served.html | wc -l)
  printf "%s %d\n" "$kw" "$n"
done
```
This command searches for the keywords `ReactFlow`, `authorize`, and `RBAC_MATRIX` in the file `/tmp/served.html` and prints the number of occurrences for each.

### 2.4. Common Errors and Prevention

#### 2.4.1. Improper Pattern Escaping
- **Problem**: If the keyword contains special characters, `grep` may interpret them as regular expressions, leading to unexpected results.
- **Solution**: 
  - Enclose the keyword in quotes or escape special characters.
  - Use the `-F` option to treat the pattern as a fixed string.
    ```bash
    grep -F "$kw" /path/to/input_file
    ```

#### 2.4.2. Case Sensitivity
- **Problem**: By default, `grep` is case-sensitive, which may lead to missed occurrences if the case does not match.
- **Solution**: Use the `-i` option to perform a case-insensitive search.
    ```bash
    grep -Fi "$kw" /path/to/input_file | wc -l
    ```

---

## Summary
This micro-skill equips you with the knowledge to perform essential data processing tasks using `curl` and `grep` on the command line. By understanding the key commands, best practices, and common pitfalls, you can efficiently handle HTTP requests and keyword counting in your data processing workflows.