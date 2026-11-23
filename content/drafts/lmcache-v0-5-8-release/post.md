---
title: "LMCache v0.5.8: One Multiprocess Architecture, and API Keys for ZMQ and gRPC"
byline: LMCache Team
date: 2026-11-22
meta_description: "LMCache v0.5.8 runs only as a standalone multiprocess service, moves in-process mode to its own package, adds optional API keys for ZMQ and gRPC, and binds the coordinator to the local host by default."
tags: [LMCache, KV cache, release, multiprocess, security]
---

# LMCache v0.5.8: One Multiprocess Architecture, and API Keys for ZMQ and gRPC

![General arrangement of LMCache v0.5.8, drawn as a blueline engineering sheet. On the left, an engine box labeled vLLM holds a box labeled LMCacheMPConnector. Two vermilion request lines, labeled ZMQ and gRPC · auto, run from the connector to two open ports on a double-outlined box labeled LMCache MP server. Inside the server, a tier labeled L1 is filled with vermilion dots and a tier labeled L2 with teal dots. A third open port on the server carries a line labeled HTTP API down to a box labeled dashboard. One vertical rod threads three keys drawn with dashed bows, one beside each of the ZMQ, gRPC, and HTTP API ports, under the note API keys · optional · one set. On the right, a box labeled coordinator, with the note --host 127.0.0.1, connects to the server at an open port. A dashed-outline box labeled lmcache-nixl attaches to the server as a separate part. A dashed-outline box labeled LMCache_inprocess sits below the engine with no connection to anything. Small open triangles mark the five changes in v0.5.8: the API keys, gRPC auto mode, the coordinator host, lmcache-nixl, and LMCache_inprocess. The title block reads LMCACHE, general arrangement, sheet 1, not to scale, revision 0.5.8.](images/lmcache-v0-5-8-release-sheet-1-general-arrangement@2x.png)

*In v0.5.8, LMCache runs only as a standalone MP server, which vLLM reaches through LMCacheMPConnector.
The triangles mark what changed: one optional key set for ZMQ, gRPC, and the HTTP API; gRPC server mode auto; a coordinator that listens on 127.0.0.1 by default; and lmcache-nixl and LMCache_inprocess as separate packages.*

LMCache v0.5.8 completes the move to one architecture.
LMCache now runs only as a standalone multiprocess (MP) service, and the legacy in-process mode moves to a separate package.
The release also adds optional API keys to the ZeroMQ (ZMQ) and gRPC request transports, and the coordinator now listens only on the local host unless you set a different address.

