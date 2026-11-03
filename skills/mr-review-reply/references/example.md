# 留言範例

兩則範例取材自同一個 MR 的兩輪審閱，內容已縮短。重點看結構、編號與語氣，不必照抄措辭。

## 目錄

- 範例一：第一輪
- 範例二：第二輪（含上一輪項目追蹤、編號接續）

兩則都附「等級說明與處理方式」表，每一輪都要附。

---

## 範例一：第一輪

```markdown
## OpenSpec verify 結果：`add-postmessage-jwt-token`

辛苦了，以下整理這次 verify 的結果供參考。整體沒有 CRITICAL，主要是幾處文件沒跟上實作，以及部分 scenario 缺少直接的測試。

### 審閱方式
- **範圍**：HEAD `441e3e9`（與本 MR 目前的 head 相同）；比對 `openspec/changes/add-postmessage-jwt-token/` 的 proposal、design、delta specs 與 tasks
- **方法**：以 Claude Code 與 Codex CLI 各執行一次 `openspec verify`，交叉比對後整理；每一項都回到程式碼與 spec 實際查證
- **實際執行的驗證**：
  - `vitest --run`：7 files / 104 tests 全部通過
  - `vue-tsc --build`：exit 0
  - `openspec validate add-postmessage-jwt-token`：valid

### 結論
0 CRITICAL、3 WARNING、4 SUGGESTION。11 個 requirements 都有對應實作，65/65 tasks 完成，設計決策 D1–D9 均已遵循。

### 等級說明與處理方式
| 等級 | 意義 | 建議採取的方案 | 本次項目 |
|---|---|---|---|
| **CRITICAL** | 會造成功能錯誤、安全或資料問題；或 requirement 未實作、task 未完成 | 建議合併前修正 | 無 |
| **WARNING** | 規格或設計與實作不一致、缺少測試證據，或特定情境下可能出錯 | 建議 archive 前處理；需要延後時，請在 MR 說明理由 | W1 |
| **SUGGESTION** | 可讀性、一致性或邊界防護，不影響現行行為 | 可以順手處理，或另開 follow-up；不處理也不影響合併 | S1 |

### WARNING

**W1. HTTP 401 的 spec 與 design 沒寫「只限帶憑證的請求」**
- **問題點**：`src/api/request.ts:214-218` 只在 `config.sentToken` 存在時把 401 視為憑證失效，也已有對應測試；但 `specs/report-token-expired-error-page/spec.md:72` 的 scenario 字面上適用於任一支請求。
- **影響**：實作是對的。archive 後 spec 會比實作寬鬆，之後依 spec 改程式的人可能把 CDN 請求的 401 也導向錯誤頁。
- **建議方案**：scenario 的 WHEN 改為「帶憑證的請求回應 HTTP 401」，並補一個「不帶憑證的請求收到 401」的 scenario。測試已存在，只需補文件。

### SUGGESTION

**S1. `normalizeOrigin` 沒有過濾 `"null"` origin**
- **問題點**：`src/utils/tokenBridge.ts:48-58` 對 `file:`、`data:` 開頭的值會得到字串 `"null"`，並進入候選清單。
- **影響**：之後 `postMessage(msg, 'null')` 會拋 `SyntaxError`，關閉訊息送不出去。前提是 e.json 被填成非網址的值，屬部署設定錯誤，所以列為 SUGGESTION。
- **建議方案**：回傳前加上 `origin === 'null' ? '' : origin`，並在無效 origin 的測試案例補 `'file:///x'`。

### 建議的處理順序
1. W1 只需改文件，建議 archive 前處理。
2. S1 可以後續處理，也可以併入階段二。

以上供參考，若有判讀不對、或我沒掌握到的背景，再麻煩指正，謝謝！

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## 範例二：第二輪

上一輪的編號到 `S4`，所以這一輪的新建議從 `S5` 開始。等級表的定義與第一輪相同，只更新「本次項目」欄。

```markdown
## OpenSpec verify 結果：`add-postmessage-jwt-token`（第 2 輪）

感謝上一輪意見的快速處理！這一輪 0 CRITICAL、0 WARNING、1 SUGGESTION，規格層面已沒有落差，可以準備 archive。

### 審閱方式
- **範圍**：HEAD `8d2cc6b`（與本 MR 目前的 head 相同）
- **方法**：以 Claude Code 執行 `openspec verify`，每一項都回到程式碼與 spec 查證；新發現的項目另追查 git 歷史確認來源
- **實際執行的驗證**：
  - `vitest --run`：9 files / 123 tests 全部通過
  - `vue-tsc --build`：exit 0
  - `eslint .`：0 errors、1 warning（`scripts/generate-layer-fallback.mjs:415`，不在本 change 範圍）
- **未涵蓋**：各環境 e.json 的 `gameapp`、`home` 不在 repo 內，無法從程式碼確認

### 結論
74/74 tasks 完成；11 個 requirements 與 42 個 scenarios 都有對應實作與測試；設計決策 D1–D9 均已遵循。

### 等級說明與處理方式
| 等級 | 意義 | 建議採取的方案 | 本次項目 |
|---|---|---|---|
| **CRITICAL** | 會造成功能錯誤、安全或資料問題；或 requirement 未實作、task 未完成 | 建議合併前修正 | 無 |
| **WARNING** | 規格或設計與實作不一致、缺少測試證據，或特定情境下可能出錯 | 建議 archive 前處理；需要延後時，請在 MR 說明理由 | 無 |
| **SUGGESTION** | 可讀性、一致性或邊界防護，不影響現行行為 | 可以順手處理，或另開 follow-up；不處理也不影響合併 | S5 |

### 上一輪項目追蹤
| 項目 | 狀態 | 依據 |
|---|---|---|
| W1 | 已處理 | spec 已限定帶 `Authorization` 的請求，並新增對應 scenario |
| W2 | 已處理 | proposal 的 Impact 已列入移除 `authUtil` |
| W3 | 已處理 | 新增 `src/App.spec.ts`，涵蓋 4 個錯誤畫面 scenario |
| S1–S4 | 已處理 | `src/config/initSettings.spec.ts`、`src/utils/tokenBridge.ts:57`、`src/api/request.ts:147-149` |

### SUGGESTION

**S5. `retryWithFreshToken` 在錯誤畫面已顯示時的路徑，與 design D5 的描述不一致**
- **問題點**：`design.md:100` 寫「錯誤畫面已顯示時…直接 reject」。實作中「要票前」的檢查併在 `src/api/request.ts:137` 的 if 條件裡，不成立時落到 `:157`，會再呼叫一次 `setBlockingError('9001')` 才 reject。
- **影響**：`blockingErrorCode` 目前只會被設成 `9001`，重複寫入同一個值沒有可觀察的差異。測試沒有斷言呼叫次數，所以不會暴露。
- **建議方案**：
  - **改程式（建議）**：在 `:137` 之前加 early return，並從 if 條件移除 `isBlocked`。階段二會動到這個函式，三個檢查點寫法一致比較不容易改壞。
  - **改文件**：D5 改成分別描述兩個檢查點的行為。不動程式，沒有 regression 風險。

### 待確認事項
- 各環境 e.json 的 `gameapp`、`home` 是否已填為 game-launcher 與大廳的實際部署網域，需要維運確認。

### 建議的處理順序
S5 不影響合併與 archive，方便的話 archive 前順手處理，或併入階段二也可以。

以上供參考，有任何疑問再一起討論，謝謝！

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```
