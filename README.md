# dc-kit

個人使用、可自由分享的 Claude Code plugin 工具集，收錄經過實戰驗證的 skills、agents 與 slash commands，提升日常開發效率。

## 包含元件

### Skills

主動觸發的技能，Claude Code 會依情境自動載入，也可用 `/dc-kit:<name>` 手動呼叫。

#### 規格與文件

| 名稱 | 說明 |
|------|------|
| `spec-recovery` | 從棕地專案（brownfield）既有程式碼回推、補齊 L0-L4 規格文件，不限前後端框架或語言 |
| `create-project-instructions` | 根據 repository 已查證內容建立或重整專案級 `CLAUDE.md` / `AGENTS.md`，涵蓋架構邊界、工作流程、驗證命令與修改限制 |
| `review-project-instructions` | 審閱專案級 `AGENTS.md` / `CLAUDE.md`，判斷規則是否必要、可執行、適用範圍清楚且可驗證，並提出精簡修正建議 |
| `persist-ai-context` | 建立、審閱與操作 `.ai/` 持久化專案脈絡層，讓 handoff、follow-up 與 archive 能跨 AI agent、工具與工作階段延續 |
| `mermaid` | 依需求產生 Mermaid 圖表，支援 flowchart、sequence、class、ER、Gantt 等 23 種圖表類型 |
| `obsidian-markdown` | 建立與編輯 Obsidian Flavored Markdown（wikilinks、embeds、callouts、properties 等語法） |
| `site-reference` | 擷取指定網站各頁的 Desktop / Mobile 截圖、版面區塊、功能清單與 design token，產出可直接開啟的單檔 HTML 參考報告；需要 `chrome-devtools` MCP 與 `python3` |

#### 程式碼理解與審閱

| 名稱 | 說明 |
|------|------|
| `explain` | 解釋已鎖定範圍的程式碼（檔案、函式、diff、PR），依固定順序輸出：結論 → 資料流 → 關鍵行 → 注意點 → 可追問方向 |
| `explore` | 探索陌生或大型 codebase，建立專案結構、入口點、跨檔案功能路徑與改動影響範圍的地圖；唯讀，不修改任何檔案 |
| `code-review` | 程式碼審閱準則，以通用原則（命名、函數設計、錯誤處理、SOLID 等）加上特定語言準則進行審閱 |
| `review-comments` | 依 8 大核心原則審查程式碼註解品質（重 why 而非 what），輸出結構化審查報告、不改動程式碼 |
| `mr-review-criteria` | Merge Request 審閱回饋的評估判準與報告格式：採納程度分級、優先度分級、影響範圍檢查清單與標準報告結構 |
| `code-review-and-quality` | 合併前的多面向程式碼審閱，適用自己、其他 agent 或他人寫的變更，附效能與安全性 checklist |
| `mr-review-reply` | 將已完成的審閱結果整理成語氣客氣、結構固定的留言，透過 GitLab MCP 發佈到指定 MR |

#### 測試與開發流程

| 名稱 | 說明 |
|------|------|
| `test-driven-development` | 以 red-green-refactor 迴圈驅動開發，適用於實作邏輯、修 bug 或變更既有行為 |
| `tdd-workflow-nestjs` | NestJS 專案的 TDD 工作流程，要求 80%+ 覆蓋率，涵蓋 unit、integration 與 E2E 測試 |
| `vue-testing-best-practices` | Vue.js 測試實務，涵蓋 Vitest、Vue Test Utils、元件測試、mocking 與 Playwright E2E |
| `sync-branch-to-develop` | 在同時維護 main 與 develop 兩條長期線的專案，以 cherry-pick 把開發分支搬到另一條線的同名分支，並用 `range-diff` 驗證一致 |
| `git-worktree` | 互動式建立、列出、刪除 git worktree 與本地分支，每個決策點逐一詢問並確認指令後才執行；僅限手動觸發 `/git-worktree` |
| `playwright-cli` | 以 Playwright 自動化瀏覽器操作、測試網頁與撰寫 Playwright 測試，涵蓋 request mocking、storage state、tracing 與錄影 |

#### 瀏覽器除錯與效能

以下 skill 皆透過 `chrome-devtools` MCP 操作瀏覽器（見下方 MCP Servers 一節）。

