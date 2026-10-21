# site.json 格式

`site.json` 是報告與示意圖的唯一資料來源。`scripts/wireframe.py` 讀 `pages[].sections` 畫示意圖，`scripts/build_report.py` 把整份 JSON 內嵌進 HTML。

所有路徑（截圖、元件圖）都是**相對於 site.json 所在目錄**。文字欄位支援兩種輕量標記：`` `code` `` 與 `**粗體**`，其他 HTML 會被跳脫。

## 目錄

1. 頂層結構
2. site／options
3. sitemap
4. tokens
5. global
6. pages 與 sections
7. section layout 可用值
8. 完整範例

## 1. 頂層結構

```json
{
  "site": {},
  "options": {},
  "sitemap": [],
  "tokens": {},
  "global": {},
  "pages": []
}
```

只有 `site` 與 `pages` 是必填，其他區塊缺少時，報告會略過對應段落。

## 2. site／options

```json
"site": {
  "name": "Example Studio",
  "url": "https://www.example.com/",
  "capturedAt": "2026-10-14",
  "viewports": { "desktop": "1440x900", "mobile": "390x844 (iPhone UA)" },
  "summary": "一句話描述網站定位與整體風格。",
  "notes": ["[fact] 主選單 6 項，另有 8 個語系", "[todo] 跨網域 CSS 2 份無法讀取，斷點可能不完整"]
},
"options": {
  "interview": false,
  "accent": "#ffcc00",
  "accentInk": "#111111"
}
```

- `options.interview`：true 時，報告會加入訪談欄位（決策、優先度、預擬問題、備註）與匯出功能。
- `options.accent`／`accentInk`：報告本身的強調色與強調色上的文字色，預設為黃底黑字。可以改成目標網站的主色，但要確認對比度足夠。

## 3. sitemap

樹狀結構，`id` 對應 `pages[].id`，`count` 是同模板頁面的數量。

```json
"sitemap": [
  { "id": "home" },
  { "id": "products", "children": [ { "id": "product-single", "count": 24 } ] },
  { "id": "not-found" }
]
```

省略時，報告會依 `pages` 的順序平鋪列出。

## 4. tokens

把 `tokens()` 的原始統計整理成有語意的 token，不要直接貼原始輸出。

```json
"tokens": {
  "colors": [
    { "name": "Brand Yellow", "value": "#ffcc00", "role": "brand", "usage": "主要按鈕、強調線、目前頁面選單" },
    { "name": "Ink", "value": "#1e293b", "role": "text", "usage": "標題" }
  ],
  "cssVariables": [ { "name": "--e-global-color-primary", "value": "#ffcc00", "note": "Elementor 全域色" } ],
  "typography": {
    "families": [ { "name": "Poppins", "role": "標題與內文", "source": "Google Fonts（400/600/700）" } ],
    "scale": [
      { "name": "H1", "fontFamily": "Poppins", "size": "58px", "weight": "600", "lineHeight": "1.2", "letterSpacing": "normal", "sample": "Play Beyond Limits", "mobileSize": "36px" },
      { "name": "Body", "fontFamily": "Poppins", "size": "18px", "weight": "400", "lineHeight": "1.6" }
    ]
  },
  "spacing": [ { "name": "Section 上下 padding", "value": "80px / 80px", "mobile": "48px / 48px" } ],
  "radius": [ { "value": "999px", "usage": "膠囊按鈕" }, { "value": "12px", "usage": "卡片" } ],
  "shadows": [ { "value": "0 4px 16px rgba(0,0,0,.08)", "usage": "卡片" } ],
  "breakpoints": [ { "value": "1024px", "note": "平板以下改單欄" }, { "value": "767px", "note": "手機版選單" } ],
  "layout": [ { "name": "內容最大寬度", "value": "1200px" }, { "name": "Grid gap", "value": "24px" } ],
  "components": [
    {
      "name": "Primary Button",
      "image": "screenshots/components/button-primary.png",
      "css": { "background": "#ffcc00", "color": "#111111", "borderRadius": "999px", "padding": "12px 32px", "font": "600 16px Poppins" },
      "states": "hover：背景變 #111、文字變黃",
      "note": "全站 CTA 共用"
    }
  ]
}
```

`role` 建議值：`brand`、`accent`、`text`、`background`、`border`、`state`（成功、錯誤、警告）。報告會依 role 分組顯示。

## 5. global

全站共用的 Header、Footer、浮動元件、彈窗。格式與單頁相同，但通常不需要 `sections`。

```json
"global": {
  "shots": [ { "label": "Mobile 漢堡選單", "src": "screenshots/states/mobile-menu.jpeg", "mobile": true } ],
  "features": ["主選單 6 項，目前頁以主色標示", "語系切換下拉（8 語系）"],
  "design": ["Header sticky，底部 3px 主色線"],
  "notes": ["[ref] 漢堡選單從右側滑出、全高黑底，層級清楚"],
  "questions": ["Header 選單項目是否沿用？"]
}
```

## 6. pages 與 sections

