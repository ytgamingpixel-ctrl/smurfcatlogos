# Smurfcat — portfolio site

A one-page site for a Minecraft server logo designer. Work, process, FAQ, and
a Discord contact.

**No build step. No frameworks. No npm install.** Plain HTML, CSS and
JavaScript — open `index.html` in a browser and it works. That's deliberate:
it'll still run and still be editable in five years, and it hosts free on
GitHub Pages.

---

## Adding a logo to the portfolio

Three steps, one command:

1. Drop the image into **`_originals/`**
2. Run **`python add-logos.py`**
3. Commit and push

That's it. The script watermarks the image, crops it square, resizes it,
saves it into `assets/img/work/`, and rebuilds `assets/js/work.js` so it
appears on the site.

**First time only:** `pip install Pillow`

### Naming

The script names each logo from its filename — `crafter realm.png` becomes
"Crafter Realm". If a guess is wrong, edit the `name` in
`assets/js/work.js`; the script keeps your version from then on. It also
keeps the **order** you put the blocks in, so drag your best work to the top
and it stays there.

---

## The "Made by hand" section

Two wide images sit near the top of the page: a Photoshop screenshot of a
poster mid-build, and the finished poster beside it. They're the proof that
the work is drawn by hand rather than generated, which is worth a lot in this
market.

These are **not** square like the portfolio tiles, so they use a separate
script:

1. Put the image in `_originals/showcase/`
2. Run `python add-showcase.py`
3. Reference the new filename in `index.html`

Output lands in `assets/img/process/`, keeping the original shape.

**Filenames starting with `raw-` skip the watermark.** That's deliberate:
finished artwork gets marked like everything else, but a work-in-progress
screenshot shouldn't be — covering your evidence in watermarks undercuts the
point of showing it.

To swap either image, keep the same filename and re-run the script; no HTML
changes needed.

---

## About the watermarks

Every logo on the site has a watermark **burned into the pixels**.

That's deliberate. Anything a website serves can be downloaded by whoever
visits it — right-click blocking doesn't change that, since devtools or a
screenshot gets around it in seconds. The only thing that genuinely protects
the work is publishing images that already carry the mark and keeping the
clean files off the server.

So: clean originals live in **`_originals/`**, which is git-ignored and never
published. Only the watermarked copies go into `assets/img/work/`.

### ⚠ Never put a clean logo straight into `assets/img/work/`

Everything in that folder is public. Always go through `_originals/` and the
script.

One caveat: `.gitignore` protects `_originals/` **only if you deploy with
git**. GitHub's web drag-and-drop uploader ignores `.gitignore` and would
publish the clean files. Use the git commands below and you're fine.

### Tuning it

Open `add-logos.py` and change the values near the top:

| Setting | Does what |
|---|---|
| `ALPHA` | Watermark strength. `70` now. Raise toward `95` for heavier protection, drop toward `50` if it's too destructive |
| `MARK` | The text. Change it if the alias changes |
| `SIZE` | Output resolution, currently `800`. Tiles display around 240px, so a stolen copy isn't much use at this size |
| `DEFAULT_TYPE` | The category new logos get |

Re-run the script after any change and every image regenerates.

---

## What's in the box

```
index.html              The whole site. All the words live here.
404.html                Shown if someone hits a bad URL.
robots.txt              Tells Google it may index the site.
.nojekyll               Stops GitHub Pages mangling folders. Leave it.
add-logos.py            Watermarks new logos and updates the portfolio.
add-showcase.py         Handles the wide images in "Made by hand".
_originals/             Clean logos. Git-ignored - never published.

assets/
  css/style.css         All styling. Colours are at the very top.
  js/work.js            ← YOUR LOGOS GO HERE
  js/main.js            Site behaviour. You shouldn't need to touch this.
  img/work/             The logo images (square portfolio tiles).
  img/process/          The wide "Made by hand" images.
  img/brand/            Favicon.
```

---

## Editing the portfolio by hand

`assets/js/work.js` is generated, but it's a plain list and safe to edit
directly:

```js
{
  name: 'Crafter Realm',        // shown on hover
  type: 'Server logo',          // category (see below)
  img:  'crafter-realm.jpg'     // file in assets/img/work/, or a full link
},
```

Change a name, change a type, or move a block up and down to reorder the
grid. `add-logos.py` respects whatever you set.

`img` also accepts a full `https://` link instead of a filename — but note
that an externally hosted image only carries a watermark if you put one
there yourself, and `cdn.discordapp.com` links **expire after about 24
hours**, so don't use those.

### About the filter buttons

