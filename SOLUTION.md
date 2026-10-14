# Lab 6 — REST vs. gRPC Measurements


| Method | Local (ms) | Same-Zone (ms) | Different Region (ms) |
|---|---:|---:|---:|
| REST add | 3.155 | 3.758 | 341.951 |
| gRPC add | 0.753 | 1.298 | 161.560 |
| REST rawimg | 4.725 | 7.479 | 1,379.959 |
| gRPC rawimg | 6.944 | 5.630 | 167.666 |
| REST dotproduct | 3.282 | 3.888 | 330.421 |
| gRPC dotproduct | 0.813 | 1.303 | 142.908 |
| REST jsonimg | 31.125 | 32.207 | 1,482.214 |
| gRPC jsonimg | 19.772 | 20.646 | 204.888 |
| **PING** | **0.053** | **0.751** | **159.817** |

## Observations

The clearest difference is how the APIs behave as network distance increases. On localhost, gRPC was faster for lightweight calls (`add`: 0.753 ms vs. 3.155 ms; `dotproduct`: 0.813 ms vs. 3.282 ms), while REST was actually faster for local raw-image processing (4.725 ms vs. 6.944 ms). Moving to a second VM in the same zone added relatively little latency, which agrees with the low 0.751 ms average ping. 

The Oregon-to-Frankfurt ping averaged 159.817 ms, and RPC latency rose sharply. REST `add` took 341.951 ms versus gRPC's 161.560 ms; for raw images, the difference was even larger (1,379.959 ms vs. 167.666 ms). 

I think it is because the benchmark's REST client establishes a new TCP connection for each request, whereas gRPC reuses a persistent connection, making connection setup particularly costly over long distances. `jsonImage` was slower than `rawImage` in all three configurations, consistent with additional Base64/JSON data and processing overhead. Overall, these results favor gRPC in this setup, especially across regions, but they do not isolate connection reuse from all other client, serialization, and network costs. Bandwidth was not directly measured.
