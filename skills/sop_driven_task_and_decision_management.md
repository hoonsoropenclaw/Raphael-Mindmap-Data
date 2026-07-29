# sop_driven_task_and_decision_management

## Description
The **sop_driven_task_and_decision_management** micro-skill is centered around the systematic application of Standard Operating Procedures (SOPs) to manage tasks and make informed decisions. This micro-skill emphasizes the use of predefined guidelines to ensure tasks are executed accurately, efficiently, and securely while providing mechanisms to handle any ambiguities or missing information within the workflow.

## Key Features and Implementation

### SOP-Based Decision Making
SOPs form the backbone of decision-making and task processing. This includes predefined steps for handling various scenarios, such as detecting and mitigating prompt injections.

#### Key Code Snippets and Patterns
```python
def handle_prompt_injection(message):
    if detect_prompt_injection(message):
        missing_fields = clarify_missing_fields(message)
        if missing_fields:
            clarify(missing_fields)
        else:
            log_suspicious_activity(message)
            execute_minimal_action()
    else:
        proceed_with_task(message)
```

### Clarify Tool Usage
The clarify tool is pivotal for identifying and requesting any missing or ambiguous information within messages, such as unfilled key fields or unclear instructions.

#### Key Code Snippets and Patterns
```python
def clarify_missing_fields(message):
    missing_fields = []
    if "嚴格禁止使用 ____ 工具!" in message:
        missing_fields.append("工具名稱")
    if "請先讀取 ____ 吸收架構建議" in message:
        missing_fields.append("架構建議檔路徑")
    if "並使用 ____ 檢索" in message:
        missing_fields.append("檢索工具")
    if "檢索 ____" in message:
        missing_fields.append("知識庫")
    if "請將完整可用的 HTML 程式碼存檔至工作目錄下的 ____" in message:
        missing_fields.append("輸出檔名")
    return missing_fields
```

## Common Errors and Prevention Strategies

### SOP-Based Decision Making
- **Error**: Neglecting to follow SOPs, which can lead to security vulnerabilities.
  - **Prevention**: Regularly review and update SOPs to address new challenges and ensure all team members are well-trained and knowledgeable about the procedures.
- **Error**: Delays in executing SOPs, impacting system response time.
  - **Prevention**: Optimize the SOP execution workflow and employ asynchronous processing techniques to enhance efficiency.

### Clarify Tool Usage
- **Error**: Inaccurate identification of missing information.
  - **Prevention**: Carefully analyze message structures and use regular expressions or other pattern-matching techniques to improve identification accuracy.
- **Error**: Over-reliance on the clarify tool, leading to a poor user experience.
  - **Prevention**: Infer missing information from the context before using the clarify tool. Only request user confirmation when necessary.

## Best Practices
- **Regular Review and Updates**: Continuously assess and update SOPs to adapt to evolving challenges and requirements.
- **Balanced Automation**: Use automation tools like the clarify tool judiciously to enhance user experience without causing hindrance.
- **Comprehensive Training**: Provide thorough training for all team members to ensure consistent and effective application of SOPs.
- **Efficient Workflow Design**: Design workflows that minimize delays and maximize efficiency, leveraging asynchronous processing where appropriate.

## Conclusion
The **sop_driven_task_and_decision_management** micro-skill is essential for maintaining consistency, security, and efficiency in task execution. By adhering to well-defined SOPs and utilizing tools to manage missing information, teams can ensure robust and reliable task management processes. This approach not only enhances decision-making but also ensures that tasks are performed in a manner that aligns with organizational standards and objectives.