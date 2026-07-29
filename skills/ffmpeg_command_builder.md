# FFmpeg Command Builder

## 說明
此微技能根據提供的配置檔案生成 FFmpeg 命令，適用於需要自動化視頻處理的場景。

## 關鍵程式碼片段
```python
def to_ffmpeg_output_args(self, output_path: Path) -> list[str]:
    """編譯 profile → ffmpeg 後段 args (-i 之後的參數)"""
    args: list[str] = []
    if self.video_codec:
        args += ["-c:v", self.video_codec]
        if self.crf is not None:
            args += ["-crf", str(self.crf)]
        elif self.video_bitrate:
            args += ["-b:v", self.video_bitrate]
        if self.preset:
            args += ["-preset", self.preset]
        if self.scale:
            args += ["-vf", f"scale={self.scale}"]
        if self.fps:
            args += ["-r", str(self.fps)]
        if self.pix_fmt:
            args += ["-pix_fmt", self.pix_fmt]
    if self.audio_codec:
        args += ["-c:a", self.audio_codec]
        if self.audio_bitrate:
            args += ["-b:a", self.audio_bitrate]
    args += list(self.extra_args)
    args += ["-y", str(output_path)]
    return args
```

## 常見錯誤及避免方法
1. **參數錯誤**: 確保所有 FFmpeg 參數正確無誤，避免因參數錯誤導致命令執行失敗。
2. **路徑處理**: 處理輸出路徑時需考慮檔案系統權限和路徑有效性。