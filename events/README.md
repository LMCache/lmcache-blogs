# Events

This directory keeps the public material from LMCache community events:
slides, demo links, and an index for each event. Each event has its own folder,
named `<yyyy-mm-dd>-<host-or-place>`. The folder's `README.md` lists every file
in it and says what each one is.

| Date | Event | Folder |
|---|---|---|
| 22 October 2026 | LMCache Meetup + Hands-on Workshop, Samsung, San Jose | [`2026-10-22-samsung-san-jose/`](2026-10-22-samsung-san-jose/) |

## Add an event

1. Create `events/<yyyy-mm-dd>-<host-or-place>/`.
2. Add the slides. Use the speaker and talk in the file name, for example
   `jane-doe-kv-cache-offload.pdf`. Add a PDF for every deck, because readers
   can open a PDF on any device. Keep the source file (`.pptx`) too when the
   speaker sent one.
3. Keep each file under 2 MB. Pre-commit rejects larger files. Lower the image
   resolution of a large PDF before you commit it.
4. Add a `README.md` that lists the files. Copy the one in
   [`2026-10-22-samsung-san-jose/`](2026-10-22-samsung-san-jose/README.md).
5. Add a row to the table above.

Publish only material that the speaker agreed to share in public.