| 名稱 | 說明 |
|------|------|
| `chrome-devtools` | 透過 Chrome DevTools MCP 除錯網頁、自動化瀏覽器互動、分析效能與檢查 network request |
| `troubleshooting` | `list_pages`、`new_page`、`navigate_page` 失敗或 MCP server 初始化失敗時，排查連線與 target 問題 |
| `a11y-debugging` | 依 web.dev 準則稽核無障礙：語意化 HTML、ARIA label、focus 狀態、鍵盤操作、點擊區域與色彩對比 |
| `cookie-debugging` | 檢查 cookie 與 session 狀態，診斷 401/403、驗證重導、session 過期、SameSite / Partitioned cookie 與 cookie consent 合規 |
| `debug-optimize-lcp` | 拆解與優化 Largest Contentful Paint（LCP），找出主要內容延遲出現的原因 |
| `memory-leak-debugging` | 以 heap snapshot 擷取、比對與檢查，診斷 JavaScript / Node.js 的記憶體洩漏與 OOM |

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
| `chrome-devtools` | `npx -y chrome-devtools-mcp@latest --isolated` | 讓 Claude Code 透過 [Chrome DevTools Protocol](https://github.com/ChromeDevTools/chrome-devtools-mcp) 操作瀏覽器：開頁面、擷取畫面、讀取 console 與 network、效能追蹤 |

前置需求：本機需有 Node.js（提供 `npx`）與 Chrome。首次啟動會下載 `chrome-devtools-mcp` 套件，需要網路連線。

`--isolated` 讓每個 MCP 實例使用暫存的 Chrome profile，瀏覽器關閉後自動刪除，因此多個 Claude Code session 可以同時使用，不會因共用 profile 而無法開啟瀏覽器。代價是 cookie 與登入狀態不會跨 session 保留。

### LSP Servers

由 `.lsp.json` 定義，安裝 plugin 後自動註冊，讓 Claude Code 在編輯 `.vue` 檔時取得型別錯誤、跳至定義、查找引用等 code intelligence。

| 名稱 | 啟動方式 | 適用檔案 |
|------|----------|----------|
| `vue` | `vue-language-server --stdio` | `.vue` |

前置需求：plugin 不會替你安裝 language server，需自行全域安裝並確認 `vue-language-server` 在 `PATH` 中：

```bash
npm install -g @vue/language-server
```

型別資訊取自專案內的 `node_modules/typescript/lib`，因此專案需已安裝 `typescript`。

## 安裝方式

### 從 marketplace 安裝

```
/plugin marketplace add dannychou7911/dc-kit
/plugin install dc-kit@dc-tools
```

### 更新

`dc-tools` 屬於第三方 marketplace，Claude Code 預設**不會**自動更新，也不會主動通知有新版。可擇一方式更新：

- 在 Claude Code 內執行 `/plugin`，進入 Installed，選 `dc-kit` 後按 **Update now**
- 在 Claude Code 內執行 `/plugin`，進入 Marketplaces，選 `dc-tools` 後按 **Update marketplace**（會一併更新已安裝的 plugin）
- 在 shell 執行：

  ```bash
  claude plugin update dc-kit@dc-tools
  ```

若想自動更新，在 `/plugin` → Marketplaces → `dc-tools` 選 **Enable auto-update**。開啟後，Claude Code 會在 session 開始後於背景更新，畫面顯示 `Plugin updated: dc-kit · Run /reload-plugins to apply`。

更新完成後，執行中的 session 仍使用舊版。執行 `/reload-plugins` 或重新啟動 Claude Code 後才會載入新版。

> 維護者注意：Claude Code 以 `plugin.json` 的 `version` 判斷是否有新版。版本號沒變時，即使 push 了新 commit，使用者也拿不到更新，因此每次發佈都要依下方「版本規則」調升版本號。

### 在專案中預先啟用

在專案的 `.claude/settings.json` 加入下列設定並 commit，成員信任該資料夾後即會自動註冊 marketplace 並啟用 plugin：

```json
{
  "extraKnownMarketplaces": {
    "dc-tools": { "source": { "source": "github", "repo": "dannychou7911/dc-kit" } }
  },
  "enabledPlugins": { "dc-kit@dc-tools": true }
}
```

### 本地測試

```bash
claude --plugin-dir /path/to/dc-kit
```

### 驗證安裝

啟動 Claude Code 後：

- 輸入 `/`，確認看到帶有 `(dc-kit)` 標籤的 `/code-review-cmd`、`/commit`、`/review-mr`、`/rewrite-comments`、`/squash-branch`
- 輸入 `@`，確認看到 `frontend-code-reviewer`、`spec-scorer`、`spec-verifier` 三個 agent
- 輸入 `/spec`，確認 skills（如 `/dc-kit:spec-recovery`）出現在清單中

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

## 版本規則

發佈前調升 `.claude-plugin/plugin.json` 的 `version`，依自上次發佈以來的變更取最高等級：

| 變更類型 | 調升位數 | 範例 |
|----------|----------|------|
| 修正既有技能 | 第三碼（patch） | `1.0.0` → `1.0.1` |
| 新增或移除技能 | 第二碼（minor） | `1.0.1` → `1.1.0` |
| 前後內容不相容 | 首碼（major） | `1.1.0` → `2.0.0` |

調升較高位數時，較低位數歸零。版本調升以獨立的 `chore: 發佈 x.y.z 版本` commit 提交。

## 需求

- Claude Code >= 1.0.33
- Node.js 與 Chrome（`chrome-devtools` MCP server 使用，見上方 MCP Servers 一節）
- `@vue/language-server`（`vue` LSP server 使用，需全域安裝，見上方 LSP Servers 一節）
- `python3`（`site-reference` skill 產生報告與示意圖使用；拼接、裁切截圖時另需 Pillow，可選）

## 來源與致謝

- [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)：`chrome-devtools` MCP server 的實作來源
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/main)：部分 skill 的參考與改寫來源
