# Figures: LMCache v0.5.8 release post

Two sheets in the LMCache whiteprint style, English and Simplified Chinese. Source: `../post.md`. Every label traces to the post. The sheets have no performance numbers, CacheBlend, or company names, and no lock or encrypted channel. Every port is drawn open.

## Placement note

| File | Anchor | Fields |
|---|---|---|
| `lmcache-v0-5-8-release-sheet-1-general-arrangement.svg` (or `@2x.png`) | Lead figure, above the opening paragraph ("LMCache v0.5.8 completes the move to one architecture."). Upload `lmcache-v0-5-8-release-sheet-1-general-arrangement-1200x630.png` as the og:image (featured image). Use the same drawing in both places. | Caption goes in the caption field. Alt text goes in `alt`, unchanged; it matches the SVG aria-label. The media-library text goes in the media description. |
| `lmcache-v0-5-8-release-sheet-2-upgrade-defaults.svg` (or `@2x.png`) | Under "## Upgrade notes for operators", after "Check these items before you upgrade:" and before the bulleted list | Same mapping |
| zh twins in `images-zh/` | Same anchors in the /zh/ edition | Same mapping, with the zh texts |

The hero is 1200 px wide, so it scales to about 0.67 in the 800 px column. Its smallest type is 15 px, which renders at about 10 px. Sheet 2 is 1100 px wide; its 14 px notes render at about 10 px. Both sheets are full column width, with no float or crop.

## Sheet 1: general arrangement (hero)

Files: `lmcache-v0-5-8-release-sheet-1-general-arrangement.svg`, `lmcache-v0-5-8-release-sheet-1-general-arrangement@2x.png`, `lmcache-v0-5-8-release-sheet-1-general-arrangement-1200x630.png`; `images-zh/lmcache-v0-5-8-release-sheet-1-general-arrangement-zh.svg`, `-zh@2x.png`, `-zh-1200x630.png`

**Caption (EN)**
In v0.5.8, LMCache runs only as a standalone MP server, which vLLM reaches through LMCacheMPConnector. The triangles mark what changed: one optional key set for ZMQ, gRPC, and the HTTP API; gRPC server mode auto; a coordinator that listens on 127.0.0.1 by default; and lmcache-nixl and LMCache_inprocess as separate packages.

**Caption (zh)**
在 v0.5.8 中，LMCache 只以独立的 MP 服务端运行，vLLM 通过 LMCacheMPConnector 连接它。三角形标出了本版本的变化：ZMQ、gRPC 和 HTTP API 共用一组可选的 API 密钥；gRPC 服务端模式默认为 auto；MP 协调器默认只监听 127.0.0.1；lmcache-nixl 和 LMCache_inprocess 改为独立的包。

**Alt text (EN)**, identical to the SVG aria-label
General arrangement of LMCache v0.5.8, drawn as a blueline engineering sheet. On the left, an engine box labeled vLLM holds a box labeled LMCacheMPConnector. Two vermilion request lines, labeled ZMQ and gRPC · auto, run from the connector to two open ports on a double-outlined box labeled LMCache MP server. Inside the server, a tier labeled L1 is filled with vermilion dots and a tier labeled L2 with teal dots. A third open port on the server carries a line labeled HTTP API down to a box labeled dashboard. One vertical rod threads three keys drawn with dashed bows, one beside each of the ZMQ, gRPC, and HTTP API ports, under the note API keys · optional · one set. On the right, a box labeled coordinator, with the note --host 127.0.0.1, connects to the server at an open port. A dashed-outline box labeled lmcache-nixl attaches to the server as a separate part. A dashed-outline box labeled LMCache_inprocess sits below the engine with no connection to anything. Small open triangles mark the five changes in v0.5.8: the API keys, gRPC auto mode, the coordinator host, lmcache-nixl, and LMCache_inprocess. The title block reads LMCACHE, general arrangement, sheet 1, not to scale, revision 0.5.8.

**Alt text (zh)**, identical to the SVG aria-label
LMCache v0.5.8 总图，以蓝线工程图样式绘制。左侧是标有 vLLM 的推理引擎框，框内有一个标有 LMCacheMPConnector 的框。两条朱红色请求线分别标有 ZMQ 和 gRPC · auto，从连接器通向双线框“LMCache MP 服务端”上的两个开放端口。服务端内部，标有 L1 的层以朱红色网点填充，标有 L2 的层以青色网点填充。服务端上的第三个开放端口引出一条标有 HTTP API 的线，向下连到标有“前端仪表盘”的框。一根竖杆穿过三把钥匙（钥匙环为虚线），分别位于 ZMQ、gRPC 和 HTTP API 端口旁边，上方注有“API 密钥 · 可选 · 同一组”。右侧是标有“MP 协调器”的框，注有 --host 127.0.0.1，通过一个开放端口连到服务端。标有 lmcache-nixl 的虚线框作为独立部件连到服务端。标有 LMCache_inprocess 的虚线框位于推理引擎下方，不与任何部件相连。五个小三角形标出 v0.5.8 的五项变化：API 密钥、gRPC auto 模式、协调器监听地址、lmcache-nixl 和 LMCache_inprocess。图框标注为 LMCACHE、总图、图 1、比例示意、版本 0.5.8。

