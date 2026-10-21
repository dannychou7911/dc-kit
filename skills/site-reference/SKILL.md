---
name: site-reference
description: 擷取指定網站的各頁截圖（Desktop／Mobile）、版面區塊架構、功能清單與 UI/UX design token（色彩、字型、間距、圓角、陰影、斷點、元件樣式），產出一份可直接開啟的單檔 HTML 參考報告，作為模仿或重新設計該網站的依據；可選擇加入需求訪談欄位。只要使用者提供網址並想「擷取網站」「截圖整站」「分析網站結構／版面／設計語彙」「拆解別人的網站」「做 design token 盤點」「做競品網站參考」「把某網站整理成 sitemap＋截圖」，即使沒有明說要 HTML 報告，也應使用此 skill。
compatibility: 需要 chrome-devtools MCP（navigate_page、emulate、evaluate_script、take_screenshot、take_snapshot、click、hover）與 python3；裁切圖片時需要 Pillow（可選）。
---

# Site Reference

把一個網站整理成「看得懂、可以照著做」的參考資料：每頁長什麼樣子、由哪些區塊組成、提供哪些功能、用了哪些設計數值。

產出是一個資料夾，雙擊 `index.html` 就能瀏覽，不需要 server：

```
<輸出目錄>/
├── site.json          # 所有分析結果（唯一資料來源，HTML 與示意圖都由它產生）
├── index.html         # 由 scripts/build_report.py 產生
├── screenshots/{desktop,mobile,states,components}/
└── wireframes/<page-id>.svg   # 由 scripts/wireframe.py 產生
```

把分析結果集中在 `site.json`，是為了讓報告和示意圖可以隨時重新產生；要修正內容時改 JSON 再重跑腳本，不要手動改 `index.html`。

## 步驟 1：確認輸入（一次問完）

使用者通常只會給 URL。用 AskUserQuestion 一次確認其餘選項，並給預設值，讓使用者可以直接按下一步：

| 項目 | 預設 |
|---|---|
| 裝置 | Desktop 1440 + Mobile 390 |
| 頁面範圍 | 主選單第一層 + 每種模板各 1 個代表頁 |
| 需求訪談欄位 | 不加入 |
| 輸出目錄 | 專案有 `docs/` 就用 `docs/site-reference/<domain>-<YYYY-MM-DD>/`，否則用 `site-reference/<domain>-<YYYY-MM-DD>/` |

需求訪談要在這一步決定，因為它會影響要不要替每頁準備「預擬問題」，最後才問會導致重做。

**輸出目錄必須在專案內**：chrome-devtools 的 `take_screenshot` 只能寫入專案目錄，寫到 `/tmp` 或 scratchpad 會被拒絕。

**只讀取、不改動目標網站**：不送出表單、不登入、不重試出錯的功能、不大量併發開頁。在瀏覽器內注入 CSS／JS 只影響自己的分頁，可以做。

## 步驟 2：建立網站架構

1. `new_page` 開啟首頁（建議用獨立的 `isolatedContext`，避免沾到使用者的登入狀態），先 `emulate` 成 `1440x900x1`。
2. 安裝 helper：讀 `scripts/browser-helpers.js` 的完整內容，作為 `evaluate_script` 的 `function` 參數執行一次。換頁會清掉 `window` 上的東西，但 helper 會把自己的原始碼存進 `sessionStorage`，所以同網域換頁後只要執行：
   ```js
   () => (0, eval)('(' + sessionStorage.getItem('__siteRefSrc') + ')')()
   ```
   就能重新安裝，不必每頁重貼整份檔案（約 20KB）。如果回傳錯誤（網站的 CSP 禁止 `eval`，或換到其他網域），再改回貼整份檔案。
3. `() => window.__siteRef.links()` 取得 header 與 footer 連結，以及站內連結依路徑分組的數量。網站沒有 `header`／`nav`／`footer` 標籤時，會改用 class 名稱或位置來找，回傳的 `source` 會註明用了哪一種；結果看起來不對時，以首屏截圖為準。
4. 嘗試抓 `/sitemap.xml`、`/sitemap_index.xml`、`/robots.txt` 中列出的 sitemap（在頁面內用 `fetch`，同網域才讀得到），補齊選單上沒有的頁面類型。
5. 依「模板」分組，不是依 URL：
   - 同模板只挑 1 個代表頁，但記下數量（例如「文章內文，共 48 篇」）。
   - 同模板有明顯變體（欄位不同、版型不同）時，每種變體各挑 1 頁。
   - 補上特殊頁：404（打一個不存在的路徑）、搜尋結果頁；多語系只拍預設語系，其他語系記錄在 notes。
