# 後端 / Node.js 審閱規則（Backend / Node.js Patterns）

> 本檔自 `agents/frontend-code-reviewer.md` 抽離，收錄 Node.js / 後端的框架專屬審閱規則。
> 審閱變更含 Node.js 後端程式碼時，`frontend-code-reviewer` agent 會在執行階段讀取本檔並套用。

## Node.js / Backend Patterns (HIGH)

審閱後端程式碼時：

- **未驗證的輸入** — request body/params 未經 schema 驗證就使用
- **缺少 rate limiting** — 公開 endpoint 沒有節流
- **無上限查詢** — 對外 endpoint 使用 `SELECT *` 或沒有 LIMIT 的查詢
- **N+1 查詢** — 在迴圈內逐筆撈關聯資料，而非用 join/批次
- **缺少逾時** — 外部 HTTP 呼叫沒有設定 timeout
- **錯誤訊息外洩** — 把內部錯誤細節回傳給 client
- **缺少 CORS 設定** — API 可被非預期來源存取
```typescript
// BAD: N+1 query pattern
const users = await db.query('SELECT * FROM users');
for (const user of users) {
  user.posts = await db.query('SELECT * FROM posts WHERE user_id = $1', [user.id]);
}

// GOOD: Single query with JOIN or batch
const usersWithPosts = await db.query(`
  SELECT u.*, json_agg(p.*) as posts
  FROM users u
  LEFT JOIN posts p ON p.user_id = u.id
  GROUP BY u.id
`);
```