**Media library (EN)**
Sheet 1 (hero and lead figure) of the LMCache whiteprint set for 'LMCache v0.5.8: One Multiprocess Architecture, and API Keys for ZMQ and gRPC.' General arrangement of v0.5.8: vLLM with LMCacheMPConnector, ZMQ and gRPC transports to the LMCache MP server with L1 and L2 tiers, the HTTP API and frontend dashboard, the coordinator on --host 127.0.0.1, optional API keys (one key set), and the separate lmcache-nixl and LMCache_inprocess packages.

**Media library (zh)**
《LMCache v0.5.8: One Multiprocess Architecture, and API Keys for ZMQ and gRPC》LMCache 蓝线图组的图 1（题图兼正文首图）。v0.5.8 总图：vLLM 通过 LMCacheMPConnector，经 ZMQ 或 gRPC 连接带 L1、L2 层的 LMCache MP 服务端；HTTP API 与前端仪表盘；监听 --host 127.0.0.1 的 MP 协调器；可选的 API 密钥（同一组）；以及独立的 lmcache-nixl 和 LMCache_inprocess 包。

**Portable image-model prompt** (hero only; set the lettering afterwards in vector)

Order for Midjourney and Flux: subject, style, negative. For Imagen and GPT-image, put the style first and write it as prose. Midjourney: append `--ar 191:100 --style raw --stylize 120 --no text,lettering,numbers,watermark`. Imagen or Gemini: add "flat technical line illustration, scan of a printed drawing" and close with "The image contains no words, letters or numbers." GPT-image: state the no-lettering rule at the top and the bottom, and ask for a "coarse visible dot screen". Flux or SDXL: weight `(blueline engineering drawing:1.3) (halftone risograph overprint:1.2)`, put the negative block in the negative field, and keep CFG low.

```
SUBJECT — a general-arrangement drawing of a software system drawn as a machine, flat orthographic elevation. Left: a tall rectangular housing containing a smaller inner module. Two parallel straight lines, drawn in vermilion, run right from the inner module to two small open circular ports on the left face of a larger rectangular housing drawn with a double-weight outline. Inside the large housing, two stacked horizontal compartments: the upper filled with coarse vermilion halftone, the lower with coarse teal halftone. A third open port low on the large housing's left face feeds a thin line that turns down to a small rectangular box. One thin vertical rod threads three small keys (a ring bow and a toothed blade), one sitting beside each of the three ports. Right of the large housing: a smaller rectangle joined by a short line that ends in an open port circle; below it, a rectangle with a dash-dot phantom outline attached by a short line. Below the left housing: a detached dash-dot phantom rectangle with no connection. Five small open triangles (revision deltas) sit near the keys, the lower line, and the three phantom or right-hand boxes. No padlock, no closed or locked port, no shield, no encrypted-tunnel or pipe-in-pipe motif.

STYLE — "whiteprint"

A diazo whiteprint, the blueline engineering drawing that replaced the blueprint.
Hairline indigo-violet linework, hex 2E3A8C, at one consistent stroke weight on a
warm bone-white paper ground, hex F7F4EE, overprinted with exactly two risograph
spot inks — teal hex 12817E and vermilion hex D9491F — used only as coarse
halftone dot fills, never on the linework. Flat orthographic elevation, dead
straight on, no perspective and no 3D. Drafting vocabulary throughout: dimension
lines with slash tick terminators, extension lines standing clear of the object,
leader lines ending in a small dot, 45-degree section hatching on anything cut
through, thin open-V arrowheads, crisp square corners. Each ink layer sits about
one pixel out of registration, in the same direction across the whole sheet;
faint paper tooth, slight ink mottle at the edge of every fill. Generous paper
margin, one thin inset border rule, and a small empty rectangular title block in
the bottom-right corner. Calm, precise, uncrowded — a shop drawing, not an
infographic.

COLOR MEANING
vermilion = hot, in flight, plaintext, failure
teal      = cold, at rest, sealed
indigo    = structure, mechanism, dimensions

NO LETTERING
Leave every label, every number and the title block completely empty. Draw the
shapes only. Lettering is set afterwards in vector.

NEGATIVE
dark background, black background, neon, glow, bloom, futuristic city, skyline,
server room photography, data center, 3D render, isometric, perspective, glass,
chrome, metallic, gradient, gradient mesh, lens flare, drop shadow, bevel, robot,
mascot, character, cartoon, padlock on circuit board, padlock, lock, shield,
falling binary digits, matrix rain, stock icon set, flat-design vector illustration,
infographic template, rounded corners, four inks, five inks, text, lettering,
typography, letters, numbers, labels, captions, watermark, signature
```

## Sheet 2: upgrade, before and after

Files: `lmcache-v0-5-8-release-sheet-2-upgrade-defaults.svg`, `lmcache-v0-5-8-release-sheet-2-upgrade-defaults@2x.png`; `images-zh/lmcache-v0-5-8-release-sheet-2-upgrade-defaults-zh.svg`, `-zh@2x.png`

