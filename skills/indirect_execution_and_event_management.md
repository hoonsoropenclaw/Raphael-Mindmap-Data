# Indirect Execution and Event Management

## Overview
This micro-skill focuses on managing the indirect evaluation and execution of code while ensuring synchronization and deduplication of events. It leverages indirect `eval` for executing compiled code in the global scope and integrates Google Calendar API synchronization with SQLite-based deduplication to maintain accurate and up-to-date event data.

## Indirect Eval Execution

### Purpose
To execute compiled code in a way that makes destructured variables (e.g., `ReactFlow`) accessible in the global scope, indirect `eval` is used. This approach ensures that variables are correctly scoped and accessible globally.

### Implementation
```javascript
const indirectEval = eval;
indirectEval(compiled);
```
- **Explanation**: By assigning `eval` to a variable (`indirectEval`), the execution context is altered, allowing the code to run in the global scope rather than the local scope.

### Key Considerations
- **Security**: Be cautious when executing compiled code to avoid security vulnerabilities. Ensure that the code being executed is from a trusted source.
- **Error Handling**: Wrap the `indirectEval` call in a `try-catch` block to handle potential runtime errors gracefully.

## Event Synchronization and Deduplication

### Google Calendar Synchronization

#### Description
The synchronization module uses the Google Calendar API to perform incremental synchronization of events, handling additions, updates, and cancellations.

#### Key Code Snippet
```python
def fetch_changes(credentials_path: str, sync_token: str | None) -> tuple[list[EventChange], str | None]:
    ...
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(
        calendarId=calendar_id,
        syncToken=sync_token,
        singleEvents=True,
        maxResults=250
    ).execute()
    ...
    return changes, next_sync_token
```

#### Common Errors and Prevention
- **Error**: Improper handling of `syncToken` expiration, leading to synchronization failure.
  - **Prevention**: Catch exceptions when the `syncToken` is invalid, perform a full synchronization, and obtain a new `syncToken`.
  
- **Error**: Failure to handle pagination, resulting in data loss.
  - **Prevention**: Check for the presence of `nextPageToken` and continue requesting data until all pages are retrieved.

#### Best Practices
- Always validate the `syncToken` before using it to fetch changes.
- Implement retry logic for transient errors during API calls.
- Log synchronization activities for auditing and debugging purposes.

### SQLite Deduplication

#### Description
The deduplication module utilizes an SQLite database to store processed event IDs and ETags, ensuring that each event is processed only once and avoiding duplicate event pushes.

#### Key Code Snippet
```python
class DedupeStore:
    def __init__(self, db_path: str) -> None:
        ...
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_events (
                event_id TEXT NOT NULL,
                etag TEXT NOT NULL,
                pushed_at INTEGER NOT NULL,
                PRIMARY KEY (event_id, etag)
            )
        """)
        ...

    def is_seen(self, event_id: str, etag: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM seen_events WHERE event_id=? AND etag=?",
            (event_id, etag),
        ).fetchone()
        return row is not None
        ...
```

#### Common Errors and Prevention
- **Error**: Improper handling of SQLite connections, causing database locks or data loss.
  - **Prevention**: Use connection pooling or thread locks to manage SQLite connections in a multi-threaded environment.
  
- **Error**: Failure to handle duplicate events, resulting in duplicate pushes.
  - **Prevention**: Before inserting a new event, check the `seen_events` table to determine if the event has already been processed.

#### Best Practices
- Regularly back up the SQLite database to prevent data loss.
- Optimize database queries for performance, especially when dealing with a large number of events.
- Implement proper error handling and logging around database operations to facilitate troubleshooting.

### Integration of Synchronization and Deduplication

#### Workflow
1. **Fetch Changes**: Use the Google Calendar API to fetch event changes using the `fetch_changes` function.
2. **Process Events**: For each event change, check if the event has already been seen using the `DedupeStore` class.
3. **Update Dedupe Store**: If the event is new, process it and update the `seen_events` table in the SQLite database.
4. **Handle Sync Tokens**: After processing, update the `syncToken` to ensure future synchronizations are incremental.

#### Error Handling
- **Network Issues**: Implement retry mechanisms for network-related errors during API calls.
- **Database Errors**: Handle SQLite errors gracefully, ensuring that the application can recover from transient issues.
- **Data Consistency**: Ensure that the synchronization and deduplication processes are atomic to maintain data integrity.

## Conclusion
By combining indirect `eval` execution with Google Calendar API synchronization and SQLite-based deduplication, this micro-skill ensures that both code execution and event data management are handled efficiently and accurately. Proper error handling and best practices are crucial to maintaining the reliability and efficiency of the system.