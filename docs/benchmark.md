# Benchmarking and validation

本專案目前沒有在固定資料集與固定硬體上提交正式 benchmark，因此 README 不虛構準確率或推論延遲。建議以相同資料集、相同解析度與相同推論裝置重複以下實驗。

## Suggested metrics

| Metric | Definition | Result |
| --- | --- | --- |
| Dice classification accuracy | 正確骰子類型與等級數 / 總樣本數 | 待實測 |
| Unknown/rejection rate | 低於 confidence threshold 而拒絕預測的比例 | 待實測 |
| Dice inference latency | 單張盤面或單批次分類平均耗時 | 待實測 |
| OCR success rate | 正確讀取房號、波次與畫面文字的比例 | 待實測 |
| Board parsing latency | 截圖到建立 `3 × 5 × 2` 盤面狀態的耗時 | 待實測 |
| Long-running stability | 連續執行時間與異常恢復次數 | 待實測 |

## Reproducible protocol

1. 固定 Emulator 解析度、Windows DPI scaling 與模型版本。
2. 建立包含不同波次、骰子種類、等級及背景畫面的標註資料集。
3. 分別記錄 GPU 與 CPU 的推論延遲，至少重複 100 次並排除第一次模型載入時間。
4. 對低信心預測記錄 rejection rate，不要只報告 accuracy。
5. 以實際遊戲流程記錄房號辨識、盤面辨識、操作成功率與連續運行時間。
6. 將硬體、Python、PyTorch、CUDA、模型版本與測試日期一併寫入結果。

## Reporting template

```text
Date: YYYY-MM-DD
OS / Python:
CPU / GPU:
Emulator resolution:
Model checkpoint:
Dice accuracy:
Dice rejection rate:
Average inference latency:
OCR success rate:
Continuous runtime:
Notes:
```
