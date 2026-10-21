# Unraid 繁體中文（台灣）語言包

本專案提供 Unraid WebGUI 的 **台灣繁體中文在地化**。翻譯原則除了繁體字之外，也重視實際操作語境、儲存與網路術語的一致性，以及資料清除或重建等操作警告的準確性。

## 維護與貢獻

- 以 **磁碟／裝置、校驗磁碟、同位元校驗檢查、儲存池、共享資料夾、連接埠、使用者名稱、USB 開機裝置** 等台灣慣用詞為主。詳見 [台灣術語表](docs/GLOSSARY.zh-TW.md)。
- 翻譯檔採 `英文查找鍵=繁體中文譯文` 格式，**只修改等號右邊**。請保留 `%s`、`%d`、Markdown／HTML 標記、網址、命令及路徑。
- 多行說明以 `:名稱_help:` 或 `:名稱_plug:` 開始，以 `:end` 結束，**不可更改標記名稱**。
- 每次提交前請執行 `python3 scripts/validate_translations.py`，GitHub Actions 也會在 Pull Request 中自動檢查格式與常見翻譯錯誤。
- 新版 Unraid 可能有尚未收錄的英文介面字串；第三方外掛若未提供語言鍵，語言包無法直接覆蓋其硬編碼英文內容。
- **涉及格式化、加密、Btrfs 修復、權限變更或磁碟指派的翻譯，務必在實際 Unraid WebGUI 確認。**

## Unraid 7.3.3：完整翻譯檔覆蓋與測試

