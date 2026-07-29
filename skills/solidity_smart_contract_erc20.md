# Solidity ERC-20 Smart Contract

## 說明
此技能涵蓋使用 Solidity 編寫符合 ERC-20 標準的智能合約，包括以下內容：
- 繼承 OpenZeppelin 的 ERC20 合約以利用其標準實現。
- 定義合約的構造函數以設置代幣名稱、符號和初始供應量。
- 使用 `_mint` 函數來鑄造初始供應量的代幣並分配給合約部署者。

## 關鍵代碼片段
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract RaphaelCoin is ERC20 {
    constructor(uint256 initialSupply) ERC20("RaphaelCoin", "RPC") {
        _mint(msg.sender, initialSupply);
    }
}
```

## 常見錯誤及避免方法
- **未正確繼承 ERC20 合約**：確保使用正確的繼承語法並導入 OpenZeppelin 的 ERC20 合約。
- **未設置代幣名稱和符號**：在構造函數中正確設置代幣的名稱和符號。
- **鑄幣函數使用錯誤**：使用 `_mint` 函數時，確保傳遞正確的參數，例如接收者和數量。