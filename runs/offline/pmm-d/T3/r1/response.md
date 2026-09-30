**On-Device AI Workload Performance: An Evaluation of the Aurora 14 AI Workstation**

Engineering and design teams are increasingly running AI models locally to protect sensitive files, ensure offline access, and avoid cloud charges. This paper evaluates the Aurora 14 AI Workstation on three workloads: language model inference, image generation, and an AI-assisted design session.

Testing was performed on pre-production units of the Aurora 14 (32 GB and 128 GB configurations) against a single Vantage Pro 16 configuration (64 GB, Vireo V9000 GPU). We tested three units per configuration and report median results.

**Language Model Inference:** With an 8B model, the Aurora 14 base (32 GB) matched the Vantage Pro 16 at 38 vs. 41 tokens per second. With a 30B model, memory capacity drove performance. The Aurora 14 base (32 GB) reached only 6 tokens per second due to slower memory paths, while the high-memory configuration (128 GB) reached 17 tokens per second, outperforming the Vantage Pro 16 at 15 tokens per second.

**Image Generation:** The Vantage Pro 16 averaged 4.1 seconds per 1024 × 1024 image versus 5.3 seconds for the Aurora 14, attributed to the competitor's larger and faster GPU.

**Sustained Performance:** Continuous 40-minute runs showed thermal throttling for both systems. The Aurora 14 settled at 12% below initial throughput, while the Vantage Pro 16 settled at 9%.

**AI-Assisted Design:** The high-memory Aurora 14 configuration sustained a CAD and AI assistant workflow without unloading the assistant. The base configuration unloaded the assistant twice, adding eight-second reload delays.

**Battery Behavior:** Under continuous local language model inference on battery, the Aurora 14 ran for 2 hours and 40 minutes. This differs from the manufacturer's 11-hour video playback rating.

**Conclusion:** The Aurora 14 high-memory configuration is capable for on-device AI, running large models faster than the tested competitor. However, buyers focused primarily on image generation may prefer the Vantage Pro 16's superior GPU.

***

**Key Messages**
*   Memory capacity, more than raw processor speed, determines which AI models the Aurora 14 can run efficiently; the 32 GB base configuration could not run a 30B model effectively, while the 128 GB high-memory configuration performed best on that workload.
*   For image generation, GPU capability dominates performance, with the tested Vantage Pro 16 configuration (4.1 seconds per image) outperforming the Aurora 14 (5.3 seconds per image).
*   Sustained AI workloads for both systems run slower than peak results due to thermal limits, with the Aurora 14 settling at 12% below initial throughput after 20 minutes of continuous inference.