**Summary**

This white paper evaluates the Aurora 14 AI Workstation for on-device AI by testing three workloads: 8B and 30B language models, image generation, and a 45-minute AI-assisted design session. The study used pre-production units (three per configuration) on a hard desk at 22°C in "Best performance" mode, reporting median results.

For 8B language models, the Aurora 14 base (32 GB) matched a Vantage Pro 16 (64 GB) at 38–41 tokens/second. For the 30B model, performance depended on memory: the Aurora 14 base fell back to slower paths at 6 tokens/second, while the high-memory (128 GB) version reached 17 tokens/second, faster than the Vantage Pro 16’s 15 tokens/second. For image generation, the Vantage Pro 16 averaged 4.1 seconds/image versus the Aurora 14’s 5.3 seconds due to its larger GPU.

Both systems thermal throttled after ~20 minutes in a 40-minute 8B run (Aurora 14: -12%, Vantage Pro 16: -9%). In a 45-minute CAD session, the Aurora 14 high-memory kept the AI assistant resident; the base version unloaded it twice with ~8-second reload delays. On battery, the Aurora 14 ran 2h40m during 8B inference; the rated 11-hour video playback does not apply to AI workloads.

**Key Messages**

*   Memory capacity, not raw processor speed, determines which AI models a mobile workstation can run; larger models require the high-memory configuration (128 GB).
*   For image generation, GPU capability dominates performance; the tested competing system with a larger GPU was faster.
*   Sustained workloads slow by ~9–12% after 20 minutes, and the rated 11-hour battery life applies to video playback, not AI inference.