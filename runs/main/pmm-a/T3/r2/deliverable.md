The Aurora 14 AI Workstation's performance on local AI workloads depends heavily on memory capacity, not just processor speed. Testing pre-production units showed the base 32 GB model bottlenecked on larger language models, while the 128 GB high-memory configuration matched and exceeded competitor speeds on those same models. However, the Aurora 14 trailed a competitor in image generation, which heavily favors GPU capability. After 20 minutes of continuous operation, both systems slowed by roughly 9–12% due to thermal limits, and unquantified local AI workloads drained the Aurora 14's battery in about 2 hours 40 minutes.

## Key Messages

*   Base 32 GB cannot run 30B parameter models fully in fast memory; throttled to 6 tokens/sec versus 17 tokens/sec on 128 GB and 15 tokens/sec on competitor.
*   128 GB configuration ran 30B parameter model at 17 tokens/sec, outperforming competitor's 64 GB (15 tokens/sec).
*   Image generation at 1024 × 1024 took longer (5.3s) than competitor (4.1s); competitors with larger, faster GPUs dominate this workload.