# Next.js 全棧無服務器應用程序開發指南

## 概述
本指南旨在幫助開發者使用 Next.js 和 React 構建全棧無服務器應用程序，同時利用 TypeScript 進行優化和組件化開發。通過嚴格的 TypeScript 配置、API 路由的實現以及服務器端渲染（SSR）的優化，開發者可以創建高效、可維護且安全的應用程序。

## 1. 嚴格的 TypeScript 配置

### 配置詳解
在 Next.js 項目中強制執行嚴格的 TypeScript 規則，以在開發過程中捕捉潛在的類型相關錯誤。

```json
// tsconfig.json
{
  "strict": true,
  "noEmit": true,
  "compilerOptions": {
    // 其他編譯器選項可在此處添加
  }
}
```

- **`strict`**: 啟用所有嚴格的類型檢查選項。
- **`noEmit`**: 防止 TypeScript 發出編譯輸出，依賴 Next.js 進行打包。

### 最佳實踐
- **文件擴展名**: 使用 `.tsx` 來包含 JSX 的文件，使用 `.ts` 來包含其他 TypeScript 文件。
- **類型共享**: 使用 `@/lib/data` 目錄和 `import type` 來在服務器和客戶端之間共享類型，確保零成本的類型導入。

### 常見錯誤及預防方法
- **錯誤**: 忘記在 `tsconfig.json` 中啟用嚴格模式。
  - **預防方法**: 始終設置 `"strict": true`，並監控構建過程中的類型錯誤。
- **錯誤**: 不一致的類型定義導致導入問題。
  - **預防方法**: 使用 `import type` 進行類型導入，並在共享目錄中保持一致的類型定義。

## 2. 在 Next.js 中實現 API 路由

### 概述
在 Next.js 應用程序中創建後端端點，以處理各種 HTTP 請求。

### 關鍵代碼片段
```tsx
// pages/api/health.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const status = searchParams.get("status");
  const role = searchParams.get("role");
  // ... 其他邏輯
  return NextResponse.json({ /* 響應數據 */ }, { status: 200 });
}

// pages/api/users.ts
export async function POST(request: Request) {
  let body: CreateUserPayload = {};
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "無效的 JSON 主體" }, { status: 400 });
  }
  // ... 其他邏輯，例如創建用戶
  return NextResponse.json({ ok: true, user: created, note: "僅回顯 — 在此演示中未持久化" }, { status: 201 });
}
```

### 最佳實踐
- **錯誤處理**: 始終使用 try-catch 塊來處理異常，例如 JSON 解析失敗。
- **輸入驗證**: 驗證並清理所有傳入的數據，以防止安全漏洞。

### 常見錯誤及預防方法
- **錯誤**: 不處理異常，導致意外崩潰。
  - **預防方法**: 使用 try-catch 塊實現全面的錯誤處理，並返回有意義的錯誤消息。
- **錯誤**: 缺乏輸入驗證，導致潛在的安全問題。
  - **預防方法**: 實施強大的驗證規則，並在處理之前清理所有用戶輸入。

## 3. 優化 Next.js 中的服務器端渲染（SSR）

### 概述
利用 SSR 在服務器上渲染頁面，以提高初始加載時間和 SEO 性能。此外，利用 React 服務器組件（RSC）來減少客戶端 JavaScript 負載。

### 關鍵代碼片段
```tsx
// pages/index.tsx
export default function Home() {
  return (
    <div>
      {/* 頁面內容 */}
    </div>
  );
}

// components/ServerComponent.tsx
"use server";
import { /* 導入 */ } from "...";

const ServerComponent = () => {
  // 僅服務器的邏輯
  return <div>服務器組件</div>;
};

export default ServerComponent;
```

### 最佳實踐
- **選擇性 SSR**: 僅對需要 SEO 或需要在服務器上渲染的頁面使用 SSR。對於靜態內容，考慮使用靜態站點生成（SSG）來緩存頁面並減少服務器負載。
- **React 服務器組件**: 通過在頂部添加 `"use server";` 來標記不需要客戶端交互的組件為 RSC。這確保它們在服務器上渲染，並且不會增加客戶端包大小。

### 常見錯誤及預防方法
- **錯誤**: 過度使用 SSR，導致服務器負載增加和潛在的性能瓶頸。
  - **預防方法**: 分析哪些頁面從 SSR 中受益，並對靜態內容使用 SSG 以平衡性能和服務器負載。
- **錯誤**: 不正確地使用 RSC，導致不必要的客戶端 JavaScript。
  - **預防方法**: 通過使用 `"use client";` 來區分服務器和客戶端組件，確保互動組件被正確標記。

## 4. Next.js 應用中的組件組織

### 概述
在 Next.js 應用中，組件被組織在 `src/components/` 目錄下。默認情況下，服務器端渲染的組件優先，只有需要互動的部分才標記為 `use client`。

### 關鍵代碼片段
```tsx
// 示例的服務器優先組件
const Navbar = () => {
  return <nav>...</nav>;
};

export default Navbar;

// 示例的客戶端組件
"use client";
import { useState } from "react";

const ThemeToggle = () => {
  const [theme, setTheme] = useState("light");
  // ...
};

export default ThemeToggle;
```

### 常見錯誤及避免方法
- **錯誤**: 將不需要互動的組件標記為 `use client`，導致性能下降。
  **避免方法**: 僅在需要使用瀏覽器 API 或狀態管理的組件中使用 `use client`。
- **錯誤**: 組件之間的類型定義不一致，導致類型錯誤。
  **避免方法**: 使用 TypeScript 並在共享的 `@/lib/data` 目錄中定義類型。

## 結論
通過遵循本指南，您可以有效地配置強大的 TypeScript 設置，實現安全高效的 API 路由，並優化 SSR 以提升應用程序的性能。堅持這些實踐將有助於創建一個更易於維護、性能更優且更安全的代碼庫。