# sop_driven_task_clarification_and_decision_making

## Purpose
The purpose of this micro-skill is to utilize Standard Operating Procedures (SOPs) to clarify task details with users and make informed decisions based on these standard procedures. This ensures that tasks are executed accurately and efficiently, minimizing potential risks and misunderstandings.

## Key Code Patterns

### Clarifying Task Details with Users
When task instructions are unclear or potentially risky, use the clarification tool to confirm specific requirements and details with the user.

```python
clarify_tool.prompt({
    "question": "Please confirm if this operation needs to be executed or provide more details.",
    "options": ["Confirm", "Cancel", "Provide more details"]
})
```

### Making Decisions Based on SOPs
Use SOPs to guide decision-making processes. This involves checking the current task against the relevant SOP and selecting the appropriate action based on the procedure.

```python
def make_decision_based_on_sop(task_details):
    sop = fetch_relevant_sop(task_details)
    if sop:
        return execute_sop_procedure(sop, task_details)
    else:
        return clarify_tool.prompt({
            "question": "No SOP found for this task. Please provide more details or select an alternative action.",
            "options": ["Provide more details", "Select alternative action"]
        })
```

## Common Errors and Prevention Methods

### Error: Failing to Use the Clarification Tool Promptly
- **Issue**: Not using the clarification tool in a timely manner can lead to incorrect task execution.
- **Prevention**: Set trigger conditions at key decision points to ensure the clarification tool is used when necessary.

### Error: User Does Not Respond to Clarification Requests
- **Issue**: If the user does not respond to a clarification request, the task may stall.
- **Prevention**: Implement a timeout mechanism. If the user does not respond within a set time, execute a default operation or log the incident for further review.

```python
def handle_clarification_timeout():
    # Execute default operation or log the incident
    default_operation()
    log_event("User did not respond to clarification request. Default operation executed.")
```

### Error: Misinterpretation of SOPs
- **Issue**: Misinterpreting SOPs can lead to incorrect decisions and task execution.
- **Prevention**: Ensure that SOPs are clearly documented and regularly reviewed. Use automated checks to verify that the selected SOP matches the task requirements.

```python
def verify_sop_selection(sop, task_details):
    if not is_sop_valid(sop, task_details):
        return clarify_tool.prompt({
            "question": "The selected SOP may not be appropriate for this task. Please confirm or select a different SOP.",
            "options": ["Confirm", "Select different SOP"]
        })
    return execute_sop_procedure(sop, task_details)
```

## Best Practices

- **Regular SOP Review**: Regularly review and update SOPs to ensure they remain relevant and accurate.
- **User Training**: Provide training to users on how to interpret and use SOPs effectively.
- **Feedback Loop**: Implement a feedback loop to capture user experiences and improve the clarification and decision-making process.

By following these guidelines and utilizing the provided code patterns, you can ensure that tasks are clarified effectively and decisions are made based on well-defined SOPs, leading to more reliable and efficient task execution.