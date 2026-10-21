# 擷取時的常見問題

截圖或量測結果不對時，先對照這份文件。每一項都寫了「看到什麼現象 → 原因 → 處理方式」。

## 截圖

| 現象 | 原因 | 處理 |
|---|---|---|
| 整頁截圖中 header 出現在中間、或重複出現 | sticky／fixed header 在整頁截圖時位置計算錯誤 | `prepare()` 預設會把頂部全寬的固定元素改成 `position: relative`；如果 header 不在頂部或寬度不足 80%，用 `evaluate_script` 自行對該元素設定 |
| 區塊一片空白，捲過去才出現 | 進場動畫還沒觸發（Elementor `.elementor-invisible`、AOS `[data-aos]`、WOW.js `.wow`） | `prepare()` 會處理這三種。其他 library 可以看空白區塊的 class，再注入 `opacity:1; transform:none; visibility:visible` |
| 圖片是灰底或 placeholder | lazy-load 尚未觸發 | 調小 `prepare({ step: 400, delay: 400 })`，讓捲動更慢；有些 library 用 `data-lazy-src`、`data-bg`，需要自行把屬性搬到 `src`／`background-image` |
| 浮動的客服按鈕、cookie bar 蓋住內容 | 固定定位的小元件 | 看 `prepare()` 回傳的 `fixedElements`，用 `prepare({ hide: ['#chat-widget', '.cookie-bar'] })` 隱藏；在 notes 記錄這些元件的存在，它們也是設計的一部分 |
| YouTube、地圖、遊戲畫面是黑色或空白 | 跨網域 iframe 無法被擷取 | 截圖無法解決，在 HTML 的 notes 註明「實際網站會正常顯示」 |
| 輪播或滑動卡片截不到第 2 張以後 | 整頁截圖會把橫向捲動位置重設為 0 | 把 viewport 拉高（例如 `390x1300x1,mobile,touch`），切換到目標卡片後用一般截圖（不帶 `fullPage`） |
| hover 狀態截不到 | 截圖前滑鼠移開，或 hover 由 JS 控制 | 用 `take_snapshot` 取得元素 uid，`hover` 後立刻 `take_screenshot`；若仍失敗，在 `evaluate_script` 裡對元素加上 hover 時的 class |
| 截圖檔寫入失敗 | `take_screenshot` 的 `filePath` 必須在專案目錄內 | 輸出目錄放在專案內；需要裁切、拼接的暫存檔再複製到 scratchpad 處理 |
| 整頁截圖出現重複的 hero、大片空白，或整頁泛白 | 頁面由捲動驅動動畫：內容要捲到才淡入、某段畫面會固定住並隨捲動切換；整頁截圖只會拍到「捲動位置在頂端」時的狀態 | 用 `inspect()` 確認後，改用 SKILL.md 步驟 3 的「捲動序列」：`scrollFrames()` → `goTo(y)` → 一般截圖 → `stitch_frames.py` 拼接 |
| 跑完 `prepare()` 後 hero 背景消失或變成灰色 | `prepare()` 一口氣捲到底再跳回頂端，打亂了頁面自己的捲動動畫狀態（PG SOFT 首頁實測） | 重新載入頁面，改用 `prepare({ scroll: false })` |
| 整頁截圖太長，Read 看不清楚 | 圖片被縮小顯示 | 用 Pillow 裁出頁首、中段、頁尾各一段再看；或把多張截圖的頁首拼成一張總覽圖一次比對 |

## 量測區塊高度

