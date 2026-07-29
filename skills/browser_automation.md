# Browser Automation

## 說明...
無頭瀏覽器是一種沒有圖形用戶界面的瀏覽器，適用於自動化測試和驗證。此技能涵蓋如何使用 Selenium 或其他工具來自動化瀏覽器操作，如導航、點擊和驗證頁面內容。

## 關鍵代碼片段或模式
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 導航到頁面
driver.get('http://127.0.0.1:9100/index.html')

# 查找元素並點擊
execute_button = driver.find_element(By.ID, 'execute-button')
execute_button.click()

# 驗證元素存在
assert driver.find_element(By.ID, 'execution-log')

driver.quit()
```

## 常見錯誤及避免方法
- **元素未找到**：確保元素在頁面上存在且 ID 或其他選擇器正確。
- **頁面加載延遲**：使用顯式等待來處理頁面加載延遲，例如 `WebDriverWait`。
- **瀏覽器驅動版本不匹配**：使用 `webdriver-manager` 來自動管理瀏覽器驅動版本，避免版本不匹配導致的錯誤。