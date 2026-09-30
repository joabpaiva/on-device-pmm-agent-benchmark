Summary

This paper tests the Aurora 14 AI Workstation on three on-device AI workloads against one competitor, the Vantage Pro 16 (base configuration only, 64 GB, 24 GB GPU). The Aurora 14 was tested at 32 GB and 128 GB, with three pre-production units each and the median reported. Final retail units may differ.

Language models ran 4-bit quantized. Only speed was measured, not output quality. With an 8B model, the Aurora 14 base and the Vantage were comparable (38 vs 41 tokens/sec). With a 30B model, the Aurora 14 at 32 GB reached 6 tokens/sec, the Aurora 14 at 128 GB reached 17, and the Vantage reached 15.

Image generation (100 images, 1024×1024): the Vantage was faster, at 4.1 vs 5.3 seconds per image.

In a 40-minute 8B run, both systems slowed after about 20 minutes. The Aurora 14 settled about 12% below its initial throughput and the Vantage about 9%. Expect sustained speeds below peak.

In a scripted 45-minute CAD-plus-assistant session, the 128 GB unit kept the assistant loaded. The 32 GB unit unloaded it twice, with about eight seconds to reload each time.

The 11-hour battery rating is for video playback at 150 nits with Wi-Fi off. Continuous local inference on battery lasted 2 hours 40 minutes. Vantage battery life was not tested.

Tests ran at 22 °C, on AC power unless stated, in default "Best performance" mode.

Key messages

- Memory decides which models run well: the 128 GB Aurora 14 beat the tested competitor on the 30B model (17 vs 15 tokens/sec).
- The competitor is faster at image generation, where GPU capability matters most.
- Treat results as preliminary: pre-production units, three per configuration, one competitor configuration.

(About 245 words in total, including the key messages.)