# Next.js 全栈功能：高级特性与动态路由

## 动态路由

### 概述
动态路由是 Next.js 的核心功能之一，允许根据不同的 URL 路径动态加载和显示内容。这对于构建多页面应用至关重要，能够提升用户体验和应用的灵活性。

### 配置与实现

#### 使用 App Router 实现动态路由
在 Next.js 的 App Router 中，可以通过在 `app` 目录下创建带方括号的文件夹名称来定义动态路由。例如，`app/articles/[id]/page.tsx` 定义了一个动态路由，其中 `[id]` 是一个动态参数。

```javascript
// app/articles/[id]/page.tsx
import { useRouter } from 'next/router';

export default function ArticlePage() {
  const router = useRouter();
  const { id } = router.query;

  return <div>Article ID: {id}</div>;
}
```

- **解释**：通过 `useRouter` 钩子获取 URL 中的动态参数 `id`，并将其显示在页面上。

### 常见错误与解决方法

#### 动态路由未正确解析
- **症状**：页面无法显示内容。
- **解决方法**：确保在 `app` 目录下的动态路由文件使用正确的命名约定，例如 `[id]`。同时，在页面组件中通过 `useRouter` 获取动态参数：
  ```javascript
  const { id } = router.query;
  ```

#### 正则匹配失败
- **症状**：动态路由无法匹配预期的 URL。
- **解决方法**：检查路由配置中的正则表达式是否正确，并确保 URL 包含必要的参数。例如：
  ```javascript
  // 正确示例: /articles/123
  // 错误示例: /articles
  ```

### 高级功能

#### 使用 `useParams` 提取动态参数
`useParams` 可以用于提取动态路由中的参数：
```javascript
import { useParams } from 'next/navigation';

const { id } = useParams();
```

#### 使用 `useSearchParams` 处理查询参数
`useSearchParams` 可以用于处理 URL 中的查询参数：
```javascript
import { useSearchParams } from 'next/navigation';

const [searchParams] = useSearchParams();
const query = searchParams.get('query');
```

#### 使用 `generateStaticParams` 生成静态路由
`generateStaticParams` 可以用于在构建时生成静态路由：
```javascript
export async function generateStaticParams() {
  const articles = await fetch('/api/articles').then(res => res.json());
  return articles.map(article => ({ id: article.id }));
}
```

## 单文件 SPA 模拟

### 概述
单文件 SPA 模拟是指在单个 HTML 文件中嵌入所有必要的 JavaScript、CSS 和 HTML，以创建一个功能完整的单页应用。这种方法适用于简单的应用或原型开发，能够减少服务器请求并提供更快的加载速度。

### 实现示例

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>单页应用 Demo</title>
  <style>
    /* CSS 样式 */
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin-top: 50px;
    }
    h1 {
      color: #333;
    }
  </style>
</head>
<body>
  <div id="app"></div>

  <script>
    // JavaScript 代码
    function render() {
      document.getElementById('app').innerHTML = '<h1>Hello, World!</h1>';
    }
    render();
  </script>
</body>
</html>
```

- **解释**：在单个 HTML 文件中包含基本的 HTML 结构、内嵌的 CSS 样式和 JavaScript 代码，实现一个简单的 SPA。

### 常见错误与解决方法

#### JavaScript 语法错误
- **症状**：页面无法正常渲染。
- **解决方法**：使用浏览器的开发者工具检查控制台错误，并修正相应的 JavaScript 代码。例如，确保所有括号和引号都正确配对：
  ```javascript
  // 错误示例: document.getElementById('app'.innerHTML = '<h1>Hello, World!</h1>';
  // 正确示例: document.getElementById('app').innerHTML = '<h1>Hello, World!</h1>';
  ```

#### CSS 样式应用错误
- **症状**：页面布局混乱。
- **解决方法**：检查 CSS 代码，确保选择器和属性正确，并且样式被正确引用。例如，确保 CSS 选择器与 HTML 元素匹配：
  ```css
  /* 错误示例: .app { ... } */
  /* 正确示例: #app { ... } */
  ```
  - 确保 CSS 样式在 `<style>` 标签内正确书写，并且没有拼写错误。

## 总结
通过掌握 Next.js 的动态路由和单文件 SPA 模拟，您可以在构建现代 Web 应用时实现更灵活和高效的页面导航和内容渲染。确保在配置动态路由时遵循正确的命名约定，并在单文件 SPA 中正确编写和引用 CSS 和 JavaScript 代码，以避免常见的错误。