目前依照上游 [`unraid/lang-en_US`](https://github.com/unraid/lang-en_US) 的參照版本 `98e4e91e870663720f749c27035d69c31a680ce9`，補齊 **51 個翻譯文字檔**（另有 `LICENSE.txt`，總共 52 個文字檔），包含已支援多語系的第三方外掛。

- 執行 `python3 scripts/validate_translations.py` 檢查容量前綴、特殊變數、繁體用詞與安全說明。
- 執行 `python3 scripts/check_upstream_coverage.py /path/to/lang-en_US` 比對每個檔案的**原始英文鍵名**及所有說明區塊。
- 執行 `python3 scripts/build_language_zip.py` 產生 `dist/zh_TW.zip`，不包含 GitHub 或測試相關檔案。
- 可直接從 [GitHub Actions](https://github.com/calebweixun/unraid_lang-zh_TW/actions) 下載近期成功驗證的 `zh_TW-language-pack` 測試成品。

**重要限制：**上游英文語言庫的參照提交時間早於 Unraid 7.3.3 發布日期。這代表「翻譯檔與上游完全對齊」，**不等於保證 Unraid 7.3.3 所有介面都會顯示繁體中文**；新版 UI 可能有未提供翻譯鍵的新增元件，部分外掛也可能未支援多語系。請以實際 7.3.3 WebGUI 的顯示結果進行驗收。

## 本機測試

將本專案的語言文字檔及原本的外掛目錄依其相對路徑打包，並使用 Unraid 網頁管理介面的語言開發者模式匯入。確認 Main、Dashboard、Shares、Settings、Docker、VMs 和 Tools 的按鈕、說明與警告正常顯示，再提交修改。

下方保留原始英文翻譯格式參考；部分介面路徑可能因 Unraid 版本不同而有所差異。

---

## Original translation-format reference (English)

# lang-zh_TW (original reference)

### READ THIS WHEN YOU WANT TO MAKE TRANSLATIONS TO ANOTHER LANGUAGE

This repository contains core translation files and additional translation files for supported plugins. The sections below document the original core file layout:

- translations.txt -- these are general translations and loaded each time
- helptext.txt     -- these are all help text sections and loaded each time
- dashboard.txt    -- these are translations for the dashboard section
- main.txt         -- these are translations for the main section
- shares.txt       -- these are translations for the shares section
- users.txt        -- these are translations for the users section
- settings.txt     -- these are translations for the settings section
- plugins.txt      -- these are translations for the plugins section
- docker.txt       -- these are translations for the docker section
- vms.txt          -- these are translations for the vms section
- tools.txt        -- these are translations for the tools section
- javascript.txt   -- these are translations for javascript scripts
- scripts.txt      -- these are translations for local scripts
- apps.txt         -- these are translations for the CA section
- ca_settings      -- these are translations for the CA settings
- javascript.ca.txt-- these are translations for the CA javascript

All file names are in lowercase and should be included in the repository to make the translations complete.

Removing a particular file, means no translations will be available for that section and the GUI will display text in original English.

### TRANSLATIONS

Each text file contains regular text strings stored in UTF-8 format with linux line-endings.
Use a text editor which supports UTF-8 and linux format, like [notepad++](https://notepad-plus-plus.org/downloads)

The content of each text file is separated into two parts

### PART 1

These are single line entries which are in the format:

`original English text=translated Foreign text`

Only modify the text after the equal sign(=) and leave the original English text at the left untouched.
Removing a line or omitting a translation after the equal sign, results in the GUI displaying this line with the original English text.

The translated text may have 'special characters', such as slashes, parenthesis or brackets which are not included in the key text,
but which are used to display text accordingly. E.g.

`Options see Help=Options (see Help)`

The characters \* and \*\* are used to display text in italics and bold respectively. E.g.

`Array must be Stopped to change=Array must be **Stopped** to change`

It is recommended to make translations per section, that is one file at the time, and verify the correctness of the translations in the GUI
before proceeding with the next section.

Keep in mind the length of the translations and try to make them similar length as the original text and avoid space issues in the GUI.

### PART 2

These are multi line entries used to translate multiple lines at once.
Multi line translations have a unique opening and closing tag:

**:unique_tag_name_plug:** - unique opening tag used for any multi line text section

**:end**    - closing tag

Do not remove or alter these tags and only translate the text between the opening and closing tags!

### HELP TEXT

All help text of the GUI is stored in a single file *helptext.txt*.

This file has multiple help text sections. Each section is enclosed by a unique opening tag and corresponding closing tag.

**:unique_tag_name_help:** - unique opening tag used for a help text section

**:end**    - corresponding closing tag

Do not remove or alter these tags and only translate the text between the opening and closing tags!

Be aware that Markdown styling syntax is used, this must be preserved.

### LOCAL TESTING

Once the translations are complete and you want to test locally the (intermediate) results, the text files need to be zipped into a single ZIP file.
Give the ZIP file the name of your language, e.g. French.zip.

In the GUI go to: Tools -> webGUI -> Language (switch to Developer view)

- By default only the English language is installed (built-in)
- Choose the ZIP file you have created earlier as the source file
- If the language name is recognized, it will be automatically selected, otherwise chose the name of the language from the dropdown menu to install.
- Click on "Upload" will add your translations to the GUI under the selected language name

NOTE: If your language is not available from the dropdown menu, please make a request on the [Unraid forum](https://forums.unraid.net/forum/75-multi-language-section/)

Now your language is available for local testing!

In the GUI go to: Settings -> Display Settings -> Language

- Select the preferred language from the dropdown menu. Note that only the available language choices are displayed here.

### GITHUB

A language repository will be made available at [Github](https://github.com/unraid), where translators can create Pull Requests (PR) and submit their work.

Once you are satisfied with your results, use Github (an account is required) to fork the respective language repository and create a PR with your modifications.

Limetech will review this and merge your work when approved.

### UPDATES

When updated source text files in English become available in the future, these updates will be made available through Github.

Translators can use the Github system to see which changes are made and update their translations accordingly.

### CREDITS

Your efforts are much welcomed and to show our appreciation, your name and language are credited on the Credits page under Tools in the GUI.
Please let us know which credentials to use.

Thank you very much!

## Unraid 7.3.3 英文選單／單位顯示排查

- 語言鍵名採精確比對（包含**大小寫、空白和句尾標點**）。例如 `Output Voltage` 與 `Output voltage`、`Sleep` 與 `SLEEP` 可能需要各自的翻譯鍵。這份語言包包含使用者回報的 7.3.3 介面變體。
- 部分外掛可能有自己的內建字串，未經 Unraid 語言載入機制的英文介面無法單靠新增 `.txt` 鍵名覆蓋。請確認外掛版本、語言包是否為最新安裝版本，必要時檢查外掛原始碼。
- 容量單位 `prefix_SI` 與 `prefix_IEC` 必須與 [官方英文來源](https://github.com/unraid/lang-en_US/blob/master/translations.txt) 相同。目前值分別是 `K M G T P E Z Y` 與 `Ki Mi Gi Ti Pi Ei Zi Yi`。如果畫面顯示 `•KMGTPEZYB`，**無法由目前字串直接判定原因**；請提供出現該字串的頁面、欄位、瀏覽器與語言包安裝來源，以確認是不是特定介面把前綴當成一般字串、載入舊版語言包或外掛版本不相容。
- 實際測試請使用 GitHub Actions 產出的 `zh_TW.zip`，匯入並重新選用語言，再重新整理（必要時清除瀏覽器快取）；僅更新 GitHub 儲存庫不會自動更新 Unraid 已安裝的語言包。
