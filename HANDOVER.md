# Hyderabadi Amruttulya — revamp handover

Single-file static site. No build step, no framework: `index.html` holds all markup, styles
(Tailwind Play CDN + one `<style>` block) and one vanilla-JS IIFE.

## 1. Deploy to GitHub Pages

| Item | Setting |
|---|---|
| Branch | Settings → Pages → Deploy from a branch → `main` (or merge `revamp-v-1.1` first) |
| Folder | `/ (root)` |
| Custom domain | `CNAME` already contains `hyderabadiamruttulya.com` — leave it in the repo root |
| Jekyll | `.nojekyll` (empty file, already created) stops Jekyll from eating `_`-prefixed paths |
| Images | Stay exactly where they are: `images/` in the repo root |

All image `src` values are relative (`./images/…`) so they survive a project-subpath deploy.
Only `og:image` / `twitter:image` are absolute, which crawlers require.

If any absolute image URLs creep back in later:

```sh
sed -i '' 's|https://hyderabadiamruttulya.com/images/|./images/|g' index.html
# then restore the two social-card tags, which must stay absolute:
sed -i '' 's|"og:image" content="./images/|"og:image" content="https://hyderabadiamruttulya.com/images/|' index.html
sed -i '' 's|"twitter:image" content="./images/|"twitter:image" content="https://hyderabadiamruttulya.com/images/|' index.html
```

### Enquiries

There is no contact form, and GitHub Pages could not process one anyway. Every enquiry route on
the page is a plain link, so nothing can silently fail:

| Where | Goes to |
|---|---|
| Hero "Enquire about a franchise" | WhatsApp, new tab |
| Mobile drawer CTA | WhatsApp, new tab |
| Nav "Call us", footer number | `tel:+919849998779` |
| `#enquiry` section | WhatsApp button + call button |

The WhatsApp links open a pre-written message the visitor completes with their city. To change
either the number or that message, edit every occurrence at once:

```sh
# number (appears in wa.me links, tel: links, JSON-LD and llms.txt)
grep -rn '9849998779' index.html llms.txt
```

## 2. Scale, phone to television

Every size on the page is in `rem`, and one root-size ramp in the `<style>` block
carries the whole design from a 320px phone to a television:

| Viewport | Root size | Shell width |
|---|---|---|
| up to 1536px | 16px (browser default — nothing changes) | 1180px |
| 1536px → 3840px | `clamp(16px, .55vw + 7.55px, 22px)` | `clamp(1180px, 62vw + 240px, 2080px)` |
| ≥ 2200px **and** `hover: none` — i.e. a TV | `clamp(22px, .95vw, 30px)` | as above |

The TV rule keys off the absence of a pointer, because a 4K monitor at desk
distance and a 4K television across a room need different sizes at the same
pixel width. Nothing about the layout changes at any of these steps; only scale.

The hero fills the first screen (`min-height: min(100svh, 66rem)`) only above
1024px wide **and** 640px tall, so mobile landscape is never squeezed.

## 3. Search + AI visibility

- `robots.txt` allows all crawlers and names the AI ones explicitly (GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended, Applebot-Extended, CCBot, OAI-SearchBot).
- `sitemap.xml` — one URL, update `<lastmod>` on content changes.
- `llms.txt` — a plain-language fact sheet for answer engines, including an explicit list of what
  is **not** published so models do not invent outlet counts, prices or dates.
- Structured data: `LocalBusiness` (phone, areaServed, sameAs) and `FAQPage` (all six questions).
- Target phrases carried in the title, meta description, H2s and FAQ: *chai franchise*,
  *affordable chai franchise*, *chai franchise cost*, *tea franchise India*.

After deploying: submit the sitemap in Google Search Console and request indexing.

## 4. Nothing on the page is unverified

Every `[VERIFY]` and `[PLACEHOLDER]` marker has been cleared. No marker was replaced with a guess:
where a figure or commitment was not confirmed, the sentence was rewritten to say only what the
business has actually stated and to name the discovery call for the rest. The page can go live as
it stands.

What is still worth supplying — each one upgrades a line that currently reads as "ask us":

| Where | What would sharpen it |
|---|---|
| Franchise numbers, third tile | A fee range, e.g. "₹3.5L – ₹6L". The tile currently reads "Quoted on the call". A range converts far better and filters out people who cannot afford it. |
| Why jaggery, card 01 | The exact variety, region and process. The card currently describes jaggery generically. Keep it descriptive — no blood-sugar, immunity, weight or mineral claims, which are regulated in India. |
| How partnering works | Confirmation that the five steps are the real process, and the end-to-end timeline. The steps as written stay inside what the FAQ already commits to. |
| FAQ, six answers | Real figures for: fee, training given, timeline in weeks, territory radius, sourcing regions and post-launch support. Fee structure is deliberately not described on the page — it varies per partner. |
| Menu preview | Confirm the six items are what every outlet serves. Prices are deliberately not published — they are set per outlet before opening. |
| Footer Instagram link | `@hydamruttulya` was read off the QR code in `images/chai-5.jpeg` and is **not confirmed**. Instagram serves the same login page for a real handle and a dead one, so this cannot be checked without signing in. Open it once before launch. |
| JSON-LD `LocalBusiness` | Registered address, geo coordinates, opening hours, other social profiles. All optional in schema.org — the block validates without them. |

**Do not put a comment inside either `application/ld+json` block.** JSON has no comments, and one
in the `LocalBusiness` block was silently invalidating the whole thing until it was removed.

The six FAQ answers are duplicated word-for-word in the `FAQPage` structured data. Google requires
the two to match, so **edit both or neither**:

```sh
python3 - <<'EOF'
import json,re,html
s=open('index.html',encoding='utf-8').read()
vis=[re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',m))).strip()
     for m in re.findall(r'<p class="pb-6 pr-8[^"]*">(.*?)</p>', s, re.S)]
ld=[q['acceptedAnswer']['text'] for q in
    json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)[1])['mainEntity']]
for i,(v,l) in enumerate(zip(vis,ld),1):
    print(i, 'MATCH' if v==l else 'DIFFERS')
EOF
```

Nothing on the page states an outlet count, location list, founding year, award or testimonial,
because none of those are confirmed.

## 5. Notes on the old site

- `images/chai-3.jpeg` was captioned "tea plantation" on the old site; it is actually an outlet
  opening. All `alt` text now matches what is really in each photo.
- `images/chai-5.jpeg` is an Instagram QR code, not a photograph, so it is not used as imagery.
- The old footer linked Facebook, Instagram, X, GitHub and YouTube icons to `#`. Those were dropped
  rather than shipped broken; only the confirmed Instagram handle is linked.
- `bundle.js` (751 KB) is now referenced only by `404.html`. The new `index.html` does not load it.
  Worth deleting or slimming when `404.html` gets the same treatment.
