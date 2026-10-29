---
title: "LMCache at Samsung: the right people in the right place"
byline: Karsten Wade
date: 2026-10-28
meta_description: "A recap of the LMCache meetup and hands-on workshop at Samsung Semiconductor in San Jose, with slides, a CPU-only LMCache notebook, and what attendees asked for next."
tags: [LMCache, KV cache, events, mini-lmcache, CXL]
---

# LMCache at Samsung: the right people in the right place

Another small but important milestone occurred for the project with this inaugural event bringing LMCache meetups to the San Francisco Bay Area.

On Thursday, 22 October 2026, engineers and researchers who work on KV cache management met LMCache maintainers and contributors at Samsung Semiconductor in San Jose.
The event was "[Elevate Your LLM Performance: LMCache Meetup + Hands-on Workshop](https://luma.com/cm7eip1b)," a free, four-hour afternoon during Open Source AI Week.
Dongjoo Seo of Samsung and I co-hosted, and Samsung provided the venue.

Our goal was to move people from listening to experimenting.
Many attendees got LMCache running locally on their laptop and began experimenting with KV cache management before the event ended.

The word among event organizers is, "Everyone knows that people sign up for free events with no plan to attend."
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

LMCache contributor Samuel Shen then led a 45-minute, hands-on deep dive using a Jupyter notebook.
Sam also built the notebook so you can run on your own laptop, with no GPU: [lmcache-cpu-demo](https://github.com/sammshen/lmcache-cpu-demo).
It starts two copies of vLLM on your CPU with the same small model, `Qwen/Qwen2.5-0.5B-Instruct`.
One copy is plain vLLM.
The other sends its KV cache to an LMCache server that keeps it in RAM and also writes it to disk.
Both copies have vLLM's own prefix cache turned off, so every cache hit you see comes from LMCache.

The notebook loads a 6,000-token document, the Wikipedia article on Samsung, as a shared prefix.
You then ask questions about it in a side-by-side UI and compare the time to first token.
On the first question, both sides compute the document.
From the second question on, the plain side computes it again each time, and the LMCache side gets it back from the cache.

If you missed the workshop, start with Sam's notebook.
Let me know in the comments or social media how things worked out with the notebook.

Following Sam, Luis Chamberlain of Samsung gave a technical session on three topics: asymmetric quantization, dma-buf support with io_uring, and learned prefix caching with Cartridges and the work that follows from it.
Cartridges is one of the research ideas listed on lmcache.ai.

Luis's slides are [online](https://docs.google.com/presentation/d/1-3YBsCb71NvSt3s2TsVxisDoVb0_dn3lJ7HQxqAwB8s/edit), and there is a PDF copy in the [event folder](https://github.com/LMCache/lmcache-blogs/tree/main/events/2026-10-22-samsung-san-jose).

Dongjoo Seo of Samsung closed the talks with LMCache on CXL (Compute Express Link) memory.
His slides are found as PowerPoint and PDF in the [lmcache-blogs repo](https://github.com/LMCache/lmcache-blogs/tree/main/events/2026-10-22-samsung-san-jose).

For more of Samsung's work with LMCache, read their September post, [Raw block in LMCache: building a fast, recoverable NVMe tier for KV cache](https://blog.lmcache.ai/en/2026/09/22/raw-block-in-lmcache-building-a-fast-recoverable-nvme-tier-for-kv-cache/).

The afternoon ended with closing remarks and a networking reception.

In particular, I welcomed everyone to the new LMCache meetup community.
Then I invited participation in helping organize and execute future meetups.

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