6. 把頁面清單（id、名稱、URL、模板、數量）告訴使用者。頁面超過 15 個時，先確認範圍再繼續，因為後面每頁都要截圖與量測，成本跟頁數成正比。

## 步驟 3：逐頁擷取

每頁、每個裝置都照同一個順序做。順序固定是為了避免「截完才發現沒處理 sticky header」而重拍；這是過去實作中最常重工的地方。

```
navigate_page → 安裝 helper → 通過前置關卡（年齡驗證、cookie 同意，用 take_snapshot 找按鈕再 click）
→ () => window.__siteRef.inspect()          ← 每頁第一次擷取前先判斷
→ async () => await window.__siteRef.prepare()
→ take_screenshot（fullPage: true, format: jpeg, quality: 75）
→ () => window.__siteRef.sections()
```

**捲動動畫型的頁面要改用「捲動序列」**：這類頁面的內容要捲到才會出現，或某段畫面會固定住、隨捲動播放動畫，整頁截圖會出現重複的 hero、大片空白或整體泛白。`inspect()` 回傳 `scrollDriven: 'likely'`，或整頁截圖出現上述現象時，改用以下流程：

1. 重新載入頁面（`navigate_page` 的 `type: reload`）。`prepare()` 一口氣捲到底再跳回頂端，可能已經弄亂頁面的動畫狀態。
2. 重新安裝 helper、通過前置關卡，然後執行 `prepare({ scroll: false, hide: [...] })`，只做隱藏與等待，不捲動。
3. `() => window.__siteRef.scrollFrames()` 取得截圖位置：每個區塊的起點，很高的區塊每隔兩個畫面高再補一張。
4. 對每個位置執行 `async () => await window.__siteRef.goTo(y)`，接著 `take_screenshot`（不帶 `fullPage`），檔名用 `frame-NN.jpeg`。
5. 用 Pillow 拼成總覽圖逐張檢查，拿掉剛好拍在轉場中間的空白畫面，再執行：
   ```bash
   python3 <skill-dir>/scripts/stitch_frames.py screenshots/desktop/01-home.jpeg frame-00.jpeg frame-01.jpeg ...
   ```
   拼好後把 `frame-*.jpeg` 移到 scratchpad，不要留在輸出目錄。
6. 在 `site.notes` 註明這一頁是捲動序列拼接，不是單一整頁截圖。

同一個網站的 Mobile 版常常不用捲動動畫，所以要對 Mobile 另外執行一次 `inspect()` 判斷。

- **Mobile**：`emulate` 成 `390x844x1,mobile,touch`，並給 iPhone 的 `userAgent`，有些網站靠 UA 判斷是否輸出手機版 HTML。切回 Desktop 時要把 `userAgent` 設回空字串。
- **截完要看**：用 Read 打開截圖確認沒有空白區塊、重疊的 header 或還沒載入的圖。整頁截圖很長時，用 Pillow 裁出頁首、中段各一塊來看。只看指令有沒有成功是不夠的。
- **`prepare()` 的回傳值要看**：`fixedElements` 會列出它沒有處理的固定定位元素（例如客服按鈕、cookie bar）。會遮住內容的，用 `prepare({ hide: ['選擇器'] })` 重跑。
- **`sections()`** 會回傳頁面的頂層區塊與實測高度。被移到畫面左右兩側之外的元素（沒顯示的 Tab 內容、輪播的其他張）會自動排除。結果不對的話（例如整頁只抓到 1 個區塊，或同一個位置出現好幾個區塊），用 `sections('選擇器')` 指定區塊選擇器，例如 Elementor 的 `'.elementor-location-header, [data-elementor-type=wp-page] > .e-con, [data-elementor-type=wp-page] > section, .elementor-location-footer'`。
- **互動狀態**另外存到 `screenshots/states/`：選單展開、hover、Tabs 各分頁、輪播、彈窗、手機漢堡選單。做法是先寫一個切換函式（例如 `showTab(i)`），再逐一截圖。
  - **橫向滑動的元件**：整頁截圖會把橫向捲動位置重設回 0，所以要先把 viewport 拉高（例如 `390x1300x1,mobile,touch`），再用一般截圖（`fullPage: false`）。

各平台與各種異常狀況的處理方式在 `references/capture-gotchas.md`，遇到截圖異常時讀這份。

## 步驟 4：擷取 design token

design token 是網站重複使用的設計數值，例如主色、字級、圓角。對「要模仿這個網站」的人來說，這部分比截圖更有用，因為截圖只能看，token 可以直接拿來用。

