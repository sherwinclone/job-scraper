# job-scraper

抓取遠端 Data / Backend 職缺，過濾後存進 SQLite，並可選擇用 Telegram 通知新職缺。目標是亞洲時區可做的遠端工作，會排除綁定特定國家的 remote 職缺。

## 做什麼

- 來源：Remote OK、We Work Remotely、Remotive、Himalayas、104、Indeed / LinkedIn / Glassdoor（`python-jobspy`）、Hitmarker、Parlay Jobs、JustRemote、Welcome to the Jungle、Working Nomads
- 依職稱與標籤過濾，並排除國家鎖定的 remote
- 結果寫入 SQLite（預設 `data/jobs.db`，此檔已被 git 忽略）
- 設定 Telegram 環境變數後，可把尚未通知的新職缺送出

## 環境

- Python 3.12 或以上

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

`[dev]` 會一併安裝 pytest。只跑抓取、不跑測試時，可用 `python -m pip install -e .`。

## 執行

```bash
python -m job_scraper scrape
python -m job_scraper scrape --notify
python -m job_scraper list
python -m job_scraper stats
python -m job_scraper notify
python -m job_scraper pull
```

- `scrape`：抓取、過濾、寫入資料庫。加上 `--notify` 時，若有新職缺會送到 Telegram。
- `list`：列出最近 7 天職缺（可用 `--days` 調整）。
- `stats`：顯示總數與各平台數量。
- `notify`：只送出尚未通知的職缺。
- `pull`：用 `gh` 下載 GitHub Actions 工作流程 `daily-scrape.yml` 最新成功執行的 `jobs.db`，合併進本地資料庫。需要已登入的 GitHub CLI。

資料庫路徑可用 `--db` 指定，例如 `python -m job_scraper scrape --db data/jobs.db`。

## 測試

```bash
python -m pytest
```

## 環境變數與 GitHub Secrets

請在執行前把下列名稱 export 到目前的 shell。若寫在 `.env`，需自行載入後才會生效。下面只列出名稱，不要把值寫進版本庫或提交紀錄。

| 名稱 | 何時需要 |
| --- | --- |
| `TG_BOT_TOKEN` | 執行 `scrape --notify` 或 `notify` 時 |
| `TG_CHAT_ID` | 同上，接收訊息的 Telegram chat |

未設定時，抓取與寫入資料庫仍會進行，通知會被略過。

GitHub Actions 排程工作流程 **Daily Job Scrape**（`.github/workflows/daily-scrape.yml`）使用同一組名稱，請在 repository 的 Actions secrets 建立：

- `TG_BOT_TOKEN`
- `TG_CHAT_ID`

該工作流程於每天 UTC 01:00（台灣時間 09:00）執行，也可在 Actions 頁面手動觸發。它會用 `python -m pip install .` 安裝本專案依賴（含 `python-jobspy`），再執行 `python -m job_scraper scrape --notify --db data/jobs.db`，並保留 `data/jobs.db`。

排程只會在預設分支（master）上的工作流程檔生效。若 GitHub 因久未執行而停用此工作流程，需在網頁上手動重新啟用：Actions → Daily Job Scrape → Enable workflow。
