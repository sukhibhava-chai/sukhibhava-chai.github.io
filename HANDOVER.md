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

### Connect the enquiry form

GitHub Pages cannot process form posts. Create a form at formspree.io, then:

```sh
sed -i '' 's|action="FORM_ENDPOINT"|action="https://formspree.io/f/YOURID"|' index.html
```

Until that swap, the form deliberately blocks submission and shows an inline notice pointing at
the phone, WhatsApp and the existing Typeform — it never fails silently.

## 2. Search + AI visibility

- `robots.txt` allows all crawlers and names the AI ones explicitly (GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended, Applebot-Extended, CCBot, OAI-SearchBot).
- `sitemap.xml` — one URL, update `<lastmod>` on content changes.
- `llms.txt` — a plain-language fact sheet for answer engines, including an explicit list of what
  is **not** published so models do not invent outlet counts, prices or dates.
- Structured data: `LocalBusiness` (phone, areaServed, sameAs) and `FAQPage` (all six questions).
- Target phrases carried in the title, meta description, H2s and FAQ: *chai franchise*,
  *affordable chai franchise*, *chai franchise cost*, *tea franchise India*.

After deploying: submit the sitemap in Google Search Console and request indexing.

## 3. What the client must supply

| Marker | Where | What is needed |
|---|---|---|
| `[VERIFY]` | Why jaggery, card 01 | Exact jaggery variety, region and process, so the card can describe the product precisely. Keep it descriptive — no health claims. |
| `[VERIFY]` | Franchise numbers, "Very affordable" | The real franchise fee (e.g. "₹4,50,000 onwards") and what it includes. A figure converts; an adjective does not. |
| `[PLACEHOLDER]` | How partnering works | Confirmation of the five steps, what happens in each, and the end-to-end timeline. |
| `[Placeholder menu]` | Menu preview | Real menu items and real counter prices. Every `₹—` is a placeholder — do not launch this section as-is. |
| `[VERIFY]` ×6 | FAQ | Answers for: franchise fee, experience needed, opening timeline, territory protection, sourcing specifics, ongoing support and any royalty. |
| `[VERIFY]` | Footer Instagram link | Handle `@hydamruttulya` was read from the QR code in `images/chai-5.jpeg`. Confirm it resolves. |
| — | JSON-LD | Registered address, geo coordinates, opening hours, and any other social profiles. |

Nothing on the page states an outlet count, location list, founding year, award or testimonial,
because none of those are confirmed. Jaggery is described only in terms of processing, flavour and
provenance — no blood-sugar, immunity, weight or mineral claims, which are regulated in India.

## 4. Notes on the old site

- `images/chai-3.jpeg` was captioned "tea plantation" on the old site; it is actually an outlet
  opening. All `alt` text now matches what is really in each photo.
- `images/chai-5.jpeg` is an Instagram QR code, not a photograph, so it is not used as imagery.
- The old footer linked Facebook, Instagram, X, GitHub and YouTube icons to `#`. Those were dropped
  rather than shipped broken; only the confirmed Instagram handle is linked.
- `bundle.js` (751 KB) is now referenced only by `404.html`. The new `index.html` does not load it.
  Worth deleting or slimming when `404.html` gets the same treatment.
