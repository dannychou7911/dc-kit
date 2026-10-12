# sc-cc-plugin

團隊共享的 Claude Code plugin 工具集，收錄經過實戰驗證的 skills、agents 與 slash commands，提升日常開發效率。

## 包含元件

### Skills

主動觸發的技能，Claude Code 會依情境自動載入，也可用 `/sc-cc-plugin:<name>` 手動呼叫。

#### 規格與文件

| 名稱 | 說明 |
|------|------|
| `spec-recovery` | 從棕地專案（brownfield）既有程式碼回推、補齊 L0-L4 規格文件，不限前後端框架或語言 |
| `create-project-instructions` | 根據 repository 已查證內容建立或重整專案級 `CLAUDE.md` / `AGENTS.md`，涵蓋架構邊界、工作流程、驗證命令與修改限制 |
| `review-project-instructions` | 審閱專案級 `AGENTS.md` / `CLAUDE.md`，判斷規則是否必要、可執行、適用範圍清楚且可驗證，並提出精簡修正建議 |
| `persist-ai-context` | 建立、審閱與操作 `.ai/` 持久化專案脈絡層，讓 handoff、follow-up 與 archive 能跨 AI agent、工具與工作階段延續 |
| `mermaid` | 依需求產生 Mermaid 圖表，支援 flowchart、sequence、class、ER、Gantt 等 23 種圖表類型 |
| `obsidian-markdown` | 建立與編輯 Obsidian Flavored Markdown（wikilinks、embeds、callouts、properties 等語法） |

#### 程式碼理解與審閱

| 名稱 | 說明 |
|------|------|
| `explain` | 解釋已鎖定範圍的程式碼（檔案、函式、diff、PR），依固定順序輸出：結論 → 資料流 → 關鍵行 → 注意點 → 可追問方向 |
| `explore` | 探索陌生或大型 codebase，建立專案結構、入口點、跨檔案功能路徑與改動影響範圍的地圖；唯讀，不修改任何檔案 |
| `code-review` | 程式碼審閱準則，以通用原則（命名、函數設計、錯誤處理、SOLID 等）加上特定語言準則進行審閱 |
| `review-comments` | 依 8 大核心原則審查程式碼註解品質（重 why 而非 what），輸出結構化審查報告、不改動程式碼 |
| `mr-review-criteria` | Merge Request 審閱回饋的評估判準與報告格式：採納程度分級、優先度分級、影響範圍檢查清單與標準報告結構 |

#### 測試與開發流程

| 名稱 | 說明 |
|------|------|
| `test-driven-development` | 以 red-green-refactor 迴圈驅動開發，適用於實作邏輯、修 bug 或變更既有行為 |
| `tdd-workflow-nestjs` | NestJS 專案的 TDD 工作流程，要求 80%+ 覆蓋率，涵蓋 unit、integration 與 E2E 測試 |
| `vue-testing-best-practices` | Vue.js 測試實務，涵蓋 Vitest、Vue Test Utils、元件測試、mocking 與 Playwright E2E |
| `sync-branch-to-develop` | 在同時維護 main 與 develop 兩條長期線的專案，以 cherry-pick 把開發分支搬到另一條線的同名分支，並用 `range-diff` 驗證一致 |
| `git-worktree` | 互動式建立、列出、刪除 git worktree 與本地分支，每個決策點逐一詢問並確認指令後才執行；僅限手動觸發 `/git-worktree` |

#### 框架與語言慣例

| 名稱 | 說明 |
|------|------|
| `vue-pattern` | Vue 官方 Style Guide 規則知識庫，涵蓋 Priority A–D 共 26 條規則，Composition API 與 Options API 範例並陳 |
| `shadcn-vue` | shadcn-vue 於 Vue / Nuxt 的使用方式，涵蓋 Reka UI 元件、Tailwind、Auto Form、data table、dark mode |
| `tailwind-patterns` | Tailwind CSS 常見元件模式（responsive layout、card、navigation、form、button、typography），含 mobile-first 與 dark mode |
| `java-coding-standards` | Spring Boot 與 Quarkus 的 Java 17+ 編碼標準，依 build file 自動偵測框架並套用對應慣例 |
| `postgres-patterns` | PostgreSQL 查詢優化、schema 設計、索引與安全性模式，基於 Supabase 最佳實務 |
| `prisma-expert` | Prisma ORM 的 schema 設計、migration、關聯建模與查詢優化 |

