# Apollo Federation Setup

## 目的
使用 Apollo Federation v2 搭建一个支持跨服务查询的 GraphQL 微服务架构。

## 关键代码片段
```javascript
const { ApolloServer } = require('@apollo/server');
const { ApolloGateway, RemoteGraphQLDataSource } = require('@apollo/gateway');
const express = require('express');
const { expressMiddleware } = require('@apollo/server/express4');

const gateway = new ApolloGateway({
  serviceList: [
    { name: 'users', url: 'http://localhost:4001/graphql' },
    { name: 'products', url: 'http://localhost:4002/graphql' },
  ],
});

const server = new ApolloServer({
  gateway,
});

await server.start();
const app = express();
app.use('/graphql', expressMiddleware(server));
```

## 常见错误及避免方法
- **错误**: `@apollo/server/plugin/disabled` 是 ESM-only 包，在 CommonJS 环境中导入会报错。
  **解决方法**: 在使用 Apollo Server v4 和 CommonJS 时，不要导入 usage-reporting 插件，直接省略即可。
- **错误**: `@link` 指令冲突导致 composition 失败。
  **解决方法**: 使用正确的 `@link` 指令写法，例如 `@link(url: "https://specs.apollo.dev/federation/v2.5", import: ["@key"])`。