1. 在首頁和 1～2 個內容最豐富的頁面執行 `() => window.__siteRef.tokens()`，合併結果。
2. 原始數據只是出現次數的統計。要整理成有語意的 token 再寫進 `site.json`：
   - 顏色：歸類為 brand／accent／text／background／border／state，並寫出用途。出現次數很少的顏色通常是圖片或第三方元件帶進來的，不要列入。
   - 字級：以 `typeScale` 為主。它把畫面上所有文字依「字型＋大小＋粗細＋大小寫」分組，由大到小排列，並附上出現次數、使用的標籤與範例文字。整理成 Display／Section Title／Body／Nav／Caption 等層級；出現次數只有 1、2 次的通常是特例，不要列為獨立層級。有 CSS 變數就以變數為準。
     - `tokens()` 不統計 `display: none`、`visibility: hidden`、透明（`opacity` 接近 0）或在畫面左右兩側之外的元素。捲動動畫型頁面的內容在捲到之前通常是透明的，所以要在 2～3 個不同的捲動位置各執行一次，再合併結果。
   - 間距：歸納出 section 上下 padding、元素間 gap、容器最大寬度的規律。
3. `cssVariables` 有值時，通常就是網站自己定義的 token（例如 Elementor 的 `--e-global-color-*`）。優先採用，並對照實際使用的值。
4. `inaccessibleSheets` 不為空時，表示有跨網域的 CSS 讀不到規則，斷點和 CSS 變數可能不完整。要在 `site.notes` 註明。
5. 元件樣式：`tokens().components` 會列出按鈕、輸入框的樣式特徵與位置。挑主要的幾種，用 `take_screenshot`（不帶 fullPage）加 Pillow 依位置裁切，存到 `screenshots/components/`。

## 步驟 5：撰寫 site.json

格式定義與完整範例在 `references/site-data-schema.md`，寫之前先讀。重點如下：

- `pages[].sections` 由上到下排列，第一個是 Header、最後一個是 Footer。示意圖的編號就是這個順序，HTML 的結構清單也用同一份資料，所以兩者一定對得上。
- 每個 section 的 `desktop.h`／`mobile.h` 填 `sections()` 量到的實測高度（px）：
  - 量不到時填文字，例如 `"含於 ⑤"`。
  - 該裝置上不顯示時，`mobile` 填 `{ "hidden": true }`。
- `layout` 選最接近的版型，讓示意圖畫出對應的線框。可用值見 schema 文件。
- `notes` 用 `[ref]` 值得參考、`[avoid]` 不建議照抄、`[fact]` 已確認事實、`[todo]` 待確認 作為開頭標籤。只寫有觀察依據的內容；推測要寫明是推測。
- 開啟需求訪談時，每頁另外寫 2～4 個 `questions`，內容要具體到這一頁，例如「首頁輪播要保留幾張？」，不要寫「這頁滿意嗎？」這種泛泛的問題。

## 步驟 6：產生示意圖與報告

在輸出目錄的上一層或任何位置執行皆可，路徑都用參數指定：

```bash
python3 <skill-dir>/scripts/wireframe.py <輸出目錄>/site.json
python3 <skill-dir>/scripts/build_report.py <輸出目錄>/site.json
```

- `wireframe.py`：依每頁的 `sections` 產生 `wireframes/<page-id>.svg`。左邊 Desktop、右邊 Mobile，同編號對齊；高度經過壓縮，右上角標實測值。
- `build_report.py`：把 `site.json` 內嵌進 `assets/report-template.html`，輸出 `index.html`。如果 `options.interview` 為 true，報告會包含訪談欄位、localStorage 自動儲存、匯出 Markdown／JSON。

## 步驟 7：驗證後回報

1. 用 `navigate_page` 開啟 `file://<輸出目錄>/index.html`，執行 script 檢查所有 `<img>` 的 `naturalWidth > 0`，並列出載入失敗的路徑。
2. 截圖檢查報告的三個地方：Design System 區塊、任一頁的示意圖 tab、Mobile 截圖 tab。重點看文字有沒有溢出、編號是否對齊。
3. 刪除過程中產生的暫存檔（預覽圖、snapshot 文字檔）。
4. 回報內容：
   - 輸出位置、頁面數與截圖數。
   - 沒涵蓋的範圍：沒拍 Mobile 的頁、需要登入的頁、跨網域讀不到的 CSS。
   - 3～5 個最值得參考的設計重點（`[ref]`），以及需要注意的問題（`[avoid]`）。

## 著作權提醒

報告用途是參考設計語彙與資訊架構。在回報時提醒使用者：實際開發時，圖片、Logo、插圖、文案要換成自己的素材，字型要確認授權。
