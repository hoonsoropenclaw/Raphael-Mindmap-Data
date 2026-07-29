# Ethereum Smart Contract Development with Solidity and Hardhat

## Target Skill: ethereum_smart_contract_development

### Summary
This skill focuses on developing and deploying ERC-20 smart contracts using Solidity and Hardhat. It covers writing Solidity code that adheres to the ERC-20 standard, leveraging OpenZeppelin for standardized implementations, and deploying contracts using Hardhat with proper environment configurations.

---

## 1. Solidity ERC-20 Smart Contract Development

### 1.1 Overview
Learn to write ERC-20 compliant smart contracts in Solidity, utilizing OpenZeppelin for standardized functionalities. This includes defining token properties, minting initial supplies, and ensuring secure and efficient contract design.

### 1.2 Key Components

#### 1.2.1 Importing OpenZeppelin ERC20
To leverage the standardized ERC20 implementation, import the OpenZeppelin ERC20 contract.

```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
```

#### 1.2.2 Contract Structure
Create a new contract that inherits from OpenZeppelin’s ERC20 contract. Define a constructor to set the token name, symbol, and initial supply.

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

### 1.3 Common Errors and Prevention

- **Incorrect Inheritance**: Ensure proper inheritance from the ERC20 contract. Use `is ERC20` in the contract declaration.
  
  ```solidity
  contract RaphaelCoin is ERC20 { ... }
  ```

- **Missing Token Details**: Always set the token name and symbol in the constructor.

  ```solidity
  ERC20("RaphaelCoin", "RPC")
  ```

- **Incorrect Minting Function**: Use the `_mint` function with the correct parameters (recipient and amount).

  ```solidity
  _mint(msg.sender, initialSupply);
  ```

- **Compiler Version Mismatch**: Ensure the Solidity version specified in the pragma matches the version compatible with OpenZeppelin.

---

## 2. Hardhat Deployment Script

### 2.1 Overview
Understand how to configure, write, and execute deployment scripts using Hardhat. This includes setting up the development environment, compiling contracts, and deploying them to Ethereum or other EVM-compatible networks.

### 2.2 Key Components

#### 2.2.1 Hardhat Configuration
Set up the Hardhat environment by creating a `hardhat.config.js` file. Configure network settings and compiler options.

```javascript
require("@nomiclabs/hardhat-waffle");

module.exports = {
  solidity: "0.8.0",
  networks: {
    rinkeby: {
      url: "https://rinkeby.infura.io/v3/YOUR_INFURA_KEY",
      accounts: ["YOUR_PRIVATE_KEY"]
    }
  }
};
```

#### 2.2.2 Deployment Script
Write a deployment script to deploy the ERC-20 contract. Use Hardhat’s contract factory and deploy method.

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

### 2.3 Common Errors and Prevention

- **Network Configuration Issues**: Verify that the network URL and accounts are correctly set in `hardhat.config.js`. Ensure the node is running if using a local network.

- **Contract Compilation Errors**: Before deploying, compile the contracts using `npx hardhat compile` and address any compilation issues.

- **Missing Environment Variables**: Securely manage private keys and API keys using environment variables or a `.env` file with the `dotenv` package.

  ```javascript
  require("dotenv").config();
  const privateKey = process.env.PRIVATE_KEY;
  ```

- **Insufficient Funds**: Ensure the deployment account has sufficient funds on the target network.

---

## 3. Best Practices and Security Considerations

### 3.1 Code Security
- **Use OpenZeppelin Libraries**: Leverage audited libraries like OpenZeppelin to ensure secure and reliable contract functionalities.
- **Avoid Hardcoding Values**: Use variables and configuration files for values like initial supply to enhance flexibility and security.

### 3.2 Deployment Security
- **Protect Private Keys**: Never expose private keys in code or commit them to version control. Use environment variables and secure storage solutions.
- **Test Networks First**: Deploy to test networks (e.g., Rinkeby, Ropsten) before moving to the mainnet to identify and fix issues.

### 3.3 Testing
- **Write Unit Tests**: Use Hardhat’s testing framework to write comprehensive tests for your contracts.
- **Continuous Integration**: Implement CI/CD pipelines to automate testing and deployment processes.

---

By mastering these components, you will be well-equipped to develop and deploy ERC-20 smart contracts using Solidity and Hardhat, ensuring both functionality and security in your blockchain applications.