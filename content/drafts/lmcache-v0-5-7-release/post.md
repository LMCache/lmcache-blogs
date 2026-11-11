# LMCache v0.5.7: Safer Defaults, New Accelerators, and Native gRPC

By LMCache Team

The LMCache contributor team and community are pleased to announce LMCache v0.5.7, released on November 5, 2026.
It includes safer defaults for deployments, optional API key authentication, support for more accelerators, and new multiprocess (MP) transport modes.

If you run the official Docker images, read the upgrade notes before you upgrade.
The images no longer run as root.

## Safer defaults for deployments

The official Docker images now run as a non-root user by default ([#5685](https://github.com/LMCache/LMCache/pull/5685)).
The user is `lmcache`, with user ID (UID) 1000.

**Important: the official images now run as a non-root user. Check writable paths and mounted-volume permissions before you upgrade.**

With this change, LMCache in a container has only the access that UID 1000 has.
Build changes in [#6056](https://github.com/LMCache/LMCache/pull/6056) and [#6132](https://github.com/LMCache/LMCache/pull/6132) make the image build work for a non-root user.

The Hugging Face cache inside the container moves to `/home/lmcache/.cache/huggingface`.
If you mount a host directory there, UID 1000 must be able to read and write it.

## Optional API key authentication

LMCache v0.5.7 adds API key authentication to the MP HTTP server ([#5756](https://github.com/LMCache/LMCache/pull/5756)) and to the frontend HTTP API ([#5767](https://github.com/LMCache/LMCache/pull/5767)).
Both use one shared verifier and one set of configuration options ([#5779](https://github.com/LMCache/LMCache/pull/5779)).

Authentication is off until you configure a key.
To turn it on, give the server a key file:

```
lmcache server --api-key-file /run/secrets/lmcache-api-key
```

You can also set `LMCACHE_API_KEY_FILE` or `LMCACHE_API_KEY`.
All key sources add to one set of accepted keys.
This lets you rotate keys: add the new key, move clients to it, and then remove the old key.

Clients send the key in the `Authorization: Bearer <key>` header, or in the `X-LMCache-API-Key` header when a proxy uses `Authorization` for itself.
The `/` and `/healthcheck` routes stay public, so liveness and readiness probes still work.

The coordinator uses the same `--api-key-file` option, and it sends the configured key on its own outbound requests ([#6174](https://github.com/LMCache/LMCache/pull/6174)).
In the words of the change: "An unset flag leaves the coordinator open; supplying a key closes every route except /healthz."

## What this covers, and what it does not

API keys check who is calling.
They do not encrypt traffic.
If requests cross a network you do not trust, put Transport Layer Security (TLS) in front of LMCache at a trusted reverse proxy.

This release adds authentication to HTTP services.
It does not add authentication to the MP request transports, ZeroMQ (ZMQ) and gRPC.
Keep the transport port on a private network or on the local host.

## Upgrade notes for operators

Check these before you move to v0.5.7:

- Your container can write to every path LMCache uses as UID 1000.
- Host directories that you mount, such as a shared Hugging Face cache, are readable and writable by UID 1000.
- If you depend on a cache that was filled under `/root`, either move it or run the container as root on purpose (`docker run --user 0`, or `securityContext.runAsUser: 0` on Kubernetes).
- If you expose the MP HTTP server, the frontend, or the coordinator beyond the local host, decide whether to turn on API key authentication.
- If you used `--http-api-key-file` or `LMCACHE_HTTP_API_KEY`, these still work. The new `--api-key-file` and `LMCACHE_API_KEY` names apply to all HTTP services.

## Pickle removed from the tensor codec

Engine-driven transfers in MP mode no longer use Python `pickle` for tensor data ([#5699](https://github.com/LMCache/LMCache/pull/5699)).
A typed codec takes its place, and it rejects unknown fields.
New `pickle` imports are now blocked outside legacy code paths ([#5903](https://github.com/LMCache/LMCache/pull/5903)).

## Bounded authentication replies

LMCache now limits the length of an authentication reply in the Redis serialization protocol (RESP) ([#6108](https://github.com/LMCache/LMCache/pull/6108)).

## Kubernetes example bound to localhost

The MP example Kubernetes deployment now binds the LMCache transport port to `127.0.0.1` ([#5684](https://github.com/LMCache/LMCache/pull/5684)).
vLLM pods connect over the node's loopback interface, so the transport port is not exposed beyond the node.

## Hardware and software in this release

### Hardware

| Platform | What is new or improved | PRs |
|---|---|---|
| Biren SUPA | New platform support | [#5420](https://github.com/LMCache/LMCache/pull/5420) |
| AWS Trainium (Neuron) | KV caching in MP mode | [#5359](https://github.com/LMCache/LMCache/pull/5359) |
| Cambricon MLU | New platform support | [#6023](https://github.com/LMCache/LMCache/pull/6023) |
| Ascend | Mamba model support; KV groups split by physical block stride | [#5702](https://github.com/LMCache/LMCache/pull/5702), [#6127](https://github.com/LMCache/LMCache/pull/6127) |
| Rebellions neural processing unit (NPU, RBLN) | Blocks-first KV layout in vLLM-RBLN; wheels built and published on GitHub Releases | [#5748](https://github.com/LMCache/LMCache/pull/5748), [#6140](https://github.com/LMCache/LMCache/pull/6140) |
| MUSA | Unified KV format | [#5573](https://github.com/LMCache/LMCache/pull/5573) |
| Intel XPU | Release wheels aligned with vLLM v0.32.0 | [#6151](https://github.com/LMCache/LMCache/pull/6151) |
| AMD ROCm | Wheels built against PyTorch 2.13; fixes for registered-L1 compaction and `hipHostRegister` faults | [#6080](https://github.com/LMCache/LMCache/pull/6080), [#5710](https://github.com/LMCache/LMCache/pull/5710), [#5534](https://github.com/LMCache/LMCache/pull/5534) |
| Device-DAX and CXL memory | L1 offsets on Device-DAX and Compute Express Link (CXL) memory; range-based DAX L2 ownership | [#5874](https://github.com/LMCache/LMCache/pull/5874), [#5878](https://github.com/LMCache/LMCache/pull/5878) |

### Engines, storage, and platforms

| Platform | What is new or improved | PRs |
|---|---|---|
| SGLang | Kimi Linear support; direct-copy memory kernels | [#5892](https://github.com/LMCache/LMCache/pull/5892), [#6062](https://github.com/LMCache/LMCache/pull/6062) |
| DeepSeek V4 | Compressed KV groups in engine-driven transfers | [#6124](https://github.com/LMCache/LMCache/pull/6124) |
| TensorRT-LLM | Respects the kernel-object batch limit | [#5762](https://github.com/LMCache/LMCache/pull/5762) |
| NIXL | Pool capacity reported in allocation-slot units | [#5800](https://github.com/LMCache/LMCache/pull/5800) |
| HF3FS | Atomic object writes through temporary files | [#5808](https://github.com/LMCache/LMCache/pull/5808) |
| Amazon S3 | Wrongly sized L2 GET results treated as misses | [#6015](https://github.com/LMCache/LMCache/pull/6015) |
| Bigtable | Rejected L2 stores reported as failures | [#5471](https://github.com/LMCache/LMCache/pull/5471) |
| Mooncake | SDK loaded only when its backend is selected; request tags in lookup keys | [#6134](https://github.com/LMCache/LMCache/pull/6134), [#5449](https://github.com/LMCache/LMCache/pull/5449) |
| gRPC (MP transport) | Native and `grpc.aio` server modes, automatic server start for `grpc://` endpoints, native-mode metrics, and `grpc+unix` | [#6031](https://github.com/LMCache/LMCache/pull/6031), [#5799](https://github.com/LMCache/LMCache/pull/5799), [#6001](https://github.com/LMCache/LMCache/pull/6001), [#6061](https://github.com/LMCache/LMCache/pull/6061), [#6154](https://github.com/LMCache/LMCache/pull/6154) |
| Python | Python 3.14 support | [#5289](https://github.com/LMCache/LMCache/pull/5289) |

## Builds and images

Install or upgrade from the Python Package Index (PyPI):

```
pip install -U lmcache
```

The official vLLM image is published on Docker Hub:

```
docker pull lmcache/vllm-openai:v0.5.7
```

RBLN wheels are published on the [GitHub release page](https://github.com/LMCache/LMCache/releases/tag/v0.5.7) ([#6140](https://github.com/LMCache/LMCache/pull/6140)).

## Other changes

- A shared-L1 memory orchestrator ([#5559](https://github.com/LMCache/LMCache/pull/5559)) and a per-request policy to load KV cache or recompute it ([#5536](https://github.com/LMCache/LMCache/pull/5536)).
- Coordinator visibility: per-server cache-event loss, view-freshness tracking, persistence and prefetch metrics, a `/status` snapshot, and a Grafana dashboard ([#5560](https://github.com/LMCache/LMCache/pull/5560), [#5681](https://github.com/LMCache/LMCache/pull/5681), [#5881](https://github.com/LMCache/LMCache/pull/5881), [#5879](https://github.com/LMCache/LMCache/pull/5879), [#6179](https://github.com/LMCache/LMCache/pull/6179)).
- Groundwork for token dropping: request-local state, request-scoped algorithm plugins, and paged GPU KV compaction ([#5870](https://github.com/LMCache/LMCache/pull/5870), [#5736](https://github.com/LMCache/LMCache/pull/5736), [#5737](https://github.com/LMCache/LMCache/pull/5737)).
- Dynamic prefetch admission ([#5889](https://github.com/LMCache/LMCache/pull/5889)), and no L2 lookup when L1 already holds the full prefetch request ([#5652](https://github.com/LMCache/LMCache/pull/5652)).
- Retryable peer-to-peer (P2P) adapter teardown ([#6208](https://github.com/LMCache/LMCache/pull/6208)).
- In-process components moved under legacy namespaces, and in-process guides moved to the legacy docs ([#5923](https://github.com/LMCache/LMCache/pull/5923)).

The [full release notes](https://github.com/LMCache/LMCache/releases/tag/v0.5.7) list every change.

## Coming in v0.5.8

These changes were merged to the dev branch after the v0.5.7 tag was created (tag commit 236f3ee).
They are in nightly builds now, and they are planned for v0.5.8.
They are not in v0.5.7.

Features and integrations:

- vLLM sleep mode with VMM-shared KV caches ([#6358](https://github.com/LMCache/LMCache/pull/6358))
- The `valkey_rdma` L2 adapter ([#5556](https://github.com/LMCache/LMCache/pull/5556))
- Request matching tags through object identity ([#6199](https://github.com/LMCache/LMCache/pull/6199), [#5843](https://github.com/LMCache/LMCache/pull/5843))
- File descriptor (fd) based sharing of VMM-mapped memory regions ([#6266](https://github.com/LMCache/LMCache/pull/6266))
- TP-replicated KV groups stored once per tensor parallel (TP) group ([#6125](https://github.com/LMCache/LMCache/pull/6125))
- HF3FS `shard_dirs` to spread stores across directories ([#6261](https://github.com/LMCache/LMCache/pull/6261))
- `--isolated-ipc` for `lmcache bench server` ([#5931](https://github.com/LMCache/LMCache/pull/5931))
- Token dropping that allocates from the resident KV length ([#5871](https://github.com/LMCache/LMCache/pull/5871))
- A GLM-5.3-Flash recipe ([#6372](https://github.com/LMCache/LMCache/pull/6372)), and Kimi K3.1 KDA support with correctness checks ([#6318](https://github.com/LMCache/LMCache/pull/6318))

Refactoring:

- The in-tree in-process implementation is removed ([#6254](https://github.com/LMCache/LMCache/pull/6254))

Bug fixes:

- CLI profiling tests isolated from host dependencies ([#6350](https://github.com/LMCache/LMCache/pull/6350))
- Padded per-layer (K, V) KV tuples on Ascend ([#6241](https://github.com/LMCache/LMCache/pull/6241))
- The Intel compiler runtime is no longer bundled into the XPU wheel ([#6281](https://github.com/LMCache/LMCache/pull/6281))
- The engine stays alive when gRPC or ZMQ requests fail ([#6275](https://github.com/LMCache/LMCache/pull/6275), [#6331](https://github.com/LMCache/LMCache/pull/6331)), and RESP settings fall back to environment variables ([#6294](https://github.com/LMCache/LMCache/pull/6294))

## Thank you, new contributors

This release includes work from 34 new contributors.
Thank you, and welcome to the LMCache community.
