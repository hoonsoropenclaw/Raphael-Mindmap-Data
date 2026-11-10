# ✗ D2 dead token：--border-strong 定義但無任何 var() 引用

`tests/defects.e2e.ts` · failed · 271ms

Ran on: browser `chromium 156.0.8078.4` · user agent `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/156.0.8078.4 Safari/537.36`

**ASSERTION_FAILED**

```text
expected true to be false
```

Look at: `tests/defects.e2e.ts:83`  

## Steps

1. ✓ `app.open` `/` (101ms) — `tests/defects.e2e.ts:79`
   - screen: 100 nodes at `/`
2. ✓ `browser.evaluate` (4ms) — `tests/defects.e2e.ts:80`

## Screen at failure

`http://127.0.0.1:8932/` · viewport 1280x720 · 100 nodes  

![screenshot at failure](attempt-1/screenshots/001-failure.png)

The screen as the agent reads it, one node per line: `#id role "name" text="…" [states]`.

```text
#root document "服務品質儀表板 — 設計 token 重構（AFTER）"
 #n2 complementary
  #n3 heading "服務品質儀表板"
  #n4 navigation "主導覽"
   #n5 link "總覽"
   #n6 link "案件量"
   #n7 link "滿意度"
   #n8 link "人力配置"
   #n9 link "系統LOG"
  #n10 text="本季目標"
  #n11 text="87%"
 #n12 main
  #n13 heading "113 年度第 2 季服務品質總覽"
  #n14 text="資料期間 113/04/01–113/06/30 · 統計單位：件 · 更新時間 113/07/05"
  #n15 button "切換深色模式"
  #n16 button "匯出報表"
  #n17 region "關鍵指標"
   #n18 article
    #n19 text="案件總數"
    #n20 text="4,812"
    #n21 text="▲ 6.2% 較上季"
   #n22 article
    #n23 text="平均處理天數"
    #n24 text="3.4"
    #n25 text="▼ 0.6 天（改善）"
   #n26 article
    #n27 text="滿意度"
    #n28 text="87.2%"
    #n29 text="▼ 1.8 百分點"
   #n30 article
    #n31 text="超時案件"
    #n32 text="43"
    #n33 text="▲ 12 件"
  #n34 heading "各處室案件處理概況"
  #n35 table "超時率門檻 5%；資料來源：服務系統 113/07/05 匯出"
   #n36 text="超時率門檻 5%；資料來源：服務系統 113/07/05 匯出"
   #n37 rowgroup
    #n38 row "處室 案件數 平均天數 超時率 狀態"
     #n39 columnheader "處室"
     #n40 columnheader "案件數"
     #n41 columnheader "平均天數"
     #n42 columnheader "超時率"
     #n43 columnheader "狀態"
   #n44 rowgroup
    #n45 row "人事室 1,204 2.8 0.8% 達標"
     #n46 cell "人事室"
     #n47 cell "1,204"
     #n48 cell "2.8"
     #n49 cell "0.8%"
     #n50 cell "達標"
      #n51 text="達標"
    #n52 row "總務室 986 3.9 2.1% 達標"
     #n53 cell "總務室"
     #n54 cell "986"
     #n55 cell "3.9"
     #n56 cell "2.1%"
     #n57 cell "達標"
      #n58 text="達標"
    #n59 row "學務組 842 5.4 4.7% 觀察"
     #n60 cell "學務組"
     #n61 cell "842"
     #n62 cell "5.4"
     #n63 cell "4.7%"
     #n64 cell "觀察"
      #n65 text="觀察"
    #n66 row "總務處櫃台 711 4.2 3.3% 達標"
     #n67 cell "總務處櫃台"
     #n68 cell "711"
     #n69 cell "4.2"
     #n70 cell "3.3%"
     #n71 cell "達標"
      #n72 text="達標"
    #n73 row "資訊維運 634 6.8 7.9% 超標"
     #n74 cell "資訊維運"
     #n75 cell "634"
     #n76 cell "6.8"
     #n77 cell "7.9%"
     #n78 cell "超標"
      #n79 text="超標"
    #n80 row "財產管理 435 3.1 1.4% 達標"
     #n81 cell "財產管理"
     #n82 cell "435"
     #n83 cell "3.1"
     #n84 cell "1.4%"
     #n85 cell "達標"
      #n86 text="達標"
  #n87 text="合計 4,812 件 · 4 個處室達標、1 個觀察、1 個超標"
  #n88 text="重點說明：資訊維運組超時率 7.9%，為唯一超過 5% 門檻的處室， 其案件平均處理天數 6.8 天亦為全組最高，建議列為第 3 季專案追蹤。"
  #n89 heading "設計 token 與色階"
  #n90 text="全部決策集中在 @layer theme；元件只引用 var(--semantic-role)。 灰階全系統鎖定色相 H=250 相鄰級距視覺等距（OKLCH 感知均勻）。"
  #n91 "中性色階"
   #n92 box
   #n93 box
   #n94 box
   #n95 box
   #n96 box
   #n97 box
   #n98 box
   #n99 box
   #n100 box
```

## Evidence

- [screenshot](attempt-1/screenshots/001-failure.png) `.e2e/results/defects-d2-dead-token-border-strong-var-775104585b3b8c1f/attempt-1/screenshots/001-failure.png`
- [screen](attempt-1/screen-at-failure.txt) `.e2e/results/defects-d2-dead-token-border-strong-var-775104585b3b8c1f/attempt-1/screen-at-failure.txt`

<sub>e2e 0.23.0 · run `01a1c79c-9fde-7479-affb-9cebe9470ab3` · the whole run is in `report.json`</sub>
