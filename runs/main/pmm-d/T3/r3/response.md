**On-Device AI Workload Performance Summary**

This white paper evaluates the Aurora 14 AI Workstation against the Vantage Pro 16 across three on-device AI workloads: language model inference, image generation, and AI-assisted design. Testing used pre-production units; final retail performance may differ.

Language model inference depends primarily on memory, not raw processor speed. With the 8-billion-parameter model, systems performed comparably. With the 30-billion-parameter model, the Aurora 14 high-memory configuration (128 GB) achieved 17 tokens per second, while the base configuration (32 GB) dropped to 6 tokens per second due to slower memory paths. The Vantage Pro 16 (64 GB) reached 15 tokens per second. Models were tested in 4-bit quantized form only; output quality was not evaluated.

Image generation is GPU-dependent. The Vantage Pro 16 averaged 4.1 seconds per 1024×1024 image, versus 5.3 seconds for the Aurora 14, due to the Vantage Pro 16’s larger, faster GPU.

In a 45-minute AI-assisted design session, the Aurora 14 high-memory configuration kept the local AI assistant resident alongside a CAD application. The base configuration unloaded the assistant twice, adding about eight seconds of reload delay each time.

Sustained performance declined for both systems after 20 minutes of continuous inference: Aurora 14 slowed 12% below initial throughput, Vantage Pro 16 slowed 9%.

Battery life under AI workloads is limited: the Aurora 14 ran for 2 hours and 40 minutes on continuous local language model inference. This is significantly lower than the 11-hour video playback rating, measured with Wi-Fi off at 150 nits brightness.

**Key Messages:**

*   Memory capacity determines which AI models can run effectively on the device; the 128 GB configuration outperformed the 64 GB Vantage Pro 16 with the 30-billion-parameter model.
*   GPU capability drives image generation performance; the Vantage Pro 16 was faster for this workload.
*   Sustained performance drops 9–12% after 20 minutes, and battery life under AI inference is approximately 2 hours and 40 minutes on battery.