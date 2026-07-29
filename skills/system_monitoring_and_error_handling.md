# System Monitoring and Error Handling

## Target Skill Name: system_monitoring_and_error_handling

## Target Summary
实施全面的错误处理、日志记录以及系统健康和性能监控，确保系统稳定、高效运行，并能够快速响应和解决问题。

---

## 1. Comprehensive Error Handling and Logging

### 1.1 Overview
本节重点在于集成强大的错误处理、调试机制和日志记录模块，以保障系统稳定性并有效支持故障排除。

### 1.2 Error Handling and Debugging

#### 1.2.1 Key Code Snippets
```python
def handle_error(error: Exception) -> None:
    # 记录错误并包含详细信息
    logging.error(f'Error: {error}')
    
    # 尝试自动恢复特定错误
    if isinstance(error, FileNotFoundError):
        create_missing_file()
    elif isinstance(error, KeyError):
        add_missing_key()
    
    # 重试失败的任务
    retry_task()
```

#### 1.2.2 Common Errors and Prevention Strategies
- **Insufficient Error Handling Logic**
  - **Issue**: 错误处理逻辑未涵盖所有可能的错误类型和场景。
  - **Solution**: 设计错误处理逻辑以涵盖所有潜在错误类型和情况。使用全面的异常处理，并考虑使用集中式错误处理机制。

- **Failure to Retry After Error Recovery**
  - **Issue**: 在从错误中恢复后，未重试任务，导致操作不完整。
  - **Solution**: 确保在错误恢复后重试任务，以完成操作。实现带有适当退避策略的重试逻辑，以防止无限循环。

### 1.3 Logger Module Integration

#### 1.3.1 Key Code Snippets
```javascript
// 可配置的日志记录器示例
const logger = {
    info: (msg: string) => {
        const timestamp = new Date().toISOString();
        const line = `[${timestamp}] [INFO] ${msg}\n`;
        // 异步写入以处理文件I/O而不阻塞
        fs.promises.appendFile('app.log', line).catch(() => {
            // 如果文件写入失败，则回退到标准输出
            process.stdout.write(line);
        });
    },
    error: (msg: string) => {
        const timestamp = new Date().toISOString();
        const line = `[${timestamp}] [ERROR] ${msg}\n`;
        fs.promises.appendFile('app.log', line).catch(() => {
            process.stdout.write(line);
        });
    },
    // ... 其他日志级别
};
```

#### 1.3.2 Common Errors and Solutions
- **Incorrect File Permissions**
  - **Issue**: 日志文件或其目录权限不正确，导致应用程序无法写入日志。
  - **Solution**: 确保存储日志文件的目录具有适当的写权限。实现错误处理以优雅地处理权限相关错误。

- **Excessive Logging Impacting Performance**
  - **Issue**: 日志记录过于频繁会降低系统性能。
  - **Solution**: 根据环境调整日志级别（例如，在开发环境中使用DEBUG级别，在生产环境中使用INFO或ERROR级别）。实现异步日志记录以最小化性能影响。考虑使用日志轮换来管理日志文件大小。

### 1.4 Best Practices
1. **集中式错误处理**: 实现集中式错误处理机制，以一致地管理和响应应用程序中的错误。
2. **全面日志记录**: 使用结构化日志记录方法捕获详细且可操作的信息。包括时间戳、错误类型、堆栈跟踪和上下文数据。
3. **异步日志记录**: 为了防止日志记录成为瓶颈，使用异步日志记录机制或后台日志记录进程。
4. **日志轮换和保留**: 实现日志轮换以管理磁盘空间，并确保日志不会无限增长。根据存储限制和合规性要求定义保留策略。
5. **安全性考虑**: 保护日志文件免受未经授权的访问，因为它们可能包含敏感信息。如有必要，加密日志并仅限授权人员访问。
6. **监控和警报**: 将日志记录与监控工具集成，以设置关键错误和系统异常的警报。使用仪表板可视化日志数据并跟踪系统健康状况。

---

## 2. System Health and Performance Monitoring

### 2.1 System Efficiency Optimization

#### 2.1.1 Terminal and File Management
- **服务生命周期管理**: 使用脚本轻松启动和停止服务。
- **状态跟踪**: 监控每个服务的状态，包括进程ID（PID）和端口使用情况。
- **日志记录**: 维护详细的服务活动日志，以便调试和监控。

**关键代码片段**
```bash
start_service() {
  nohup $1 > $2 2>&1 &
  echo $! > "$PROJECT_DIR/.run/${name}.pid"
  echo "  → ${name} started (pid $!, port $port, log $log)"
}
```