#### 工作階段輔助

| 名稱 | 說明 |
|------|------|
| `strategic-compact` | 在邏輯斷點建議手動 context compaction，避免 auto-compaction 在不恰當時機觸發 |
| `i-have-adhd` | ADHD 友善的輸出格式：先講下一步、多步驟編號、跨輪重述狀態、抑制離題。以 `/i-have-adhd` 開啟，說「stop adhd mode」關閉 |

### Agents

專責的子代理，可用 `@` 呼叫或由主 agent 主動委派。

| 名稱 | 說明 |
|------|------|
| `frontend-code-reviewer` | 通用程式碼審閱專家，聚焦可讀性、可維護性、安全性與專案慣例，不限框架，僅回報高信心度（>80%）的問題。框架專屬規則由 `references/` 擴充補充 |
| `spec-scorer` | 規格文件品質評分專家，獨立審閱 `spec-recovery` 產出的 L0-L4 文件（A 多維度評分、B 可測試性評分），與主 agent 分離以避免 confirmation bias |
| `spec-verifier` | 規格文件差異驗證專家（C 評分），獨立重讀原始碼盤點行為、比對規格覆蓋率並列出遺漏；繼承 session model 以確保盤點偵測力 |

### Slash Commands

| 指令 | 參數 | 說明 |
|------|------|------|
| `/code-review-cmd` | `<spec-path>` | 以資深前端工程師角度審閱 Vue 2 / Nuxt 2 / JavaScript 程式碼，依提供的功能規格比對實作 |
| `/commit` | `[message] \| --amend` | 使用 conventional commit 格式建立格式良好的 commit，預設不使用 emoji |
| `/review-mr` | `<project-path> <mr-number>` | 分析指定專案 MR 的所有審閱回饋，驗證後產出修正計畫 |
| `/rewrite-comments` | `[file-path]` | 改寫程式碼註解，著重 why 而非 what；冗餘者刪除、過期者修正、推斷不出意圖者標記請人補 |
| `/squash-branch` | `[base-branch]` | 將目前分支自基準分支分歧後的所有 commits 合併為單一 commit，執行前先建立備份分支 |

### MCP Servers

由 `.mcp.json` 定義，安裝 plugin 後自動註冊。

| 名稱 | 啟動方式 | 說明 |
|------|----------|------|
| `chrome-devtools` | `npx -y chrome-devtools-mcp@latest` | 讓 Claude Code 透過 [Chrome DevTools Protocol](https://github.com/ChromeDevTools/chrome-devtools-mcp) 操作瀏覽器：開頁面、擷取畫面、讀取 console 與 network、效能追蹤 |

前置需求：本機需有 Node.js（提供 `npx`）與 Chrome。首次啟動會下載 `chrome-devtools-mcp` 套件，需要網路連線。

## 安裝方式

### 本地測試

```bash
claude --plugin-dir /path/to/sc-cc-plugin
```

### 驗證安裝

啟動 Claude Code 後：

- 輸入 `/`，確認看到帶有 `(sc-cc-plugin)` 標籤的 `/code-review-cmd`、`/commit`、`/review-mr`、`/rewrite-comments`、`/squash-branch`
- 輸入 `@`，確認看到 `frontend-code-reviewer`、`spec-scorer`、`spec-verifier` 三個 agent
- 輸入 `/spec`，確認 skills（如 `/sc-cc-plugin:spec-recovery`）出現在清單中

## 使用範例

```bash
# 回推整個專案規格（skill 亦會在相關語境中自動觸發）
/spec-recovery

# 回推單一模組
/spec-recovery src/modules/auth

# 建立 conventional commit
/commit

# 分析某專案的 MR 回饋並產出修正計畫
/review-mr ~/Project/my-app 486

# 將目前分支的多個 commits 壓成一個（先建立備份分支）
/squash-branch main
```

## 需求

- Claude Code >= 1.0.33
- Node.js 與 Chrome（`chrome-devtools` MCP server 使用，見上方 MCP Servers 一節）

## 來源與致謝

- [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)：`chrome-devtools` MCP server 的實作來源
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/main)：部分 skill 的參考與改寫來源
