# LMCache Meetup + Hands-on Workshop at Samsung, San Jose

- Date: Thursday, 22 October 2026, 1:30 to 5:30 PM Pacific time
- Place: Samsung Semiconductor, 3655 N First St, San Jose, California
- Hosts: Dongjoo Seo (Samsung) and Karsten Wade (Tensormesh)
- Event page: <https://luma.com/cm7eip1b>
- More LMCache events: <https://luma.com/LMCache>

The event was a free, four-hour afternoon of talks and hands-on work on KV
cache management with LMCache. It took place the day after PyTorch Conference,
during Open Source AI Week.

## What is in this folder

| File | Talk | Speaker |
|---|---|---|
| [`karsten-wade-introduction-to-lmcache.pdf`](karsten-wade-introduction-to-lmcache.pdf) | Introduction to LMCache | Karsten Wade, Tensormesh |
| [`luis-chamberlain-lmcache-october-workshop.pdf`](luis-chamberlain-lmcache-october-workshop.pdf) | Asymmetric quantization, dma-buf support with io_uring, and learned prefix caching with Cartridges | Luis Chamberlain, Samsung |
| [`dongjoo-seo-lmcache-on-cxl-memory.pdf`](dongjoo-seo-lmcache-on-cxl-memory.pdf) | LMCache on CXL memory | Dongjoo Seo, Samsung |
| [`dongjoo-seo-lmcache-on-cxl-memory.pptx`](dongjoo-seo-lmcache-on-cxl-memory.pptx) | LMCache on CXL memory (PowerPoint source) | Dongjoo Seo, Samsung |

Notes on the files:

- Karsten's PDF has its page images reduced to 1920 x 1080 pixels to fit the
  repo's 2 MB file limit. The text is still searchable.
- Luis's PDF is an export of his
  [online slides](https://docs.google.com/presentation/d/1-3YBsCb71NvSt3s2TsVxisDoVb0_dn3lJ7HQxqAwB8s/edit),
  made on 28 October 2026. The online copy may change after that date.
- Dongjoo's PDF was made from his PowerPoint file with LibreOffice. Some fonts
  are replaced with similar ones. Open the `.pptx` to see the original fonts.

## Hands-on session

Samuel Shen (Tensormesh) led a 45-minute, hands-on session on research and
testing with mini-lmcache. To run a similar demo on your own laptop, with no
GPU, use his notebook:
[sammshen/lmcache-cpu-demo](https://github.com/sammshen/lmcache-cpu-demo).