**Caption (EN)**
If you upgrade to v0.5.8 and change nothing, these five behaviors change. The last column says what to do. The list below covers the other upgrade items.

**Caption (zh)**
如果升级到 v0.5.8 时不改任何配置，以下五项行为会发生变化。最后一列说明应如何操作。其他升级事项见下方列表。

**Alt text (EN)**, identical to the SVG aria-label
Table titled upgrade: before and after. It compares v0.5.7.post1 with v0.5.8 for a deployment that changes nothing, and gives what to do for each row. Coordinator --host: 0.0.0.0 before, 127.0.0.1 now; set --host to an address that remote MP servers can reach, and enable API keys first. --grpc-server-mode: sync before, auto now, which picks native or aio; pass --grpc-server-mode sync. --separate-object-groups, which affects hybrid models only: off before, on now; --no-separate-object-groups turns it off, but keep the default for Mamba and linear-attention hybrids. An existing HTTP API key: checked on HTTP only before, on HTTP, ZMQ, and gRPC now; set LMCACHE_API_KEY_FILE or LMCACHE_API_KEY on clients. Dashboard Unix sockets: declared and discovered paths before, declared only now; add discovered paths with --uds-allowlist. The v0.5.8 column has a double outline and a small triangle in its header. The title block reads LMCACHE, upgrade: before and after, sheet 2, not to scale, revision 0.5.8.

**Alt text (zh)**, identical to the SVG aria-label
表格，标题为“升级：前后对照”。表格对比不改任何配置时 v0.5.7.post1 与 v0.5.8 的行为，并给出每一行的操作。MP 协调器 --host：以前为 0.0.0.0，现在为 127.0.0.1；请设为远程 MP 服务端可以访问的地址，并先启用 API 密钥。--grpc-server-mode：以前为 sync，现在为 auto，会选择 native 或 aio；传入 --grpc-server-mode sync 可恢复旧模式。--separate-object-groups，仅影响混合模型：以前关闭，现在开启；--no-separate-object-groups 可关闭它，但 Mamba 和线性注意力混合模型请保留默认值。已有的 HTTP API 密钥：以前只在 HTTP 上检查，现在在 HTTP、ZMQ 和 gRPC 上检查；请在客户端设置 LMCACHE_API_KEY_FILE 或 LMCACHE_API_KEY。前端仪表盘 Unix 套接字：以前包括已声明和已发现的路径，现在仅限已声明的路径；用 --uds-allowlist 添加已发现的路径。v0.5.8 一列为双线框，表头有一个小三角形。图框标注为 LMCACHE、升级：前后对照、图 2、比例示意、版本 0.5.8。

**Media library (EN)**
Sheet 2 of the LMCache whiteprint set for 'LMCache v0.5.8: One Multiprocess Architecture, and API Keys for ZMQ and gRPC.' Upgrade table, v0.5.7.post1 versus v0.5.8, with the action for each row: coordinator --host (0.0.0.0 to 127.0.0.1), --grpc-server-mode (sync to auto), --separate-object-groups (off to on), HTTP API key now also checked on ZMQ and gRPC, and dashboard Unix sockets limited to declared paths (--uds-allowlist).

**Media library (zh)**
《LMCache v0.5.8: One Multiprocess Architecture, and API Keys for ZMQ and gRPC》LMCache 蓝线图组的图 2。升级对照表，v0.5.7.post1 与 v0.5.8，附每一行的操作：MP 协调器 --host（0.0.0.0 改为 127.0.0.1）、--grpc-server-mode（sync 改为 auto）、--separate-object-groups（关改为开）、HTTP API 密钥现在也在 ZMQ 和 gRPC 上检查、前端仪表盘 Unix 套接字仅限已声明路径（--uds-allowlist）。

**Portable image-model prompt:** none. A comparison table is all lettering, and the house style never generates one. Use the drawn SVG.

## Decisions

- Sheet 2 is optional. It shows the five behaviors that change when an operator upgrades and changes nothing. Each row has the before value, the after value, and the action, which the upgrade list spreads across separate bullets. Cut it if the editor wants only one figure. The list already carries the same facts.
- Not drawn: in-process removal steps, lmcache_inprocess install order, NIXL pin command, MUSA wheel, image contents, the hardware matrix, P2P writes, cache identity (LoRA and revisions), and the security fixes (#6534, #6601). The tables or prose already carry these, or they are not mechanisms. The P2P and cache-identity items would each need their own detail sheet, and the post gives them one sentence each.
- The hero has about 17 text elements, above the house soft ceiling of ten. The brief asked for each change mark. If the hero must be sparser, drop "HTTP API" and "--host 127.0.0.1" first; the caption carries both.
- Revision triangles mark the changes. The title block's REV cell (triangle, 0.5.8) acts as the key, so the sheet needs no legend.
- Optional API keys are keys with dashed bows on one rod: optional, and one key set. The sheet has no lock or encrypted channel, and every port is drawn open. lmcache-nixl and LMCache_inprocess have dash-dot (phantom) outlines, which mark them as separate packages. LMCache_inprocess is not connected to anything.
