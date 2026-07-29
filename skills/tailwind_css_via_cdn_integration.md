# Tailwind CSS via CDN Integration

## 目的
快速集成 Tailwind CSS 到 HTML 文件中，无需构建工具或本地安装。

## 关键代码模式
```html
<link href="https://cdn.tailwindcss.com" rel="stylesheet">
<script>
    tailwind.config = {
        theme: {
            extend: {
                colors: {
                    // 自定义颜色
                }
            }
        }
    };
</script>
```

## 常见错误及避免方法
- **错误**：CDN 链接错误或不可用，导致样式无法加载。
  **避免方法**：使用可靠的 CDN 服务，并设置备用链接。
- **错误**：Tailwind 配置不正确，导致样式应用错误。
  **避免方法**：参考官方文档，确保配置语法正确，并进行测试验证。