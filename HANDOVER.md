# Hyderabadi Amruttulya — revamp handover

Single-file static site: `index.html` holds all markup, styles and one vanilla-JS IIFE.
Nothing is loaded from a third party except Google Fonts — no framework, no CDN, no
external JavaScript at all.

Deploying needs no build. Four generators in `build/` regenerate parts of the page, and
you only run the one whose input you touched:

| You changed | Run |
|---|---|
| Any Tailwind class in `index.html` | `python3 build/build-css.py` |
| An FAQ question or answer | `python3 build/make-faq.py` |
| Any page copy at all | `python3 build/make-llms-full.py` |
| The tagline, the price, or a typeface on the social card | `python3 build/make-og-card.py` |

`build/build-css.py` needs `npx`; the other three need Python, and the card also needs
Pillow. Commit whatever they rewrite.

## 1. Deploy to GitHub Pages

| Item | Setting |
|---|---|
| Branch | Settings → Pages → Deploy from a branch → `main` (or merge `revamp-v-1.1` first) |
| Folder | `/ (root)` |
| Custom domain | `CNAME` already contains `hyderabadiamruttulya.com` — leave it in the repo root |
| Jekyll | `.nojekyll` (empty file, already created) stops Jekyll from eating `_`-prefixed paths |
| Build files | `build/` and `tailwind.config.js` are served but harmless; nothing links to them |
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

### The franchise fee

The page publishes **from ₹1 lakh** and deliberately publishes no upper figure. That one
number is the highest-intent thing on the site — "chai franchise cost" is what people
search — so it appears in the title, the meta description, the hero, the franchise tiles,
the at-a-glance table, the FAQ, the `Offer` schema and both fact sheets.

To change it, these are every place it lives:

```sh
grep -rn 'lakh\|1,00,000\|100000' index.html llms.txt
# then regenerate the derived files:
python3 build/make-faq.py && python3 build/make-llms-full.py && python3 build/make-og-card.py
```

If an upper bound is ever published, add `"maxPrice"` back beside `"minPrice"` in the
`Offer` node and `"maxValue"` beside `"minValue"` in the `Service` node's
`additionalProperty`.

### The stylesheet is compiled, not compiled-in-the-browser

The page used to load Tailwind's Play CDN: ~120KB of JavaScript that recompiled the same
CSS on every visit, flashed unstyled content, and left the page unstyled if the CDN was
slow. It is now ~19KB of real CSS inlined between `/* tw:start */` and `/* tw:end */` in
`index.html`.

**Do not hand-edit inside those markers.** The theme lives in `tailwind.config.js`. After
adding or changing any class:

```sh
python3 build/build-css.py
```

That runs the CLI and splices the result back in. It is pinned to Tailwind 3 on purpose —
the page uses v3 comma syntax in arbitrary grid values (`lg:grid-cols-[1.1fr,.9fr]`), which
v4 rejects. `tailwind.config.js` strips the generated block before scanning, so Tailwind is
never fed its own output.

### Structured data

One `@graph` in the head links five nodes by `@id` — `Organization`, `WebSite`, `WebPage`,
`Service` and `Offer` — plus a separate `FAQPage`. An answer engine that reads any one node
can resolve the whole entity from it.

The main entity is `Organization`, not `LocalBusiness`. `LocalBusiness` is only eligible for
local rich results with a street address, and none is confirmed. **When a registered address
exists**, change `"@type": "Organization"` to `"LocalBusiness"` on the `#business` node and add
`address`, `geo` and `openingHours`; nothing else needs to move.

**Do not put a comment inside either `application/ld+json` block.** JSON has no comments, and
one in the old `LocalBusiness` block was silently invalidating the whole thing.

### The FAQ has one source

Google requires the visible answer and the `FAQPage` answer to match word for word. Both are
now generated from the list at the top of `build/make-faq.py`. **Edit questions there, not in
`index.html`,** then run it. To verify at any time:

```sh
python3 - <<'EOF'
import json,re,html,io
s=io.open('index.html',encoding='utf-8').read()
vis=[re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',m)).replace('\u00a0',' ')).strip()
     for m in re.findall(r'<p class="pb-6 pr-8[^"]*">(.*?)</p>', s, re.S)]
faq=[b for b in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', s, re.S)
     if '"FAQPage"' in b][0]
ld=[q['acceptedAnswer']['text'] for q in json.loads(faq)['mainEntity']]
print('all %d match' % len(vis) if vis==ld else 'MISMATCH')
EOF
```

### Files for answer engines