**最佳实践**
- **资源管理**: 确保端口和PID得到有效管理，以防止冲突。
- **错误处理**: 提供详细的错误消息以帮助排查服务启动问题。

#### 2.1.2 Terminal Command Execution
- **执行模式**: 在终端中运行指定的命令或脚本，捕获并处理命令输出，管理执行过程中的错误。
- **关键模式**
  - **命令规范**: 明确定义要执行的命令，包括任何参数或选项。
    - 示例: `ls -la /path/to/directory`
  - **环境配置**: 设置终端环境，如设置环境变量或更改目录。
    - 示例 (Bash):
      ```bash
      export VAR_NAME=value
      cd /path/to/directory
      ```
  - **命令执行**: 执行命令并处理执行过程，包括捕获输出和错误。
    - 示例 (Python):
      ```python
      import subprocess

      try:
          result = subprocess.run(['ls', '-la', '/path/to/directory'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
          print(result.stdout)
      except subprocess.CalledProcessError as e:
          print(f"Command execution error: {e.stderr}")
      ```

**常见错误及预防**
- **无效命令或参数**: 在执行前验证命令及其参数。
- **权限不足**: 确保AI具有执行命令和访问所需资源的必要权限。
- **命令执行失败**: 实现错误处理以捕获和管理命令执行期间的异常。

#### 2.1.3 Writing Data to Files
- **文件路径规范**: 明确目标文件的存储路径和名称。
- **数据格式处理**: 根据目标文件类型选择合适的数据格式，如纯文本、JSON、Markdown等。
- **写操作**: 执行写操作，处理潜在的写错误。

**关键代码片段**
```python
try:
    with open('path/to/file.txt', 'w', encoding='utf-8') as file:
        file.write('Your data here')
except IOError as e:
    print(f"File write error: {e}")
```

**常见错误及预防**
- **文件路径不正确或权限不足**: 验证文件路径是否正确，并确保AI对目标目录具有写权限。
- **数据格式不正确**: 确保数据符合目标文件类型所需格式。
- **写操作失败**: 实现错误处理以捕获写过程中的异常。

#### 2.1.4 Combining File and Terminal Operations
- **数据处理**: 从文件中读取数据，处理数据，并根据文件内容执行命令。
- **动态命令执行**: 根据文件内容或其他动态因素生成并执行命令。

**关键代码片段**
```python
import subprocess

try:
    with open('path/to/file.txt', 'r', encoding='utf-8') as file:
        data = file.read()
    # 处理数据
    command = ['echo', data]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)
except Exception as e:
    print(f"Error: {e}")
```

**常见错误及预防**
- **文件数据与命令要求不匹配**: 确保从文件中读取的数据与正在执行的命令兼容。
- **资源泄漏**: 正确管理资源，如文件句柄和进程句柄，以防止泄漏。
- **安全漏洞**: 对所有输入和命令进行消毒和验证，以防止安全漏洞，如注入攻击。

### 2.2 System Heartbeat Check

#### 2.2.1 Overview
此微技能用于检查系统是否处于正常运行状态，并验证接收到的指令是否符合安全性和合法性要求。

#### 2.2.2 Key Code Snippets or Patterns
```python
def check_system_heartbeat(command: str) -> bool:
    # 检查指令中是否包含关键词，如 'SYSTEM_HEARTBEAT'
    if 'SYSTEM_HEARTBEAT' in command:
        return True
    return False
```

#### 2.2.3 Common Errors and Prevention
- **错误**: 误将非法指令视为合法指令。
  **预防方法**: 在验证过程中加入严格的关键词检查和上下文分析。
- **错误**: 无法识别被截断或格式错误的指令。
  **预防方法**: 在检查前对指令进行预处理，确保指令的完整性和正确性。

### 2.3 Unified Data Graph Management

#### 2.3.1 Apollo Federation Setup
##### 2.3.1.1 Purpose
利用Apollo Federation v2构建支持跨服务查询的GraphQL微服务架构。

##### 2.3.1.2 Key Code Snippets
```javascript
const { ApolloServer } = require('@apollo/server');
const { ApolloGateway, RemoteGraphQLDataSource } = require('@apollo/gateway');
const express = require('express');
const { expressMiddleware } = require('@apollo/server/express4');

const gateway = new ApolloGateway({
  serviceList: [
    { name: 'users', url: 'http://localhost:4001/graphql' },
    { name: 'products', url: 'http://localhost:4002/graphql' },