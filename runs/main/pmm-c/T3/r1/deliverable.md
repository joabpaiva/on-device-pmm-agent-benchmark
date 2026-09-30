This paper tests the Aurora 14 AI Workstation on three on-device AI workloads against one competitor: the Vantage Pro 16, base configuration only (64 GB, 24 GB GPU). Aurora units were pre-production. Three units per configuration were tested, and the median is reported. Tests ran at 22 °C, on AC power, in default "Best performance" mode. Language models were 4-bit quantized. The authors measured speed, not output quality.

Results: With an 8B model, the base Aurora and the Vantage were comparable (38 vs 41 tokens/sec). With a 30B model, the Aurora 32 GB reached 6 tokens/sec, the Aurora 128 GB reached 17, and the Vantage reached 15. The Vantage generated images faster (4.1 vs 5.3 seconds). Running the 8B model for 40 minutes, both systems slowed after about 20 minutes. The Aurora settled about 12% below its initial throughput, and the Vantage about 9%. In a scripted 45-minute CAD-plus-assistant session, the 128 GB Aurora kept the assistant loaded. The base unit unloaded it twice, with a reload delay of about eight seconds each time. The 11-hour battery rating is for video playback (150 nits, Wi-Fi off). Continuous inference on battery ran 2 hours 40 minutes. Vantage battery life was not tested.

Key messages:
- Memory capacity, more than processor speed, determines which models run well on the device. Size memory to the largest model the team expects to use.
- The Aurora 14 at 128 GB ran the 30B model faster than the tested competitor (17 vs 15 tokens/sec). This comes from pre-production units, and retail units may differ.
- The Vantage Pro 16 was faster at image generation, where GPU capability matters most.

By my count this is about 235 words, bullets included.