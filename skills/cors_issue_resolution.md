# CORS Issue Resolution

## 说明
解决由于跨域资源共享策略导致的请求被阻止的问题。

## 关键代码片段或模式
```javascript
// 在服务器端设置 CORS 头
const express = require('express');
const app = express();
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});
```

## 常见错误及避免方法
- **服务器未正确配置 CORS**：确保服务器设置了适当的 CORS 头。
- **使用 CDN 时 CORS 问题**：选择支持 CORS 的 CDN，或使用代理服务器。
```bash
# 使用 jsDelivr 作为 CDN
https://cdn.jsdelivr.net/npm/reactflow@11.11.4/dist/umd/index.min.js
```