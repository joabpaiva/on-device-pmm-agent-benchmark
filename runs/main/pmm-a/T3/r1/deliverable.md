On-Device AI Workload Performance on the Aurora 14 AI Workstation

The paper evaluates the Aurora 14 AI Workstation on three on-device AI workloads: language model inference, image generation, and a mixed AI-assisted design workflow. Results depend on configuration and workload type. The evaluation used three pre-production units of the Aurora 14 in 32 GB and 128 GB configurations, and one 64 GB Vantage Pro 16 (Vireo V9000 GPU, 24 GB VRAM) unit. Language models were run in 4-bit quantized form; output quality was not evaluated.

- 8-billion parameter model: Aurora 14 (both configurations) and Vantage Pro 16 achieved similar throughput (median 38 vs 41 tokens/sec). Time to first token was under two seconds on all systems.
- 30-billion parameter model: Aurora 14 32 GB reached 6 tokens/sec due to slow memory fallback; 128 GB reached 17 tokens/sec. Vantage Pro 16 reached 15 tokens/sec.
- Image generation: Vantage Pro 16 averaged 4.1 seconds/image vs Aurora 14’s 5.3 seconds (1024×1024). GPU capability was the deciding factor.
- Sustained performance: After 40 minutes of continuous 8B inference, both systems slowed; Aurora 14 settled at ~12% below peak, Vantage Pro 16 at ~9%.
- AI-assisted design (45 minutes): Aurora 14 128 GB kept CAD and AI assistant resident; 32 GB unloaded the assistant twice with ~8 second delays.
- Battery: Aurora 14 delivered 2 hours 40 minutes on continuous local inference; rated 11 hours is for 150-nits video playback with Wi‑Fi off.

Limitations: pre‑production units; three units per configuration; single competitor configuration; quantized models; sustained workloads slower than peak; video‑playback battery rating.