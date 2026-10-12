---
name: git-worktree
description: 互動式管理 git worktree：建立指定分支的工作區、列出現有工作區、刪除工作區與本地分支。每個決策點都先詢問使用者，確認完整指令後才執行。僅供手動觸發：/git-worktree [create|remove|list] [分支名稱]
disable-model-invocation: true
argument-hint: "[create|remove|list] [branch-name]"
---

# Git Worktree 互動管理

使用者輸入：`$ARGUMENTS`

worktree 讓同一個 repo 同時 checkout 多個分支，各自放在獨立資料夾，不必 stash 來回切換。這個 skill 幫使用者建立、列出、刪除自己的 worktree。

注意：這不是 Claude Code 內建的 `EnterWorktree` / `ExitWorktree`（那是切換 Claude 自己的 session）。這裡一律用 `git worktree` 指令操作，Claude 的工作目錄保持不動。

## 互動原則

這個 skill 存在的理由就是「使用者逐一選擇、確認後才執行」，所以：

- 每個決策點用 `AskUserQuestion` 詢問，一次一題，給 2～4 個選項；需要自由輸入（例如分支名稱）時，提示使用者選「Other」輸入。
- 使用者在 `$ARGUMENTS` 已經給的資訊不要再問，但仍要在最後確認時列出。
- **執行前一定先列出完整指令清單並取得同意**。使用者只同意部分時，只執行那部分。
- 破壞性選項（`--force`、`git branch -D`）各自獨立詢問，不和一般確認合併，因為它們會丟掉找不回來的東西。
- 偵測指令（`git status`、`git worktree list`、`git show-ref` 等唯讀查詢）不用問，直接跑。

## 進度標示

讓使用者隨時知道自己在流程的哪裡、後面還會問什麼，回答時才能判斷要不要現在就調整方向。

- **第一題之前**，先用一段簡短清單列出這次預計會問的題目，例如：

  ```
  接下來會依序確認：
  1. 從哪個分支開出來
  2. worktree 路徑
  3. 確認執行指令
  ```

  清單依當下已知的偵測結果決定，`$ARGUMENTS` 已提供的資訊不列入。
- **每一題的開頭**標示 `（n/N）` 與題目主題，例如 `（2/3）worktree 路徑`。
- 後續檢查發現需要**追加問題**時（例如刪除流程中發現未 commit 修改，需要問是否 `--force`），先說明新增了哪一題、原因是什麼，再更新總數，例如「安全檢查發現未 commit 修改，新增一題：是否強制刪除，總共變為 5 題」。不要讓 `N` 無聲地改變。
- 使用者選擇中止或取消時，說明停在第幾步、哪些已執行、哪些沒有執行。

## 步驟 0：解析參數與共用偵測

1. 解析 `$ARGUMENTS`：第一個字是 `create` / `remove` / `list` 時當作動作，其餘當分支名稱。只給分支名稱沒給動作、或什麼都沒給時，用 `AskUserQuestion` 問要「建立 / 刪除 / 列出」。
2. 確認在 git repo 內：`git rev-parse --is-inside-work-tree`，失敗就告知並停止。
3. 找出**主工作區**路徑：`git worktree list --porcelain` 的第一筆 `worktree` 行。不要用 `git rev-parse --show-toplevel`，因為使用者可能正位於某個 linked worktree 裡，那會拿到錯的路徑。後續 git 指令一律用 `git -C <主工作區>` 執行，避免受目前所在目錄影響。
4. 遠端名稱：`git remote`。只有一個就用它；有多個且包含 `origin` 用 `origin`；有多個且沒有 `origin` 時詢問；沒有遠端就略過所有遠端相關判斷。

## 列出（list）

執行 `git worktree list`，整理成表格：路徑、分支（或 detached HEAD）、是否有未 commit 修改（`git -C <path> status --porcelain` 是否有輸出）、是否標記 `locked` / `prunable`。若有 `prunable` 項目（資料夾已不存在但紀錄還在），詢問是否執行 `git worktree prune`。

## 建立（create）

### 1. 取得分支名稱

沒有就詢問。用 `git check-ref-format --branch <name>` 驗證，不合法時說明原因並重問。

### 2. 更新遠端資訊

```bash
git -C <主工作區> fetch <remote> --prune
```

讓下一步的「遠端有沒有這個分支」判斷是最新的。失敗（例如離線）時告知使用者，詢問要「用本地資訊繼續」或「中止」。

### 3. 判斷分支狀態

先檢查分支是否已被某個 worktree checkout（`git worktree list --porcelain` 中是否有 `branch refs/heads/<name>`）。git 不允許同一分支同時被兩個 worktree checkout，遇到時告知該 worktree 路徑並停止。

接著依序判斷，三種情況用的指令不同：

| 狀況 | 判斷 | 指令 |
| --- | --- | --- |
| 本地已有 | `git show-ref --verify --quiet refs/heads/<name>` | `git worktree add <path> <name>` |
| 只有遠端有 | `git show-ref --verify --quiet refs/remotes/<remote>/<name>` | `git worktree add --track -b <name> <path> <remote>/<name>` |
| 都沒有 | 以上皆否 | `git worktree add --no-track -b <name> <path> <base>` |

本地與遠端都有、但兩者指向不同 commit 時，告知使用者落後或分歧的情況（`git rev-list --left-right --count <name>...<remote>/<name>`），仍以本地分支建立，不自動更新。

