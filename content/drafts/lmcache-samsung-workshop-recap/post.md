---
title: "LMCache at Samsung: the right people in the right place"
byline: Karsten Wade
date: 2026-10-28
meta_description: "A recap of the LMCache meetup and hands-on workshop at Samsung Semiconductor in San Jose, with slides, a CPU-only LMCache notebook, and what attendees asked for next."
tags: [LMCache, KV cache, events, mini-lmcache, CXL]
---

# LMCache at Samsung: the right people in the right place

On Thursday, 22 October 2026, the day after PyTorch Conference, engineers and researchers who work on KV cache management met LMCache maintainers and contributors at Samsung Semiconductor in San Jose.
The event was "Elevate Your LLM Performance: LMCache Meetup + Hands-on Workshop," a free, four-hour afternoon during Open Source AI Week.
Dongjoo Seo of Samsung and I co-hosted, and Samsung provided the venue.

Our goal was to move people from listening to experimenting.
After the talks, attendees opened their laptops and worked against a live, public mini-lmcache deployment.
Nobody had to install anything.

Everyone knows that people sign up for free events with no plan to attend.
Measured against our own baseline, turnout was double what we expected.
**More important, it was the right people in the right place.**

[IMAGE: Wide photo of the room during the hands-on session, attendees at laptops. Alt text: "Attendees work on laptops at tables in a Samsung Semiconductor meeting room during the LMCache hands-on workshop in San Jose."]

## Who came

Registrants came from hardware, memory, storage, and silicon companies, from universities, and from AI startups.
Many of them build the systems where KV cache offload lands.
That is the audience LMCache most needs to hear from.

## The program

I opened with an introduction to LMCache.
My slides are in the [lmcache-blogs repo](https://github.com/LMCache/lmcache-blogs/tree/main/events/2026-10-22-samsung-san-jose).

Samuel Shen of Tensormesh then led a 45-minute, hands-on deep dive on research and testing with mini-lmcache.
He showed the public server deployment, and attendees called its API endpoints directly to benchmark and tune KV cache management.
The test environment stayed open after the session so that people could keep experimenting.

Sam also built a notebook you can run on your own laptop, with no GPU: [lmcache-cpu-demo](https://github.com/sammshen/lmcache-cpu-demo).
It starts two copies of vLLM on your CPU with the same small model, `Qwen/Qwen2.5-0.5B-Instruct`.
One copy is plain vLLM.
The other sends its KV cache to an LMCache server that keeps it in RAM and also writes it to disk.
Both copies have vLLM's own prefix cache turned off, so every cache hit you see comes from LMCache.
The notebook loads a 6,000-token document, the Wikipedia article on Samsung, as a shared prefix.
You then ask questions about it in a side-by-side UI and compare the time to first token.
On the first question, both sides compute the document.
From the second question on, the plain side computes it again each time, and the LMCache side gets it back from the cache.
You need Python 3.12 on macOS or Ubuntu 24.04.
**If you missed the workshop, start with Sam's notebook.**

Luis Chamberlain of Samsung gave a technical session on three topics: asymmetric quantization, dma-buf support with io_uring, and learned prefix caching with Cartridges and the work that follows from it.
Cartridges is one of the research ideas listed on lmcache.ai.
Luis's slides are [online](https://docs.google.com/presentation/d/1-3YBsCb71NvSt3s2TsVxisDoVb0_dn3lJ7HQxqAwB8s/edit), and there is a PDF copy in the [event folder](https://github.com/LMCache/lmcache-blogs/tree/main/events/2026-10-22-samsung-san-jose).

Dongjoo Seo of Samsung closed the talks with LMCache on CXL (Compute Express Link) memory.
Dongjoo asked that his slides go to everyone who attended, and you can find them, as PowerPoint and PDF, in the [lmcache-blogs repo](https://github.com/LMCache/lmcache-blogs/tree/main/events/2026-10-22-samsung-san-jose).
For more of Samsung's work with LMCache, read their September post, [Raw block in LMCache: building a fast, recoverable NVMe tier for KV cache](https://blog.lmcache.ai/en/2026/09/22/raw-block-in-lmcache-building-a-fast-recoverable-nvme-tier-for-kv-cache/).

The afternoon ended with closing remarks and a networking reception.

[IMAGE: Photo of a speaker presenting at the front of the room with slides on screen. Alt text: "A speaker presents slides about LMCache to a seated audience at Samsung Semiconductor in San Jose."]

## What you told us

Registration answers showed us how people run inference today.
About 60 percent of registrants run vLLM, and about 30 percent run SGLang.
About 65 percent run agent workloads.
Long context, retrieval-augmented generation (RAG), and multi-turn chat came next.

You also told us what you want from the maintainers.
The most common requests were:

1. A production deployment guide.
2. Reproducible benchmarks on your own stack.
3. A clear comparison between LMCache and the prefix caching built into vLLM.
4. An honest view of how good SGLang support is today.

This list helps us decide where to spend time.
If one of these requests is yours, tell us more about your setup in the LMCache Slack.

## Thank you, and what comes next

Thank you to Samsung for hosting us, to Luis and Dongjoo for their talks, and to Sam for building and running the hands-on session.

Here is how to continue:

- Run Sam's notebook: [lmcache-cpu-demo](https://github.com/sammshen/lmcache-cpu-demo)
- Get all the slides in the [event folder](https://github.com/LMCache/lmcache-blogs/tree/main/events/2026-10-22-samsung-san-jose).
- Join the LMCache Slack and star [LMCache on GitHub](https://github.com/LMCache/LMCache).
- Follow the [LMCache events calendar](https://luma.com/LMCache) for the next event.

We will see you at the next one.
