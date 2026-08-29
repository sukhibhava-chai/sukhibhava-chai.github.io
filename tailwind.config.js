/* ---------------------------------------------------------------------------
   Build config for the compiled stylesheet.

   The page used to load Tailwind's Play CDN, which shipped ~120KB of JS and
   compiled the CSS in the browser on every visit. This config reproduces that
   exact theme so the CLI can emit the same CSS ahead of time.

   Regenerate after adding or changing any class in index.html:

       python3 build/build-css.py

   That runs the CLI and splices the result back into index.html between the
   tw:start / tw:end markers. See HANDOVER.md §3.

   Pinned to Tailwind 3: the page uses v3 comma syntax in arbitrary grid
   values (`lg:grid-cols-[1.1fr,.9fr]`), which v4 no longer accepts.
   --------------------------------------------------------------------------- */
const fs = require('fs')

/* index.html now carries the compiled stylesheet inline, so scanning the file
   as-is would feed Tailwind its own output and let escaped selectors read back
   as class names. Strip the generated block before scanning. */
const html = fs.readFileSync(__dirname + '/index.html', 'utf8')
                .replace(/\/\* tw:start \*\/[\s\S]*?\/\* tw:end \*\//, '')

module.exports = {
  content: [{ raw: html, extension: 'html' }],
  theme: {
    extend: {
      colors: {
        ink:      '#10201E',
        enamel:   '#123B45',
        shallow:  '#1B5563',
        brass:    '#C08A3E',
        jaggery:  '#E6A93C',
        steam:    '#F4EFE4',
        leaf:     '#3E6B4A',
        chai:     '#8A4B2A'
      },
      fontFamily: {
        display: ['"Bricolage Grotesque"', 'Georgia', 'system-ui', 'sans-serif'],
        body:    ['Karla', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        deva:    ['"Noto Sans Devanagari"', 'system-ui', 'sans-serif']
      },
      /* The shell is a CSS variable so one media-query-free clamp can widen
         every section together on 1440s, 4K monitors and television. */
      maxWidth: { shell: 'var(--shell, 1180px)' },
      screens: {
        /* Above 2xl (1536px) the page is being read from further away, not
           closer: a 4K monitor at desk distance and a TV across a room both
           want more measure and more scale, never more columns. */
        '3xl': '1800px',
        '4xl': '2400px'
      }
    }
  }
}