**都沒有時，詢問要從哪個分支開出來**。選項依實際存在的分支組成，例如：目前分支、`main` 或 `master`、`develop`。`<base>` 優先用 `<remote>/<分支>`（剛 fetch 過，是最新的），遠端不存在才用本地分支。

`--no-track` 的理由：從遠端分支（如 `origin/main`）開新分支時，git 預設會把 upstream 設成 `origin/main`，之後在新分支上 `git pull` 會拉到 main 的內容。新分支應該在第一次 push 時才建立自己的 upstream。

### 4. 決定路徑

預設路徑：`<主工作區的上一層>/<repo 名稱>-worktrees/<分支名稱，/ 換成 ->`

例如主工作區在 `~/Project/shop-web`，分支 `feat/ABC-123` → `~/Project/shop-web-worktrees/feat-ABC-123`。

放在 repo 外面，是為了不讓 IDE、ESLint、Vite 等工具掃到重複的原始碼，也不必修改 `.gitignore`。

詢問使用者：「使用預設路徑（顯示完整路徑）」或「自訂路徑」。目標路徑已存在時，告知並請使用者換一個路徑，不覆蓋。

### 5. 確認並執行

列出要執行的完整指令，詢問「執行 / 取消」。同意後執行，再用 `git worktree list` 顯示結果。

### 6. 完成提示

回報 worktree 路徑與 `cd <path>` 指令，並提醒：

- 新 worktree 沒有 `node_modules` 等未追蹤的產物，需要自行安裝依賴（依 lockfile 判斷提示 `pnpm install` / `npm install` / `yarn` / `bun install`）。
- `.env` 等本地設定檔不會跟過去，請使用者自行複製。不要代為讀取或複製這類檔案，它們可能含有 secrets。

## 刪除（remove）

### 1. 選擇要刪的 worktree

從 `git worktree list --porcelain` 取得清單，排除主工作區。沒有任何 linked worktree 時告知並停止。

- `$ARGUMENTS` 有分支名稱 → 找對應的 worktree，找不到就告知並改為讓使用者選擇。
- 候選 ≤ 4 個 → 用 `AskUserQuestion` 列出（label 用分支名，description 放路徑）。
- 候選 > 4 個 → 先用編號表格列出，再請使用者輸入編號或分支名。

### 2. 安全檢查

對選中的 worktree 逐項檢查，結果整理成清單給使用者看：

| 檢查 | 指令 | 為什麼 |
| --- | --- | --- |
| 未 commit 修改（含 untracked） | `git -C <path> status --porcelain` | 刪 worktree 會連同這些檔案一起刪掉 |
| 未 push 的 commit | 有 upstream：`git -C <path> rev-list --count @{u}..HEAD`；沒有 upstream：`git log --oneline <預設分支>..<branch>` | 只存在本地的 commit，刪分支後就找不回來（只能靠 reflog） |
| 是否已合併 | `git merge-base --is-ancestor <branch> <預設分支>`（exit 0 表示已合併） | 決定 `git branch -d` 會不會成功 |
| 是否被 lock | porcelain 輸出中有 `locked` | lock 的 worktree 需要先 `git worktree unlock` |
| 目前所在目錄 | 目前目錄（`pwd -P`）是否在該 worktree 路徑底下 | 使用者的 shell 停在被刪的目錄會出錯 |

預設分支：`git symbolic-ref --short refs/remotes/<remote>/HEAD` 會回傳 `<remote>/main` 這種形式，去掉 `<remote>/` 前綴取得分支名。失敗時依序找本地的 `main`、`master`，都沒有就詢問。

worktree 是 detached HEAD（沒有分支）時，略過分支相關檢查，下一步也只提供「只刪 worktree」。

被 lock 時，顯示 lock 原因並詢問是否解除，不同意就停止。目前目錄在該 worktree 內時，提醒使用者先 `cd` 離開；Claude 自己的指令都用 `git -C <主工作區>` 執行，不受影響。

### 3. 選擇刪除範圍

詢問：

- 只刪 worktree，保留分支
- 刪除 worktree 與本地分支

分支未合併或有未 push 的 commit 時，把「只刪 worktree」標為建議，並在說明中寫出會遺失的 commit 數量。

遠端分支不在這個 skill 的處理範圍內：刪遠端分支是 push 操作，影響其他人。使用者要求時，給出 `git push <remote> --delete <branch>` 讓使用者自己執行。

### 4. 破壞性選項（需要時才問，各自獨立）

- **有未 commit 修改**：列出 `git status --short` 的內容，詢問「強制刪除（`--force`，這些修改會消失）」或「中止，先自行處理」。
- **選了刪分支但分支未合併**：`git branch -d` 會被 git 拒絕。先列出未合併的 commit（`git log --oneline <預設分支>..<branch>`），再詢問「強制刪除分支（`-D`）」或「保留分支」。

### 5. 確認並執行

列出完整指令清單，例如：

```bash
git -C <主工作區> worktree remove <path>
git -C <主工作區> branch -d <branch>
git -C <主工作區> worktree prune
```

詢問「執行 / 取消」，同意後依序執行。任一步失敗就停下來回報實際錯誤，不自動改用 `--force` 或 `-D` 重試。最後用 `git worktree list` 顯示結果。
