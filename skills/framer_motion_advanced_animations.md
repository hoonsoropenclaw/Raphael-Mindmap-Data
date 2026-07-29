# framer_motion_advanced_animations

## 說明
在 React 應用中整合 Framer Motion，實現交錯動畫及自訂動畫邊線效果。Framer Motion 是一個強大的動畫庫，能夠輕鬆地為 React 組件添加動畫效果。通過使用 Framer Motion，可以實現複雜的動畫效果，如交錯動畫和自訂動畫邊線效果。

## 關鍵代碼片段或模式

### 交錯動畫
交錯動畫是指多個元素按照一定的順序或時間間隔依次觸發動畫效果。以下是一個實現交錯動畫的範例：

```javascript
import { motion, AnimatePresence } from 'framer-motion';

const items = [1, 2, 3, 4, 5];

function StaggeredAnimation() {
  return (
    <AnimatePresence>
      {items.map((item, index) => (
        <motion.div
          key={item}
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          transition={{ duration: 0.5, delay: index * 0.2 }}
        >
          {item}
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
```

### 自訂動畫邊線效果
使用 Framer Motion 實現自訂動畫邊線效果，例如動態繪製邊線或邊線顏色變化。以下是一個實現動態繪製邊線的範例：

```javascript
import { motion } from 'framer-motion';

function AnimatedEdge({ source, target, strokeWidth, strokeColor }) {
  const pathVariants = {
    initial: {
      pathLength: 0,
      pathOffset: 0,
    },
    animate: {
      pathLength: 1,
      pathOffset: 1,
      transition: {
        duration: 2,
        ease: 'easeInOut',
      },
    },
  };

  return (
    <svg>
      <motion.path
        d={`M ${source.x} ${source.y} L ${target.x} ${target.y}`}
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        initial="initial"
        animate="animate"
        variants={pathVariants}
      />
    </svg>
  );
}
```

## 常見錯誤及避免方法

### 錯誤: 動畫效果不觸發或無法正確渲染
- **解決方法**: 
  - 確認 Framer Motion 的版本是否與 React 版本兼容。
  - 檢查是否正確導入 `motion` 和其他必要的 Framer Motion 組件。
  - 確保動畫屬性（如 `initial`, `animate`, `transition`）設置正確。

### 錯誤: 動畫效果不流暢或出現卡頓
- **解決方法**: 
  - 優化動畫邏輯，減少不必要的重渲染。
  - 使用 `useMemo` 或 `React.memo` 來優化組件渲染。
  - 考慮使用 `useReducedMotion` 來處理用戶的動畫偏好設置。

### 錯誤: 邊線樣式不生效
- **解決方法**: 
  - 檢查邊線樣式定義，確保 `stroke`, `strokeWidth` 等屬性正確應用。
  - 確認 SVG 元素是否正確嵌套，並且沒有 CSS 衝突。
  - 使用瀏覽器的開發者工具檢查實際應用的樣式，確保沒有被其他樣式覆蓋。

### 錯誤: 交錯動畫順序錯誤或延遲設置不當
- **解決方法**: 
  - 確認 `transition` 中的 `delay` 設置是否正確，確保每個元素的動畫順序和時間間隔符合預期。
  - 使用 `AnimatePresence` 來處理元素的進入和退出動畫，確保動畫順序的正確性。

## 總結
通過整合 Framer Motion，開發者可以輕鬆地在 React 應用中實現各種複雜的動畫效果。關鍵在於正確設置動畫屬性，優化動畫邏輯，並注意常見的錯誤和解決方法。掌握這些技巧後，可以大大提升應用的用戶體驗和視覺效果。