- `llms.txt` — the fact sheet. Includes an explicit "do not infer" list so models do not
  invent outlet counts, an upper price, or founding dates. **Hand-maintained.**
- `llms-full.txt` — the whole page as markdown, generated by `build/make-llms-full.py`.
  Regenerate after any copy change or it goes stale.
- `robots.txt` — allows everything and names 19 AI crawlers explicitly.
- `sitemap.xml` — one URL with three image entries. Update `<lastmod>` on content changes.

### The rest

- `images/og-card.jpg` is a real 1200×630 social card, generated by `build/make-og-card.py`.
  It replaced the 999×999 logo, which every platform centre-cropped into a meaningless
  slice of a circle.
- The hero photograph is preloaded (`<link rel="preload" as="image">`) because it is the LCP
  element on every viewport.
- `404.html` was still the vendor template — titled "Base - Tailwind CSS Startup Template"
  and pulling 751KB of `bundle.js` just to say "not found". It is now a small self-contained
  branded page, `noindex, follow`. `bundle.js` was deleted; nothing referenced it.

After deploying: submit the sitemap in Google Search Console, request indexing, and run the
page through the Rich Results Test.

## 4. Nothing on the page is unverified

Every `[VERIFY]` and `[PLACEHOLDER]` marker has been cleared. No marker was replaced with a guess:
where a figure or commitment was not confirmed, the sentence was rewritten to say only what the
business has actually stated and to name the discovery call for the rest. The page can go live as
it stands.

What is still worth supplying — each one upgrades a line that currently reads as "ask us":

| Where | What would sharpen it |
|---|---|
| Why jaggery, card 01 | The exact variety, region and process. The card currently describes jaggery generically. Keep it descriptive — no blood-sugar, immunity, weight or mineral claims, which are regulated in India. |
| How partnering works | Confirmation that the five steps are the real process, and the end-to-end timeline. The steps as written stay inside what the FAQ already commits to. |
| FAQ, twelve answers | Real figures for: training given, timeline in weeks, territory radius, sourcing regions and post-launch support. The fee is published as "from ₹1 lakh"; no upper figure is published, by decision. |
| Menu preview | Confirm the six items are what every outlet serves. Prices are deliberately not published — they are set per outlet before opening. |
| Footer Instagram link | `@hydamruttulya` was read off the QR code in `images/chai-5.jpeg` and is **not confirmed**. Instagram serves the same login page for a real handle and a dead one, so this cannot be checked without signing in. Open it once before launch. |
| JSON-LD `LocalBusiness` | Registered address, geo coordinates, opening hours, other social profiles. All optional in schema.org — the block validates without them. |

The FAQ and its structured data are generated together — see §3, "The FAQ has one source".

Verify at any time:

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

## 5. Typography

Two families do the work, and the split between them is the rule to keep:

| | Face | Where |
|---|---|---|
| Voice | **Fraunces** (variable, `opsz 9..144`, `wght 400..900`) | h1, every h2 and h3, the blockquote, the big numerals and stats, the table caption, the menu list, the wordmark, the footer number |
| Interface | **Inter** (variable, `wght 400..700`) | all body copy, every button and pill, both navigations, the marquee, the tracked uppercase labels and eyebrows |
| Devanagari | **Noto Sans Devanagari** 500 | the one word `अमृततुल्य` in the signboard |

**A button is interface, not voice.** Controls, navigation and tracked uppercase
labels stay in Inter: a tracked uppercase serif at 13px is a reading problem, and
a serif on a pill reads as fussy rather than warm. If you add a control, do not
give it `font-display`.

Inter is requested at `400..700`, so **`font-extrabold` (800) has no weight behind
it on interface elements** — use `font-semibold` on controls and `font-bold` on
the caps labels. Fraunces is requested at `400..900`, so `font-extrabold` is fine
on headings.

Three things follow from Fraunces being a serif, and all three are already set:

- **Tracking is roughly half what a grotesque wants.** A serif carries less air
  between letters to begin with. The scale on the page is `-.01em` on small
  display text, `-.015em` on section headings, `-.02em` on the big numerals.
  The hero has its own ramp — see below.
- **Leading is looser.** Headings sit at `1.08`, not `1.02`; the menu board at
  `1.22`. Fraunces has long extenders and 1.02 collides.
- **The fallback is a serif** (`Georgia`). A fallback must match the class of the
  face it stands in for or the swap is a visible jump in metrics and x-height.
  Georgia was previously the fallback for a *grotesque*, which is the same
  mistake in reverse.