```json
{
  "id": "home",
  "name": "首頁",
  "url": "https://www.example.com/",
  "template": "首頁",
  "count": 1,
  "purpose": "品牌形象、主打產品與導流",
  "shots": [
    { "label": "Desktop", "src": "screenshots/desktop/01-home.jpeg" },
    { "label": "Mobile", "src": "screenshots/mobile/01-home.jpeg", "mobile": true },
    { "label": "卡片 hover", "src": "screenshots/states/home-card-hover.jpeg" }
  ],
  "sections": [
    { "name": "Header", "desc": "全站共用", "layout": "nav", "desktop": { "h": 96 }, "mobile": { "h": 64 } },
    { "name": "Hero 輪播", "desc": "5 張全寬輪播，左右箭頭＋圓點", "layout": "carousel",
      "desktop": { "h": 640 }, "mobile": { "h": 400 } },
    { "name": "熱門產品", "desc": "8 張卡片，hover 顯示價格與按鈕", "layout": "cards",
      "desktop": { "h": 938, "cols": 4, "rows": 2 }, "mobile": { "h": 907, "cols": 2, "rows": 4 } },
    { "name": "Footer", "desc": "全站共用", "layout": "footer", "desktop": { "h": 485 }, "mobile": { "h": 876 } }
  ],
  "features": ["Hero 自動輪播 5 秒", "卡片點擊開啟產品頁"],
  "design": ["白底與淺灰底交替區隔 section", "標題置中＋上方小字 eyebrow"],
  "notes": ["[ref] 卡片 hover 資訊層設計值得參考", "[avoid] 輪播沒有暫停按鈕，無障礙不佳"],
  "questions": ["Hero 輪播要保留幾張？"]
}
```

| 欄位 | 說明 |
|---|---|
| `id` | 英數與連字號。示意圖檔名為 `wireframes/<id>.svg` |
| `shots[].mobile` | true 時檢視器以手機寬度顯示 |
| `sections` | 由上到下，第一個是 Header、最後一個是 Footer。示意圖編號與報告的結構清單都依這個順序 |
| `sections[].desktop`／`mobile` | `h`：實測高度（px 數字），或量不到時填文字（例如 `"含於 ⑤"`）；`hidden: true` 表示此裝置不顯示；`layout`、`cols`、`rows`、`caption` 可覆寫區塊層級的設定 |
| `sections[].caption` | 顯示在示意圖區塊底部的短說明，例如 `"8 張（4 × 2）"`。Mobile 欄寬只有 190px，文字要控制在 14 個全形字內 |
| `notes` 標籤 | `[ref]` 值得參考、`[avoid]` 不建議照抄、`[fact]` 已確認事實、`[todo]` 待確認 |
| `questions` | 只在 `options.interview` 為 true 時顯示 |

## 7. section layout 可用值

示意圖依 `layout` 畫出對應的線框。選最接近的即可，細節寫在 `desc` 和 `caption`。

| layout | 畫法 | 常用參數 |
|---|---|---|
| `nav` | Logo＋選單（Mobile 為漢堡選單） | — |
| `hero` | 全寬圖片＋置中標題與按鈕 | — |
| `carousel` | 全寬圖片＋左右箭頭＋圓點 | — |
| `banner` | 較矮的全寬圖片＋標題（內頁頁首） | — |
| `text` | 置中標題＋多行文字 | `rows`：文字行數 |
| `split` | 左圖右文（`reverse: true` 為左文右圖）；Mobile 自動改成上下排列 | `reverse` |
| `cards` | 卡片 Grid（圖＋標題＋文字） | `cols`、`rows` |
| `icons` | icon＋標題＋文字的特色列表 | `cols`、`rows` |
| `logos` | Logo 牆 | `cols`、`rows` |
| `list` | 列表（左圖右文的橫列） | `rows` |
| `tabs` | Tab 列＋內容區 | `cols`：tab 數 |
| `form` | 表單欄位＋送出按鈕 | `rows`：欄位數 |
| `cta` | 標題＋按鈕的行動呼籲列 | — |
| `stats` | 數字亮點 | `cols` |
| `media` | 單張大圖或影片 | — |
| `embed` | 嵌入內容（地圖、遊戲 iframe、第三方元件） | — |
| `footer` | 深色底、多欄連結、版權列 | `cols` |
| `blank` | 只畫外框與名稱（無法歸類時使用） | — |

## 8. 完整範例

最小可用範例：

```json
{
  "site": { "name": "Example", "url": "https://www.example.com/", "capturedAt": "2026-10-14" },
  "options": { "interview": false },
  "pages": [
    {
      "id": "home", "name": "首頁", "url": "https://www.example.com/", "template": "首頁",
      "purpose": "品牌形象與導流",
      "shots": [ { "label": "Desktop", "src": "screenshots/desktop/01-home.jpeg" } ],
      "sections": [
        { "name": "Header", "layout": "nav", "desktop": { "h": 96 }, "mobile": { "h": 64 } },
        { "name": "Hero", "layout": "hero", "desktop": { "h": 600 }, "mobile": { "h": 420 } },
        { "name": "Footer", "layout": "footer", "desktop": { "h": 320 }, "mobile": { "h": 560 } }
      ],
      "features": ["Hero CTA 連到產品頁"],
      "design": ["大量留白，單一主色"],
      "notes": ["[ref] Hero 文案層級清楚"]
    }
  ]
}
```