The row of filter buttons above the grid is built from the `type` values. Right
now every logo is a `Server logo`, so **the filter row hides itself** — one
category isn't worth filtering. Add logos with a different `type` (say
`Discord icon`) and the buttons appear automatically.

Keep spellings identical — `Server logo` and `Server Logo` count as two.

### Transparent logos

The tiles crop images to fill the square, which suits artwork that has its own
background. If you add a logo with a *transparent* background, give that entry
some breathing room by adding the `work-card--pad` class — see the comment
next to `.work-card__img` in `style.css`.

---

## Changing your details

| Find this | Where | Change to |
|---|---|---|
| `wolf_708` | `index.html` — **two places** | Your Discord username |
| `Smurfcat` / `SMURFCAT` | `index.html`, `404.html` | If the name ever changes |

> The Discord username appears **twice** in `index.html`: once as visible text,
> and once inside `data-copy="wolf_708"` on the copy button. Change both, or
> the button copies the wrong name.

---

## Changing the colours

Open `assets/css/style.css`. The first block is all the colours:

```css
--accent:      #3F9E3A;   /* grass green — the main brand colour */
--accent-lift: #63C455;   /* brighter version, used on dark sections */
```

Change those two and the whole site re-skins — buttons, links, the marquee
squares, the logo mark, the tick lists.

---

## Viewing it on your own machine

Double-clicking `index.html` mostly works, but browsers block some things on
`file://` URLs. To see it exactly as visitors will:

```bash
python -m http.server 4321
```

Then open <http://localhost:4321>. `Ctrl+C` to stop.

(No Python? `npx serve .` does the same.)

> If you edit a file and the change doesn't show, it's the browser cache.
> Hard-reload with `Ctrl+Shift+R`.

---

## Putting it online with GitHub Pages

Free, and it handles HTTPS.

**1. Create the repository**

```bash
git init
git add .
git commit -m "Initial site"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

**2. Switch Pages on**

**Settings → Pages**. Set **Source: Deploy from a branch**, **Branch: `main`**,
**folder: `/ (root)`**. Save.

The site appears at `https://YOUR-USERNAME.github.io/YOUR-REPO/` within a
minute or two.

**3. Updating later**

Edit, commit, push. GitHub rebuilds in about a minute. No build to run.

---

## When you get a domain

There's no domain wired in yet, so nothing needs undoing. When you have one:

**1.** Create a file called `CNAME` in the site root containing just the
domain, on one line, no `https://`:

```
yourdomain.com
```

**2.** At your registrar, add four A records for the apex domain:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

And these AAAA records if supported:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

For `www` — a CNAME record pointing to `YOUR-USERNAME.github.io`.

**3.** Back in **Settings → Pages**, enter the domain and tick **Enforce
HTTPS** once the certificate is issued (can take up to an hour).

> These are GitHub's current published IPs. If it doesn't work, check
> [GitHub's custom domain docs](https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site).

**4.** Add these two lines into the `<head>` of `index.html`, so search engines
and link previews point at the right place:

```html
<link rel="canonical" href="https://yourdomain.com/">
<meta property="og:url" content="https://yourdomain.com/">
```

---

## The social sharing image

When someone pastes the link into Discord or Twitter, a preview image can
appear. There isn't one yet.

To add it: make a **1200×630 PNG** (a logo on a dark background works well),
save it as `assets/img/brand/og-image.png`, and add this to the `<head>` of
`index.html` once you have a domain:

```html
<meta property="og:image" content="https://yourdomain.com/assets/img/brand/og-image.png">
```

Worth doing properly — most traffic will arrive as a pasted Discord link, and
that image *is* the first impression.

---

## Notes on how it's built

- **No dependencies.** Two Google Fonts are the only external requests.
- **Accessible** — keyboard navigable, skip link, visible focus rings,
  `prefers-reduced-motion` respected, and the FAQ uses native `<details>` so it
  works without JavaScript.
- **The portfolio grid is the only JS-dependent content.** Everything else is
  in the HTML, so search engines read it fine.
- **Square corners everywhere.** `border-radius: 0` is a deliberate nod to
  Minecraft's blocky geometry — it's why the site reads as "gaming" without
  pixel fonts. Keep it if you extend the design.
- **No contact form.** Everything routes to Discord, which is where the work
  actually happens.
- **Portfolio images are watermarked, downscaled to 800px, and served as
  JPEG.** Right-click and drag-to-save are also blocked on the tiles, but
  treat that as a speed bump — the watermark is the real protection.
- **The footer keeps a one-line Mojang notice.** Mojang's brand guidelines ask
  for it on anything commercial using the Minecraft name. It costs nothing and
  is worth leaving in.