`font-optical-sizing: auto` is declared on `.font-display`. It is the initial
value, so it looks redundant — it is there because the `opsz 9..144` axis is the
only reason to pay for a variable font here, and losing it silently would cost
exactly the thing it was bought for.

### Tracking is a function of size

`.hero-title` runs from 33px on a 320px phone to 72px and beyond. One
`letter-spacing` is wrong at one end of a range that wide, so a second clamp
rides the size clamp:

```css
font-size:      clamp(2.05rem, 1.4rem + 2.95vw, 4.5rem);
letter-spacing: clamp(-.113rem, .001rem - .109vw, -.02rem);   /* -.010em -> -.025em */
```

Both are in `rem`, so the ratio survives the root-size ramp in §2. If you change
the size clamp, recompute the tracking clamp against it — measure the em ratio at
each end, do not eyeball a px value.

### If you change a typeface again

1. `tailwind.config.js` — `fontFamily.display` / `.body`, **and the fallbacks**.
2. The Google Fonts `<link>` in the head. Ask for variable ranges, not a list of
   named weights: one file covers every weight the page uses.
3. Re-check the tracking and leading scale above. Values cut for one face are
   wrong for another — this is the step that gets skipped.
4. `build/make-og-card.py` draws the social card in the same two faces and caches
   a static instance of each in `build/.fonts/`. Delete the cached `.ttf` and
   re-run it.
5. `python3 build/build-css.py`.
6. Check the pills. Inter sets wider than the grotesque it replaced and the hero
   pair stopped fitting the signboard column by half a pixel. They carry
   `whitespace-nowrap` so a label can never break mid-phrase, and the row is
   `sm:flex-wrap` so it stacks instead.

## 6. Interaction

Everything here follows from one idea: an interface feels direct when it responds
on press, moves continuously, and can be caught mid-motion.

- **`.tap` / `.tap-wide`** — press feedback on every control. Tailwind's preflight
  removes the tap highlight, so before this there was *no* touch feedback anywhere
  on the page. The press (60ms) is quicker than the release (160ms), the way a
  real button is. `.tap-wide` scales less, because a full-width button travelling
  3% is a lot of movement. Put `.tap` on any control you add.
- **The nav is a material, not a switch.** The script writes `--nav-p` — the first
  120px of scroll as 0..1 — and the stylesheet interpolates background, blur and
  shadow off it together. It used to flip a class at 40px, so the background faded
  while the blur and shadow arrived in a single frame. The header carries **no**
  CSS transition on purpose: the scroll position *is* the animation, and a
  transition on top of it makes the background lag the blur it belongs to.
  `backdrop-filter` is only mounted once `--nav-p > 0`; an idle backdrop root
  costs a compositor layer for no picture.
- **The drawer** grows out of the button that opened it and collapses back to the
  same point, so the way in and the way out are one path. It is driven by
  `data-state`, not by `.hidden` — `.hidden` is added only once the exit finishes,
  and reopening before then cancels it and catches the sheet where it is. `inert`
  keeps the closing sheet out of the tab order.
- **The FAQ** interpolates open where the browser supports `interpolate-size` and
  `::details-content`, and snaps exactly as before where it does not. The whole
  block is inside one `@supports`.
- **The marquee pauses** whenever the strip leaves the viewport.
- **Focus** is a two-band ring: ink outline, jaggery box-shadow. A single jaggery
  ring vanished on the jaggery buttons, which are the primary calls to action. The
  old rule also set `border-radius: 6px` on the focused element, which squared off
  every pill it landed on — outlines follow the element's own radius, so nothing
  is declared.
- **Reduced motion, reduced transparency and increased contrast** are all handled
  separately. Reduced motion is not "no feedback" — the drawer still fades, it
  just does not travel.

Numbers that have to hold still carry `font-variant-numeric: tabular-nums`: the
two counters run up from 40 and from 100, and with proportional figures every
digit that changed shifted the ones beside it.

Antialiasing is asked for **per surface**, not on `<body>`. It thins strokes,
which rescues light-on-dark and washes out dark-on-light, and this page alternates
between the two every section.

## 7. Notes on the old site

- `images/chai-3.jpeg` was captioned "tea plantation" on the old site; it is actually an outlet
  opening. All `alt` text now matches what is really in each photo.
- `images/chai-5.jpeg` is an Instagram QR code, not a photograph, so it is not used as imagery.
- The old footer linked Facebook, Instagram, X, GitHub and YouTube icons to `#`. Those were dropped
  rather than shipped broken; only the confirmed Instagram handle is linked.
- `bundle.js` (751 KB) has been deleted, along with the vendor `404.html` that was its only
  caller. See §3.
