# -*- coding: utf-8 -*-
"""
Rebuild the FAQ in index.html.

    python3 build/make-faq.py

Google requires the visible answer and the FAQPage answer to match word for
word, and keeping two copies in sync by hand is how that breaks. Both are
emitted from the FAQ list below, so edit a question HERE and nowhere else.

Ordered by search intent: cost first, then affordability, then everything a
prospective partner asks before calling.
"""
import sys, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import io, json, re, html

TEL = u'<a class="font-bold text-chai underline underline-offset-2" href="tel:+919849998779">+91&nbsp;98499&nbsp;98779</a>'

FAQ = [
 (u"How much does a Hyderabadi Amruttulya chai franchise cost?",
  u"A Hyderabadi Amruttulya chai franchise starts from &#8377;1 lakh &mdash; that is &#8377;1,00,000 onwards. What a "
  u"particular site works out at depends on the site itself, and it is settled on your discovery call. "
  u"Rent, deposit and licences are yours and sit outside the fee. Call " + TEL + u"."),

 (u"Is there a chai franchise under 2 lakhs in India?",
  u"Yes. Hyderabadi Amruttulya starts from &#8377;1 lakh, which puts the entry cost well under &#8377;2 lakh. The "
  u"outlet is a 100&ndash;200 sq ft counter rather than a sit-down caf&eacute;, so the space and the fit-out "
  u"stay small as well."),

 (u"What makes this an affordable chai franchise?",
  u"Three things. The fee starts from &#8377;1 lakh. An outlet needs 100&ndash;200 sq ft and runs as a counter, "
  u"not a sit-down caf&eacute;, so the fit-out stays small. And chai is something people already buy twice a "
  u"day, so the product needs no explaining."),

 (u"Is a chai franchise profitable?",
  u"Hyderabadi Amruttulya outlets work on a 40%&ndash;50% profit margin. That figure moves with location, "
  u"rent and running costs, so the numbers for your own site are worked through on the discovery call."),

 (u"Do I need experience running a food business?",
  u"No. Most of our enquiries come from first-time business owners, and training is provided before you "
  u"open. What that training covers for someone with no food background is walked through on the "
  u"discovery call."),

 (u"How long does it take to open an outlet?",
  u"The clock runs from signed agreement to opening day, and covers site assessment, setup and training. "
  u"The timeline for your city and your site is confirmed on the discovery call."),

 (u"Can I open a Hyderabadi Amruttulya outlet in Hyderabad?",
  u"Hyderabadi Amruttulya opens outlets across Telangana and Andhra Pradesh, Hyderabad included. Which "
  u"areas are free right now, and how a territory is drawn around one, is confirmed with the franchise "
  u"team on " + TEL + u"."),

 (u"Do I get an exclusive territory?",
  u"Territory terms, how the radius is defined and which cities are currently open are confirmed "
  u"directly with the franchise team on " + TEL + u"."),

 (u"What is Amruttulya chai?",
  u"&ldquo;Amruttulya&rdquo; (&#2309;&#2350;&#2371;&#2340;&#2340;&#2369;&#2354;&#2381;&#2351;) means equal to nectar. It is chai served over a counter rather than "
  u"at a table &mdash; strong, milky and spiced, boiled long. At Hyderabadi Amruttulya every cup of it is "
  u"sweetened with jaggery in place of refined sugar."),

 (u"Why jaggery instead of refined sugar?",
  u"Jaggery is cane juice boiled down and set, rather than stripped white. It is darker and faintly "
  u"smoky, so it holds its own against ginger, cardamom and a long boil where white sugar disappears "
  u"into the milk. It also comes straight from farmers in rural India, which keeps the supply chain "
  u"short. It is the single thing that separates this chai from the tea stall two doors down."),

 (u"Where do the tea and jaggery come from?",
  u"Raw, unprocessed produce comes from farmers in rural India who work by traditional methods and "
  u"age-old wisdom, bought at fair prices, and every cup is sweetened with jaggery in place of refined "
  u"sugar. The specific regions, and how supply reaches partners, are covered on the discovery call."),

 (u"What ongoing support do franchise partners get?",
  u"Training is provided before you open. What continues after that, and what it covers for your "
  u"outlet, is set out on the discovery call."),
]

PLUS = (u'<span class="faq-plus shrink-0 text-brass" aria-hidden="true">\n'
        u'            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>\n'
        u'          </span>')

def plain(h):
    """Answer as an answer engine and Google's FAQ parser will see it."""
    t = re.sub(u'<[^>]+>', u'', h)
    t = html.unescape(t).replace(u' ', u' ')
    return re.sub(u'\\s+', u' ', t).strip()

details = []
for q, a in FAQ:
    details.append(
u'''      <details class="group py-1">
        <summary class="flex items-center justify-between gap-4 py-5">
          <h3 class="font-display text-[1.0625rem] font-extrabold tracking-[-.02em] text-ink sm:text-[1.125rem]">
            %s
          </h3>
          %s
        </summary>
        <p class="pb-6 pr-8 text-[0.9375rem] leading-relaxed text-ink/75">
          %s
        </p>
      </details>''' % (q, PLUS, a))

block = (u'    <div class="mt-10 divide-y divide-ink/10 border-y border-ink/10">\n'
         + u'\n\n'.join(details) + u'\n    </div>')

ld = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "@id": "https://hyderabadiamruttulya.com/#faq",
  "inLanguage": "en-IN",
  "isPartOf": {"@id": "https://hyderabadiamruttulya.com/#webpage"},
  "about": {"@id": "https://hyderabadiamruttulya.com/#franchise"},
  "mainEntity": [
    {"@type": "Question", "name": plain(q),
     "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
    for q, a in FAQ
  ]
}

s = io.open('index.html', encoding='utf-8').read()

# --- swap the visible list -------------------------------------------------
start = s.index(u'    <div class="mt-10 divide-y divide-ink/10 border-y border-ink/10">')
end   = s.index(u'</section>', start)
end   = s.rindex(u'</div>', start, end)          # closes the FAQ column wrapper
end   = s.rindex(u'</div>', start, end) + len(u'</div>')
s = s[:start] + block + s[end:]

# --- swap the FAQPage block ------------------------------------------------
blocks = re.findall(u'<script type="application/ld\\+json">\\s*(\\{.*?\\})\\s*</script>', s, re.S)
old = [b for b in blocks if u'"FAQPage"' in b]
assert len(old) == 1, len(old)
s = s.replace(old[0], json.dumps(ld, indent=2, ensure_ascii=False))

io.open('index.html', 'w', encoding='utf-8').write(s)
print(u'FAQ rebuilt: %d questions' % len(FAQ))
