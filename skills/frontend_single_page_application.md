# Frontend Single Page Application

## 目的
构建一个单页前端应用，通过 Apollo Gateway 发送 GraphQL 查询，验证跨服务查询的正确性。

## 关键代码片段
```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <title>GraphQL Federation Demo — Gateway :4000</title>
  <style>/* 样式代码 */</style>
</head>
<body>
  <h1>🔗 GraphQL Federation Demo</h1>
  <p>前端单档 HTML → 打到 <strong>Gateway :4000</strong>(Apollo Federation) → query plan 拆 sub-query → 两个 subgraph(:4001 users / :4002 products)並行。</p>
  <!-- 其他 HTML 代码 -->
</body>
</html>
```

## 常见错误及避免方法
- **错误**: 前端请求未正确设置 `x-user-id` header，导致跨服务查询失败。
  **解决方法**: 在前端代码中正确设置 `x-user-id` header，例如 `x-user-id: u1`。
- **错误**: 前端未处理跨域问题。
  **解决方法**: 在 Apollo Gateway 中配置 CORS，例如使用 `cors` 中间件。