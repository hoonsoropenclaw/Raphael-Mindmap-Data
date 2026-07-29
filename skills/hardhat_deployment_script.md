# Hardhat Deployment Script

## 說明
此技能涵蓋使用 Hardhat 編寫和執行智能合約的部署腳本，包括以下內容：
- 配置 Hardhat 環境，包括網絡設置和合約編譯。
- 編寫部署腳本以部署智能合約到指定的區塊鏈網絡（如 Ethereum）。
- 使用環境變量來管理私鑰和網絡配置以確保安全性。

## 關鍵代碼片段
```javascript
const hre = require("hardhat");

async function main() {
  const RaphaelCoin = await hre.ethers.getContractFactory("RaphaelCoin");
  const raphaelCoin = await RaphaelCoin.deploy(1000000);
  await raphaelCoin.deployed();
  console.log("RaphaelCoin deployed to:", raphaelCoin.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

## 常見錯誤及避免方法
- **網絡配置錯誤**：確保 Hardhat 配置文件中的網絡設置正確，並且節點已啟動。
- **合約編譯失敗**：在部署前先編譯合約，檢查編譯錯誤。
- **環境變量未設置**：確保所有必要的環境變量（如私鑰）已正確設置。