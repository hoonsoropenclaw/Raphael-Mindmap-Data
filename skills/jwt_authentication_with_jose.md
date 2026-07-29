# JWT Authentication with Jose

## 說明
此技能涉及使用 `jose` 庫在 Next.js 中實現 JWT 身份驗證，包括生成和驗證 JWT token。

## 關鍵代碼片段
```typescript
import { SignJWT, jwtVerify } from "jose";

const SECRET = new TextEncoder().encode(process.env.PORTAL_JWT_SECRET ?? "dev-secret-change-me-in-production-min-32-chars");

export async function login(username: string, password: string): Promise<string | null> {
  // 驗證用戶邏輯
  const token = await new SignJWT({ username })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(SECRET);
  return token;
}

export async function verify(token: string): Promise<{ username: string } | null> {
  try {
    const { payload } = await jwtVerify(token, SECRET);
    return payload as { username: string };
  } catch (e) {
    return null;
  }
}
```

## 常見錯誤及避免方法
- **錯誤**：secret 未正確設置或洩露。
  **解決方法**：確保 `PORTAL_JWT_SECRET` 設置為強隨機值，並且不將其提交到版本控制系統。
- **錯誤**：token 過期時間設置過長或過短。
  **解決方法**：根據應用程序需求設置合理的過期時間，並考慮實現刷新 token 機制。