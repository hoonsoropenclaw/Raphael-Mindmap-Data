# data_crawling_extraction_and_schema_inference

## 說明
本技能涵蓋數據爬取、提取、可視化以及模式推斷的完整流程，特別是從 HTML 文件中提取內聯的 `<script>` 區塊，以便進行後續的語法檢查或執行。數據爬取涉及從網絡資源中獲取數據，提取則是從獲取的數據中解析出有用的信息。可視化有助於理解數據的結構和分佈，而模式推斷則是從數據中推斷出潛在的結構或規則。

## 數據爬取與提取

### 關鍵代碼片段或模式
```python
import requests
from bs4 import BeautifulSoup
import re

# 數據爬取：從指定的 URL 獲取網頁內容
url = 'https://example.com'
response = requests.get(url)
html_content = response.text

# 數據提取：使用 BeautifulSoup 解析 HTML 並提取內聯的 <script> 區塊
soup = BeautifulSoup(html_content, 'html.parser')
scripts = soup.find_all('script', src=False)

# 使用正則表達式提取 <script> 標籤內的內容
script_blocks = [script.string for script in scripts if script.string]
# 或者使用正則表達式
script_blocks = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', html_content, re.DOTALL)
```

### 常見錯誤及避免方法
- **錯誤**: 未能正確匹配內聯的 `<script>` 區塊。
  **解決方法**: 使用正則表達式時，確保排除帶有 `src` 屬性的 `<script>` 標籤，並使用 `re.DOTALL` 標誌以匹配多行內容。
- **錯誤**: 網頁內容未正確獲取。
  **解決方法**: 使用 `requests` 庫時，檢查響應狀態碼並處理異常情況，例如使用 `response.raise_for_status()` 來拋出異常。

## 可視化

### 關鍵代碼片段或模式
```python
import matplotlib.pyplot as plt
import pandas as pd

# 假設我們已經提取了一些數據並存儲在 DataFrame 中
data = {
    'Category': ['A', 'B', 'C', 'D'],
    'Values': [10, 20, 15, 25]
}
df = pd.DataFrame(data)

# 繪製柱狀圖
plt.bar(df['Category'], df['Values'])
plt.xlabel('Category')
plt.ylabel('Values')
plt.title('Category vs Values')
plt.show()
```

### 常見錯誤及避免方法
- **錯誤**: 圖表顯示不清晰或信息不完整。
  **解決方法**: 確保軸標籤和圖表標題清晰，並選擇合適的圖表類型來展示數據。
- **錯誤**: 數據未正確傳遞給繪圖函數。
  **解決方法**: 檢查數據格式並確保數據已正確加載到數據結構中，例如使用 `df.head()` 來檢查 DataFrame 的內容。

## 模式推斷

### 關鍵代碼片段或模式
```python
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# 假設我們有一組多維數據
data = pd.DataFrame({
    'Feature1': [1, 2, 3, 10, 12, 13],
    'Feature2': [1, 1, 2, 11, 12, 12]
})

# 使用 PCA 進行降維
pca = PCA(n_components=2)
principal_components = pca.fit_transform(data)

# 使用 KMeans 進行聚類
kmeans = KMeans(n_clusters=2)
clusters = kmeans.fit_predict(principal_components)

# 可視化聚類結果
plt.scatter(principal_components[:, 0], principal_components[:, 1], c=clusters, cmap='viridis')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('KMeans Clustering')
plt.show()
```

### 常見錯誤及避免方法
- **錯誤**: 聚類結果不理想。
  **解決方法**: 嘗試不同的聚類算法或調整參數，例如選擇合適的 `n_clusters` 值。
- **錯誤**: 數據未正確標準化。
  **解決方法**: 在進行模式推斷之前，確保數據已進行適當的標準化或歸一化處理。

## 總結
本技能結合了數據爬取、提取、可視化和模式推斷的多個方面，提供了一個全面的框架來處理和分析網絡數據。通過正確應用這些技術，可以有效地從複雜的 HTML 結構中提取有用的信息，並對其進行深入的分析和可視化展示。