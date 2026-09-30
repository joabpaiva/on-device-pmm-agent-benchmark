This white paper evaluates the Aurora 14 AI Workstation's performance on three on-device AI workloads. Testing was conducted on pre-production units with a small sample size (three units per configuration), and final retail performance may differ.

The study tested an 8B and 30B parameter language model in 4-bit quantized form, image generation, and a 45-minute AI-assisted design session. All tests ran at 22°C on AC power in "Best performance" mode except where noted.

For 8B language model inference, the Aurora 14 base configuration (32 GB) and the competitor Vantage Pro 16 (64 GB) achieved comparable speeds of 38 and 41 tokens per second, respectively. The 30B model's performance was memory-dependent: the Aurora 14 base fell back to slower paths at 6 tokens per second, the high-memory configuration (128 GB) reached 17 tokens per second, and the Vantage Pro 16 reached 15 tokens per second.

In image generation, the Vantage Pro 16 averaged 4.1 seconds per image compared to the Aurora 14's 5.3 seconds, attributed to the competitor's larger and faster GPU.

During sustained 40-minute testing of the 8B model, both systems throttled after 20 minutes. The Aurora 14 settled at 12% below initial throughput, while the Vantage Pro 16 settled at 9% below.

In a 45-minute AI-assisted design session, the Aurora 14 high-memory configuration maintained both the CAD application and AI assistant in memory. The base configuration unloaded the assistant twice, adding eight seconds of delay each time.

On battery, the Aurora 14 delivered 2 hours and 40 minutes of continuous 8B language model inference, versus its rated 11 hours of video playback at 150 nits with Wi-Fi off.

*   Memory capacity determines which AI models run well on-device; the 128 GB configuration outperformed the 32 GB and a 64 GB competitor on large language models, while the 32 GB configuration fell back to slower system paths with the 30B model.
*   GPU capability is the deciding factor for image generation, where the Vantage Pro 16 was 22% faster than the Aurora 14.
*   Sustained performance degrades under long runs; both systems slowed by 9-12% after 20 minutes, and the Aurora 14's base configuration required a high-memory configuration to keep AI assistants responsive alongside CAD workloads.