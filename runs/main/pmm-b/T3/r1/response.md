**Executive Summary for VP Audience**

This evaluation tested the Aurora 14 AI Workstation (32 GB and 128 GB configurations) against a single Vantage Pro 16 configuration (64 GB) on three on-device AI workloads. All Aurora 14 units were pre-production; final retail performance may differ. Sample sizes were three units per configuration, limiting statistical breadth.

For 8-billion-parameter language models, both systems performed comparably (Aurora 14: 38 tokens/sec; Vantage Pro 16: 41 tokens/sec). For the larger 30-billion-parameter model, memory capacity proved decisive. The Aurora 14 (32 GB) dropped to 6 tokens/sec due to memory constraints, while the high-memory Aurora 14 (128 GB) reached 17 tokens/sec, outperforming the Vantage Pro 16 (15 tokens/sec). Note that all language model tests used 4-bit quantization; output quality was not evaluated.

The Vantage Pro 16 was faster at image generation (4.1 seconds per image vs. 5.3 seconds for Aurora 14), attributed to its larger GPU. In sustained 40-minute tests, both systems throttled after ~20 minutes due to thermal limits (Aurora 14: -12% throughput; Vantage Pro 16: -9%).

In a scripted AI-assisted design session, the Aurora 14 high-memory configuration kept the AI assistant resident in memory, while the base configuration unloaded it twice, adding ~8-second reload delays. Battery life under continuous language model inference was 2 hours 40 minutes for the Aurora 14; this does not reflect the 11-hour video playback rating (measured at 150 nits, Wi-Fi off). The Vantage Pro 16 battery was not tested.

**Key Messages**

*   Memory capacity is the primary determinant for running large language models on-device; the Aurora 14 high-memory configuration outperformed the tested competitor on 30B models, while both systems were comparable on 8B models.
*   The competing Vantage Pro 16 holds a clear advantage for image generation workloads due to its larger GPU, averaging 4.1 seconds per image versus 5.3 seconds for the Aurora 14.
*   Sustained performance degrades for both systems after ~20 minutes due to thermal limits, and battery life under AI workloads (2h 40m for Aurora 14) is significantly lower than standard video playback ratings.