# Unraid 7.3.3 主畫面與外掛翻譯：執行階段稽核

## 為何官方 `en_US` 鍵名 100% 覆蓋仍有大量英文？

在 [WebGUI 的 Translations.php](https://github.com/unraid/webgui/blob/26eb1b5c1d547ddbf44a38e63956ba24f659098b/emhttp/plugins/dynamix/include/Translations.php) 中，`translations.txt` 為全域字典。其他語言檔依目前要求的 URI 路徑逐層載入。

這代表 `/Main`、`/sub/devices` 和 `/plugins/unassigned.devices/include/UnassignedDevices.php` 等請求，**不保證載入相同的專屬檔案**。若某字串只在 `Unassigned Devices/unassigneddevices.txt`，背景請求可能無法取得譯文，最後就顯示英文。

此外，官方 `unraid/lang-en_US` 的基準版本可能早於正在執行的 WebGUI 與外掛；新版程式碼會呼叫英文基準尚未列出的鍵名。例子如下：

| 畫面文字 | 原始碼證據 | 修復方式 |
|---|---|---|
| `STOP will take the array offline` | [ArrayOperation.page](https://github.com/unraid/webgui/blob/26eb1b5c1d547ddbf44a38e63956ba24f659098b/emhttp/plugins/dynamix/ArrayOperation.page) 對兩段分別呼叫翻譯 | 新增獨立的 `will take the array offline` |
| `No internal boot setup detected...` | [device_list](https://github.com/unraid/webgui/blob/26eb1b5c1d547ddbf44a38e63956ba24f659098b/emhttp/plugins/dynamix/nchan/device_list) 的背景輸出 | 增加全域 `Internal Boot` 與帶 `%s` 的提示 |
| `SMB Shares` / `Share Type` / `Serial Number (Mount Point)` | [UnassignedDevices.page](https://github.com/unraid/unassigned.devices/blob/7bdcd03cccb67320598e95a1cab38821182f633b/source/unassigned.devices/usr/local/emhttp/plugins/unassigned.devices/UnassignedDevices.page) | 將既有外掛譯文加入全域備援，供主頁及背景請求使用 |
| `No Remote SMB/NFS or ISO File Shares configured` | [UnassignedDevices.php](https://github.com/unraid/unassigned.devices/blob/7bdcd03cccb67320598e95a1cab38821182f633b/source/unassigned.devices/usr/local/emhttp/plugins/unassigned.devices/include/UnassignedDevices.php) 將兩個查找結果接起來 | 分別翻譯兩個子字串，並測試組合後的句子 |
| `Output voltage`、`ONLINE` 等 | 頁面與背景輸出的文字大小寫可能不同 | 補對應鍵名；但不擅自改變動態資料值 |

翻譯查找會**移除部分英文字串的標點符號**。例如原始碼 `_('Serial Number (Mount Point)')` 對應的鍵名是 `Serial Number Mount Point`；單純以顯示的原文新增括號版本，未必能生效。

## 本次修正範圍

- 把 `Unassigned Devices/unassigneddevices.txt`、`Unassigned Devices/unassigneddevicessettings.txt` 與 `Dynamix S3 Sleep/sleepsettings.txt` 中、全域字典原先缺少的 241 個鍵名加入 `translations.txt`。**只新增缺少的鍵，保留原本全域既有譯文**，避免不同功能的 `Format`、`Public` 等詞義互相覆蓋。
- 補上 WebGUI `Main`、裝置串流、內部開機設定、ZFS ARC、Mover、通知及系統日誌設定的新版執行階段字串。
- 修正表格 `Source` 為「來源」，並測試未設定遠端 SMB/NFS/ISO 的組合句。
- 新增 `scripts/check_runtime_translation_scope.py`，對照固定版本的 WebGUI 與 Unassigned Devices 原始碼，檢查翻譯是否能在相應請求的字典範圍找到。這與原本的 `en_US` 覆蓋率檢查為互補驗證。

## 仍不應當成一般文字翻譯的內容

- `cache` 可能是使用者自訂的儲存池名稱。
- `Dev 1` 是 Unassigned Devices 產生的磁碟裝置識別名稱，可能會被指令碼或管理介面引用，不應任意將原始識別值替換為中文。
- `ONLINE` 如經過翻譯函式，現在可顯示「線上」；若其他元件直接顯示底層 ZFS 狀態碼而未呼叫翻譯函式，僅新增語言鍵無法改變畫面。
- 某些第三方外掛會直接輸出硬編碼英文，不能只靠語言包修好。

## 驗收方式

1. 從 PR 成功的 GitHub Actions 下載 **zh_TW-language-pack**，取得裡面的 `zh_TW.zip`，不要使用 GitHub 的 Source code ZIP。
2. 在 Unraid 的語言開發者匯入介面重新安裝 ZIP，重新選擇繁體中文，強制重新整理頁面。官方 [FileUpload.php](https://github.com/unraid/webgui/blob/26eb1b5c1d547ddbf44a38e63956ba24f659098b/emhttp/plugins/dynamix/include/FileUpload.php) 會從 ZIP 取出各檔案的 basename 並清理先前編譯的 `.dot` 翻譯快取，因此更新儲存庫本身不等於已更新伺服器。
3. 驗證 Main 陣列停止說明、Unassigned Devices 共享表格與按鈕、Internal Boot、設定頁通知與 Mover、儀表板 `ONLINE`。
4. 若某個字串仍是英文，請以實際執行的外掛版本與程式碼路徑確認翻譯是否被呼叫。本次自動掃描涵蓋固定的常用頁面和 AJAX 來源，**不代表所有動態 HTML、JavaScript 或未掃描外掛已完成翻譯**。

SI/IEC 前綴維持之前已驗證的空白分隔格式，未變動。
