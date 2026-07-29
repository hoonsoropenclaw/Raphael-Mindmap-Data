# Cross Service Entity Resolution

## 目的
在 Apollo Federation 中实现跨服务的实体解析，例如在用户服务中引用产品服务的数据。

## 关键代码片段
```javascript
// 在 products-service 中定义 User 的 resolver
User: {
  favoriteProducts: (ref) => products.filter(p => p.ownerUserId === ref.id),
},

// 在 users-service 中定义 Product 的 stub
type Product @key(fields: "id") {
  id: ID!
}
```

## 常见错误及避免方法
- **错误**: 跨服务引用的类型未在本地定义，导致 schema 构建失败。
  **解决方法**: 在引用类型的服务中定义一个 stub，例如 `type Product @key(fields: "id") { id: ID! }`，只包含 federation key，不包含其他字段。
- **错误**: 同一个字段在多个子图中定义，导致数据来源不明确。
  **解决方法**: entity 字段只在一个子图中定义，其他子图只包含 key-only stub。例如，`User.favoriteProducts` 的 resolver 只在 products-service 中实现，users-service 只包含 `User { id }` stub。