| 現象 | 原因 | 處理 |
|---|---|---|
| `sections()` 只回傳 1～2 個區塊 | 頁面的 wrapper 結構和預設規則不同 | 用 `sections('選擇器')` 指定，例如 `'main > section'`、`'#content > div'` |
| 同一個位置出現好幾個區塊，內容交錯 | 頁面有多個切換畫面（Tab、子頁籤），沒顯示的畫面用水平位移藏在畫面左右兩側之外，但仍在 DOM 中 | 新版 `sections()` 已自動排除畫面外的元素；如果網站是用 `opacity` 或 `z-index` 疊在同一個位置，仍需用 `sections('選擇器')` 指定目前顯示中的容器 |
| 區塊太細碎（每個標題都是一個區塊） | 選擇器選到的層級太深 | 改選上一層，或在 site.json 中自行合併相鄰區塊（高度相加） |
| 兩個區塊屬於同一個元件，無法分開量（例如 Tab 列與內容） | 同一個 DOM 元素 | 在 site.json 中前一個填 `"含於 ⑤"`，後一個填合計高度，並在 desc 中說明 |
| 用 iframe 一次量多頁時數字錯誤 | iframe 放在畫面外（`left:-9999px`）時，部分網站不會觸發排版或動畫 | iframe 用 `position:fixed` 放在畫面內，量完再移除；或直接逐頁 `navigate_page` 量測（較慢但最可靠） |
| Mobile 量到的數字跟 Desktop 一樣 | 沒有正確切換 viewport | `emulate` 的 viewport 要帶 `,mobile,touch`，並給 iPhone UA；切換後要重新 `navigate_page`（有些網站在伺服器端依 UA 輸出不同 HTML） |

## Design token

| 現象 | 原因 | 處理 |
|---|---|---|
| `cssVariables` 是空的 | 網站沒有使用 CSS 變數，或 CSS 放在跨網域 CDN | 看 `inaccessibleSheets`。若是 CDN，可以用 `fetch` 讀取（需要 CORS 允許），讀不到就只用 computed style 的統計 |
| 顏色統計出現很多奇怪的顏色 | 第三方元件、圖片疊色、透明度漸層 | 只保留出現在 3 個以上元素、或明顯屬於品牌的顏色 |
| 字型在報告中顯示成系統字型 | 本機沒有安裝該字型 | 正常現象。報告的字級表會顯示字型名稱；需要準確預覽時，可以在報告中自行加入 Google Fonts 的 `<link>` |
| 按鈕樣式有很多種 | 同一個按鈕有不同尺寸或狀態 | 依「主要／次要／文字連結」三種整理，尺寸差異寫在 note |

## 平台特性

| 平台 | 要注意的地方 |
|---|---|
| WordPress + Elementor | 區塊選擇器：`[data-elementor-type=wp-page] > .e-con`（新版 Flexbox Container）或 `> section`（舊版 Section）；全域色字型在 `.elementor-kit-*` 的 `--e-global-*` 變數；Header／Footer 為 `.elementor-location-header`／`-footer` |
| WordPress + 主題原生 | sitemap 多半在 `/wp-sitemap.xml`（WP 內建）或 `/sitemap_index.xml`（Yoast、Rank Math） |
| Shopify | 模板依路徑區分：`/products/`、`/collections/`、`/pages/`、`/blogs/`；token 常在 `:root` 的 `--color-*` |
| Webflow | 區塊多為 `.section`；互動用 `data-w-id`，進場動畫會先把 `opacity` 設為 0，需要注入 `opacity:1` |
| 沒有語意標籤的網站（全部用 `div`） | `links()` 會依序改用 class 名稱與位置來找 header／footer 連結，回傳的 `source` 會註明用了哪種方式；也要用首屏截圖核對選單 |
| CSP 禁止 `eval` 的網站 | 用 `sessionStorage` 重新安裝 helper 會失敗，改回每頁貼整份 `browser-helpers.js` |
| Next.js／Nuxt 等 SPA | `navigate_page` 後要等內容渲染完成（`wait_for` 某段文字）；sitemap 可能不存在，要從連結自己整理；路由切換後 helper 仍在，但 DOM 已經換掉 |
| 有前置關卡的網站（年齡驗證、地區選擇、cookie 同意） | 先截一張關卡畫面（它也是設計的一部分），再通過關卡；通過後通常會寫入 cookie，同一個 `isolatedContext` 後續頁面不會再出現 |
| 多語系網站 | 預設只擷取一個語系；檢查語系切換後的連結是否指向正確語系，錯誤時記成 `[avoid]` |