The LMCache contributor team and community are pleased to announce LMCache v0.5.8, released on November 22, 2026.
It also adds new peer-to-peer (P2P) data paths, including opt-in writes to the memory of peers (`--enable-p2p-write`, [#6532](https://github.com/LMCache/LMCache/pull/6532)).
Because of cache identity fixes, Low-Rank Adaptation (LoRA) adapters and model revisions no longer share key-value (KV) cache entries ([#5713](https://github.com/LMCache/LMCache/pull/5713), [#6267](https://github.com/LMCache/LMCache/pull/6267)).
The NIXL connector moves into its own package, and the release includes model-serving correctness fixes for vLLM and SGLang.

Read the upgrade notes before you upgrade if you use in-process mode, if your coordinator serves MP servers on other hosts, or if your server already uses an HTTP API key, because you must now give that key to vLLM and other clients. ⟲ Each of these cases needs a change to your deployment.

## In-process mode moves to its own package

The legacy in-process implementation is no longer in the lmcache package ([#6254](https://github.com/LMCache/LMCache/pull/6254)).
LMCache now runs as a standalone MP service, and vLLM connects to it through LMCacheMPConnector.

This removal was planned.
The LMCache documentation has marked in-process mode as deprecated for several releases, and the [LMCache 2026 Q4 roadmap](https://github.com/LMCache/LMCache/issues/5873) lists in-process mode deprecation and deletion as its first item.
The [v0.5.7.post1 post](https://blog.lmcache.ai/en/2026/11/18/lmcache-v0-5-7-post1-release/) listed the removal as coming in the next release.
This is the first release without in-process mode.

**Important: if you run LMCache in-process, stay on v0.5.7.post1 or move to MP mode before you upgrade.** ⟲

The in-process code and its documentation are now in [LMCache_inprocess](https://github.com/LMCache/LMCache_inprocess).
The package keeps the import path lmcache.inprocess and the vLLM adapter path that the vLLM connector imports.

The lmcache_inprocess package is a pre-release.
The only version on the Python Package Index (PyPI), 0.1.0rc2, does not support lmcache 0.5.8 yet.
When a compatible release is available on PyPI, upgrade lmcache first and then install lmcache_inprocess.
Installing lmcache_inprocess first does not work. ⟲

As before, the SGLang integration supports only MP mode.
For an example of MP mode on other hardware, see [LMCache x Ascend, part two](https://blog.lmcache.ai/en/2026/11/16/lmcache-x-ascend-part-two-multiprocess-mode-on-ascend-npus/).

## Upgrade notes for operators

Check these items before you upgrade:

![Table titled upgrade: before and after. It compares v0.5.7.post1 with v0.5.8 for a deployment that changes nothing, and gives what to do for each row. Coordinator --host: 0.0.0.0 before, 127.0.0.1 now; set --host to an address that remote MP servers can reach, and enable API keys first. --grpc-server-mode: sync before, auto now, which picks native or aio; pass --grpc-server-mode sync. --separate-object-groups, which affects hybrid models only: off before, on now; --no-separate-object-groups turns it off, but keep the default for Mamba and linear-attention hybrids. An existing HTTP API key: checked on HTTP only before, on HTTP, ZMQ, and gRPC now; set LMCACHE_API_KEY_FILE or LMCACHE_API_KEY on clients. Dashboard Unix sockets: declared and discovered paths before, declared only now; add discovered paths with --uds-allowlist. The v0.5.8 column has a double outline and a small triangle in its header. The title block reads LMCACHE, upgrade: before and after, sheet 2, not to scale, revision 0.5.8.](images/lmcache-v0-5-8-release-sheet-2-upgrade-defaults@2x.png)

*If you upgrade to v0.5.8 and change nothing, these five behaviors change.
The last column says what to do.
The list below covers the other upgrade items.*

- If you use in-process mode, stay on v0.5.7.post1 or move to MP mode. ⟲
- If your server already has an API key for its HTTP API (`--api-key-file`, `LMCACHE_API_KEY`, `LMCACHE_API_KEY_FILE`, or the older `LMCACHE_HTTP_API_KEY` names), v0.5.8 also requires that key on ZMQ and gRPC requests.
  Before you upgrade, set `LMCACHE_API_KEY_FILE` or `LMCACHE_API_KEY` for vLLM and other clients. ⟲
- The coordinator `--host` default is now `127.0.0.1` (it was `0.0.0.0`).
  If your coordinator serves MP servers on other hosts, start it with an explicit `--host` ([#6606](https://github.com/LMCache/LMCache/pull/6606), [#6609](https://github.com/LMCache/LMCache/pull/6609)).
  Coordinators that the LMCache Kubernetes operator deploys already pass `--host 0.0.0.0`.
  The coordinator also rejects a registered instance address that includes a scheme, port, or path ([#6534](https://github.com/LMCache/LMCache/pull/6534)).
- The native NIXL connector is now the separate lmcache-nixl package, at the same version as lmcache, and `pip install "lmcache[nixl]"` installs it ([#5400](https://github.com/LMCache/LMCache/pull/5400)).
  To add it to an existing installation, pin the installed version, for example `pip install "lmcache[nixl]==0.5.8"`.
  The adapter refuses a mismatched lmcache-nixl and prints that command.
- The gRPC server mode default is now `auto` (it was `sync`) ([#6754](https://github.com/LMCache/LMCache/pull/6754)).
  It selects `native` when pygrpc-native is installed, and `aio` when it is not.
  The P2P listener makes the same selection.
  Explicit modes do not change.
  To keep the old behavior, pass `--grpc-server-mode sync`.
- `--separate-object-groups` is enabled by default ([#6041](https://github.com/LMCache/LMCache/pull/6041)).
  For hybrid models, each cross-chunk attention window type has its own object group.
  To use one group, pass `--no-separate-object-groups`.
  Keep the default for Mamba and linear-attention hybrids, because they require it.
  Models that are not hybrid are not affected.
- The frontend dashboard now connects only to Unix socket paths that you declare with `--nodes`, `--config`, or `--uds-allowlist` ([#6497](https://github.com/LMCache/LMCache/pull/6497)).
  If it discovers socket nodes through `--node-supplier-url`, add those paths with `--uds-allowlist`.
- If an L2 adapter uses the `aesgcm` serializer-deserializer (serde), objects that earlier versions encrypted fail to load one time after the upgrade and are recomputed ([#6601](https://github.com/LMCache/LMCache/pull/6601)).
- This release has no MUSA wheel. ⟲

## Optional API keys for request transports

The ZMQ transport ([#5769](https://github.com/LMCache/LMCache/pull/5769)) and the sync, aio, and native gRPC servers ([#5770](https://github.com/LMCache/LMCache/pull/5770), [#6439](https://github.com/LMCache/LMCache/pull/6439)) can now check an API key on each request.
Before this release, only the HTTP services had this check.

The request transport documentation says: "Authentication stays disabled when the server has no keys, preserving existing deployments."
To enable it, give the server keys with `--api-key-file` (you can repeat it), `LMCACHE_API_KEY_FILE`, or `LMCACHE_API_KEY`.
The server combines keys from all sources into one set, so you can rotate keys.
Clients, including vLLM, read `LMCACHE_API_KEY_FILE` or `LMCACHE_API_KEY`.
One set of keys covers the HTTP API and both transports, so a server that already has an HTTP key now also checks it on ZMQ and gRPC. ⟲

On gRPC, the server checks the key before it deserializes the request.
A missing or wrong key returns `UNAUTHENTICATED`.

On ZMQ, the client sends the credential in a new versioned frame.
Older servers cannot read this frame, and older clients cannot connect to a server that requires keys.
The documentation advises: "Upgrade the deployment before enabling keys."

API keys do not encrypt request traffic.
ZMQ sends the token in clear text, and the default gRPC channel is not encrypted.
Keep these transports on a trusted network, or use an encrypted tunnel.

## Coordinator binds to the local host by default

The coordinator now listens on `127.0.0.1` by default ([#6606](https://github.com/LMCache/LMCache/pull/6606)), so only clients on the same machine can connect to it.
To serve MP servers on other hosts, start it with `--host` set to an address that they can reach, and enable API keys before you expose it.
The default port is still 9300.

The coordinator also accepts an instance address only as an IPv4 address, IPv6 address, or host name, with nothing added ([#6534](https://github.com/LMCache/LMCache/pull/6534)).
A registration that includes a scheme, port, or path now fails with HTTP 422.
For more about the coordinator, see [The LMCache coordinator: a control plane for fleet-wide KV cache](https://blog.lmcache.ai/en/2026/11/11/the-lmcache-coordinator-a-control-plane-for-fleet-wide-kv-cache/).

## Other security changes

The Unix socket proxy of the frontend dashboard now forwards only to declared socket paths, and it compares paths after it resolves symbolic links ([#6497](https://github.com/LMCache/LMCache/pull/6497)).
A socket node from `--node-supplier-url` that is not on the allowlist gets a 403 response.

With the opt-in `aesgcm` serde (Advanced Encryption Standard in Galois/Counter Mode, or AES-GCM), each encrypted object is now bound to the cache key that it was stored under ([#6601](https://github.com/LMCache/LMCache/pull/6601)).
An encrypted object that is found under a different key now fails to load and is recomputed.

## Hardware and software in this release

### Hardware

| Platform | What is new or improved | PRs |
|---|---|---|
| CUDA | File descriptor (fd) based sharing of regions mapped with virtual memory management (VMM); automatic detection of VMM KV allocation; vLLM sleep mode with VMM-shared KV caches; faster copies for head-major (HND) KV layouts with one KV head | [#6266](https://github.com/LMCache/LMCache/pull/6266), [#6499](https://github.com/LMCache/LMCache/pull/6499), [#6358](https://github.com/LMCache/LMCache/pull/6358), [#6299](https://github.com/LMCache/LMCache/pull/6299) |
| ROCm | VMM KV cache inter-process communication (IPC) through rocm.bindings; opt-in `--rocm-host-event-wait` (off by default); hipify guard fix; v0.5.8 wheels for gfx942 and gfx950 on GitHub Releases (ROCm 7.2 with PyTorch 2.13, and ROCm 7.2.4 with PyTorch 2.10) | [#6626](https://github.com/LMCache/LMCache/pull/6626), [#6212](https://github.com/LMCache/LMCache/pull/6212), [#5035](https://github.com/LMCache/LMCache/pull/5035) |
| XPU | Smaller wheel: the extensions no longer need or bundle the compiler runtime, and debug information is removed | [#6281](https://github.com/LMCache/LMCache/pull/6281) |
| Ascend | Padded per-layer (K, V) tuples for pooled layouts in vLLM-Ascend v0.30; per-plane layout in shape descriptors | [#6241](https://github.com/LMCache/LMCache/pull/6241), [#6215](https://github.com/LMCache/LMCache/pull/6215) |
| MUSA | Native CacheGen codec; IPC handles sent as plain data (no wheel for this release ⟲) | [#5865](https://github.com/LMCache/LMCache/pull/5865), [#6283](https://github.com/LMCache/LMCache/pull/6283) |
| RBLN | Nightly rbln-serve validation; wheel on GitHub Releases | [#6157](https://github.com/LMCache/LMCache/pull/6157) |
| RDMA and memory | Remote direct memory access (RDMA) writes in the transfer channel; shared Device-DAX (device direct access) regions | [#6401](https://github.com/LMCache/LMCache/pull/6401), [#6121](https://github.com/LMCache/LMCache/pull/6121) |

### Engines, storage, and platforms

| Platform | What is new or improved | PRs |
|---|---|---|
| vLLM | New KVCacheGroup support; kv_cache_access on LMCacheMPConnector; LoRA cache-key isolation; Kimi K3.1 state for Kimi Delta Attention (KDA) layers; faster packed prompt-token handling | [#6608](https://github.com/LMCache/LMCache/pull/6608), [#6487](https://github.com/LMCache/LMCache/pull/6487), [#5713](https://github.com/LMCache/LMCache/pull/5713), [#6318](https://github.com/LMCache/LMCache/pull/6318), [#6503](https://github.com/LMCache/LMCache/pull/6503) |
| SGLang | Health check; retry of earlier failed stores; store-progress reset after recovery; native SGLang image builds | [#6319](https://github.com/LMCache/LMCache/pull/6319), [#6404](https://github.com/LMCache/LMCache/pull/6404), [#6659](https://github.com/LMCache/LMCache/pull/6659), [#6658](https://github.com/LMCache/LMCache/pull/6658), [#6814](https://github.com/LMCache/LMCache/pull/6814) |
| Valkey | valkey_rdma L2 adapter; valkey_rdma workers spread across several RDMA interfaces (`rdma_interface`); blob-tcp transport; username and password authentication fixed for the GLIDE client | [#5556](https://github.com/LMCache/LMCache/pull/5556), [#6293](https://github.com/LMCache/LMCache/pull/6293), [#6400](https://github.com/LMCache/LMCache/pull/6400), [#5917](https://github.com/LMCache/LMCache/pull/5917) |
| 3FS (HF3FS) | shard_dirs to spread stores across directories; key-buffer miss confirmation and stale-entry handling | [#6261](https://github.com/LMCache/LMCache/pull/6261), [#6002](https://github.com/LMCache/LMCache/pull/6002), [#6344](https://github.com/LMCache/LMCache/pull/6344) |
| Aerospike | Environment variable fallbacks for L2 settings | [#6264](https://github.com/LMCache/LMCache/pull/6264) |
| NIXL | Separate lmcache-nixl package; scratch-file cleanup | [#5400](https://github.com/LMCache/LMCache/pull/5400), [#6369](https://github.com/LMCache/LMCache/pull/6369) |
| Kubernetes and llm-d | llm-d integration guide and manifests; Kubernetes example for a CPU-only server | [#6520](https://github.com/LMCache/LMCache/pull/6520), [#6627](https://github.com/LMCache/LMCache/pull/6627), [#5981](https://github.com/LMCache/LMCache/pull/5981) |
| Models | GLM-5.3-Flash recipe | [#6372](https://github.com/LMCache/LMCache/pull/6372) |

For more about the Valkey work, see [Valkey in LMCache: a fast shared memory fabric](https://blog.lmcache.ai/en/2026/11/19/valkey-in-lmcache-fast-shared-memory-fabric/).
For the llm-d guide, see [LMCache with llm-d](https://docs.lmcache.ai/production/llm_d.html).
For vLLM version guidance, see [vLLM and LMCache compatibility](https://docs.lmcache.ai/getting_started/compatibility.html).

## Builds and images

Install or upgrade from PyPI:

```
pip install -U lmcache
```

To add the NIXL connector:

```
pip install "lmcache[nixl]"
```

All four images are on Docker Hub for amd64 and arm64.
The full lmcache/vllm-openai:v0.5.8, lmcache/standalone, and lmcache/sglang images use CUDA 13.0.
The `latest` tags now point to the v0.5.8 images.

```
docker pull lmcache/vllm-openai:v0.5.8
docker pull lmcache/vllm-openai:v0.5.8-lightweight
docker pull lmcache/sglang:v0.5.8
docker pull lmcache/standalone:v0.5.8
```

The lmcache/vllm-openai:v0.5.8 and lmcache/standalone images include pygrpc-native, so their gRPC server uses native mode by default.
The lmcache/vllm-openai:v0.5.8 image also includes lmcache-nixl.
The lightweight image includes neither, so its gRPC server uses aio mode by default.

Wheels for ROCm, XPU, and RBLN are on their own GitHub Releases pages, not on PyPI: [v0.5.8-rocm](https://github.com/LMCache/LMCache/releases/tag/v0.5.8-rocm), [v0.5.8-rocm-torch210](https://github.com/LMCache/LMCache/releases/tag/v0.5.8-rocm-torch210), [v0.5.8-xpu](https://github.com/LMCache/LMCache/releases/tag/v0.5.8-xpu), and [v0.5.8-rbln](https://github.com/LMCache/LMCache/releases/tag/v0.5.8-rbln).
This release has no MUSA wheel. ⟲

The PyTorch 2.14.0 builds and the removal of CUDA 12.9 (cu129) wheels and images came in v0.5.7.post1 ([#6465](https://github.com/LMCache/LMCache/pull/6465), [#6533](https://github.com/LMCache/LMCache/pull/6533)).
See the [v0.5.7.post1 post](https://blog.lmcache.ai/en/2026/11/18/lmcache-v0-5-7-post1-release/) for those changes.

## Other changes

- One stalled ZMQ client or malformed message no longer blocks other clients ([#6256](https://github.com/LMCache/LMCache/pull/6256), [#4934](https://github.com/LMCache/LMCache/pull/4934)).
- The engine no longer crashes when a gRPC transfer fails or the ZMQ server rejects a request ([#6275](https://github.com/LMCache/LMCache/pull/6275), [#6331](https://github.com/LMCache/LMCache/pull/6331)).
- Slow L2 writes no longer block all of L1 ([#5863](https://github.com/LMCache/LMCache/pull/5863)). gRPC clients now ignore `http_proxy`, `https_proxy`, and `grpc_proxy` and connect directly ([#6278](https://github.com/LMCache/LMCache/pull/6278)).
- KV cache that is replicated across a tensor-parallel (TP) group is stored one time per group ([#6125](https://github.com/LMCache/LMCache/pull/6125)), and the final partial prompt chunk is now saved ([#5886](https://github.com/LMCache/LMCache/pull/5886)).
- Early work toward multiple chunk sizes ([#6765](https://github.com/LMCache/LMCache/pull/6765), [#6719](https://github.com/LMCache/LMCache/pull/6719)) and token dropping ([#5871](https://github.com/LMCache/LMCache/pull/5871), [#5875](https://github.com/LMCache/LMCache/pull/5875), [#6365](https://github.com/LMCache/LMCache/pull/6365)).

The [v0.5.8 release notes](https://github.com/LMCache/LMCache/releases/tag/v0.5.8) list every change, and the [full changelog](https://github.com/LMCache/LMCache/compare/v0.5.7.post1...v0.5.8) compares v0.5.8 with v0.5.7.post1.
Documentation is at [docs.lmcache.ai](https://docs.lmcache.ai).

## Thank you, new contributors

This release includes work from 29 new contributors.
Thank you, and welcome to the LMCache community.
