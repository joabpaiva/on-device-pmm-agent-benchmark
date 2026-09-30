The paper tests the Aurora 14 AI Workstation on three on-device AI workloads against one competitor, the Vantage Pro 16. Only its base configuration was tested (64 GB, 24 GB GPU). Aurora units were pre-production. Three units per configuration were tested, and the median is reported. Tests ran at 22 °C, on AC power unless stated, in "Best performance" mode. Language models ran 4-bit quantized. Speed was measured, not output quality.

With an 8B model, the systems were comparable (38 vs 41 tokens/sec). With a 30B model, the 32 GB Aurora reached 6, the 128 GB Aurora 17, and the Vantage 15. The Vantage was faster at image generation (100 images, 1024×1024): 4.1 vs 5.3 seconds per image. In 40 minutes of continuous 8B inference, both slowed after about 20 minutes. The Aurora settled about 12% lower and the Vantage about 9% lower. In a scripted 45-minute CAD-plus-assistant session, the 128 GB unit kept the assistant loaded. The 32 GB unit unloaded it twice, with about eight seconds of reload delay each time. The 11-hour battery rating is for video playback (150 nits, Wi-Fi off). Continuous inference on battery lasted 2 hours 40 minutes. There was no Vantage battery test.

Key messages:

- Memory capacity, more than processor speed, decided which models ran well. Size memory to the largest model the team expects to use.
- The 128 GB Aurora ran the 30B model faster than the tested competitor (17 vs 15 tokens/sec), on pre-production units.
- Image-generation buyers may find the Vantage faster. Sustained speeds run below peak.

(About 245 words in total, bullets included.)