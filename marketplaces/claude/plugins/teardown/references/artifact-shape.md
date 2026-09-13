# Teardown artifact shape

The interactive page a teardown produces alongside its vault note: one Artifact per studied repo, one tab per descent layer. The vault note is the durable record; the page is where the reader explores. Everything on the page must also be true in the note or in a surveyor file you verified — the page never carries a claim the record does not.

The worked exemplar is the Home Assistant core page (`Inside Home Assistant`, commit `eb5024a`, 2026-09-13). Its structure is what this file describes.

## When to build it

- **Build it by default** whenever the `Artifact` tool is available. Say so in the one-line session-open statement, so the user can decline.
- **Without the tool** (Codex, a print session, a subagent), skip the page and say so in one line. The vault note is complete on its own; never write page-only content that the note lacks.
- **Build one tab per layer, as the layer lands.** Layer 1 publishes a page with one view; layer 2 republishes it with two. Do not stub future tabs as "coming soon" — a tab appears when its content exists.

## Publishing mechanics

1. **Load `artifact-design` before writing any HTML**, every session. It sets the theme tokens, responsive, and CSP rules; this file sets only the teardown-specific structure.
2. **Keep the HTML in the output directory**: `<outdir>/<repo-name>.html`.
3. **Republish the same file path** for each new layer in a session, so the URL stays the same.
4. **Set `favicon` only on the first publish.** Omit it on every republish.
5. **Record the URL in the vault note's frontmatter** as `artifact: <url>` after the first publish. A later session has a different output directory, so it cannot rely on the file path: it passes that `url` to the Artifact tool with `action: "read"`, builds on the HTML that comes back, and publishes with `url`.

Title the page as a name for the subject, such as `Inside Home Assistant`, not `Home Assistant Teardown — Architecture Study`. Pass the explanation as `description`.

## Page frame

- **View tabs sit at the top of the page**, as a `nav` of buttons with `aria-pressed`, one per landed layer. Each tab shows a name and a short subtitle ("System map" / "Layers & an event trace").
- **The header** holds an eyebrow, the project name as the page `h1`, and one lede per view. Only the active view's lede is shown.
- **Controls that apply to one view appear only inside that view.** Mark them (the exemplar uses `.system-only`) and hide them when another tab is active. A mode switch for the system map must not sit above the Code tab.
- **The view is stored in the URL hash** (`#system`, `#domain`, `#code`) through `history.replaceState` inside a `try`, so a shared link opens the right tab.
- **The commit and the date are stated on the page** — in the Code view's thesis at minimum, and in the footer. Example: "Snippets are excerpts from commit `eb5024a` on the dev branch (2026-09-13)." Link the short SHA to `https://github.com/<owner>/<repo>/tree/<sha>`.
- **Keep the data in named constants** at the top of the script, and render from them. The constants below are the contract between a surveyor file and the page: filling one from a verified file is mechanical.

## Layer 1 — System map

The reader's first question: what are the parts, and how does one thing move through them?

- **Layers are rows of clickable blocks.** Each row is one architectural layer (`Clients`, `Interfaces`, `Core`, `Logic`, `Integrations`, `Persistence`, `Host`, `Devices & protocols`), with a title and a one-line gloss. The central abstraction (the event bus) gets a distinct form: the exemplar draws it as a full-width rail, not another block.
- **A sticky detail panel** beside the map shows the selected block: kicker (its layer), name, tag (its code-level handle, e.g. `hass.bus`), a one-sentence summary, 3 points, and an optional real snippet or record. It stacks under the map below about 940px.
- **Trace mode** is a toggle next to Explore. It steps through one real event, lighting the blocks each step touches, dimming the rest, and badging lit blocks with the step number. The panel shows the step's title, body, and a real payload, with Back/Next buttons, a progress strip, and arrow-key navigation.
- **Variant controls** are allowed when the system genuinely differs by deployment (the exemplar's `HA OS` / `Container` toggle). Blocks absent in a variant render dashed rather than disappearing.

```js
const LAYERS = [{ key: "core", title: "Core", sub: "One process, one event loop" }, /* … */];
const C = [
  { id: "bus", layer: "core", rail: true, name: "Event bus", tag: "hass.bus",
    summary: "…", points: ["…", "…", "…"], code: "…", installs: ["haos", "container"] },
];
const STEPS = [
  { ids: ["states", "bus"], title: "State machine stores it; the bus announces it",
    body: "…", code: '{ "event_type": "state_changed", … }' },
];
```

## Layer 2 — Domain model

The reader's second question: how does the system model the things it manages, and therefore how does an extension fit in?

- **Open with a thesis line** that states the modeling decision in plain words ("Home Assistant never models a brand. It models *a light*, *a lock*, *a battery reading*"), plus a short paragraph on what it buys.
- **Build interactive figures from real record shapes**, never invented ones. Take them from what the code writes: registry JSON in `.storage`, state objects, event payloads, manifest files. Replace credential values with asterisks and shorten ids (`"01J5K2Q8…"`), and change nothing else.
- **Figures that earned their place in the exemplar:**
  - a contract figure: implementers on one side, the base class and its members in the middle, consumers on the other, with lines lighting on hover;
  - a record explorer: a tree of the records one real setup creates (config entry → device → entity), with a card showing the stored JSON and which store file holds it;
  - a moment simulator: a button that fires a real event and shows each representation the system produces for it;
  - a lifecycle stepper: the files an extension passes through, in order.
- **A table of extension routes** belongs here when the platform has routes that need no code (discovery protocols, declarative configs). Wrap it in its own `overflow-x: auto` container.

```js
const HX = [
  { id: "entry", kind: "Config entry", depth: 0, name: "Hue Bridge", sub: "hue integration · added by discovery",
    store: ".storage/core.config_entries", about: ["…"],
    record: { entry_id: "01J5K2Q8…", domain: "hue", source: "zeroconf", data: { host: "192.168.1.40" } } },
];
```

## Layer 3 — Code

The reader's third question: what does the real code look like, which patterns hold it together, and what is it built from?

- **A numbered walkthrough of real functions**: one path through the runtime (the exemplar follows one button press through nine functions). The numbers are a genuine sequence of calls. A list of stations sits on the left and a card on the right shows the selected station:
  - a mono title with the function name;
  - a **thread badge** (`Event loop`, `Executor`, `Recorder thread`) and a **pattern badge** (`Observer`, `Template Method`, or a plain descriptive name);
  - a **permalink** to `blob/<sha>/<path>#L<x>-L<y>`, showing the path and range;
  - 1–2 short paragraphs of explanation;
  - a **snippet of at most 15 lines**, copied from the file at that SHA, with every cut marked by a comment line (`# ...`).
- **A pattern explorer**: a list of the framework's recurring patterns, each with where it lives, a permalink, the explanation, and a snippet.
- **A library table with pinned versions** from the manifest at that SHA (`pyproject.toml`, `package.json`, `go.mod`), grouped by role, each row carrying what the project uses the library for. Versions are right-aligned and use `tabular-nums`.
- **A surprises list**: a short bold claim and one or two sentences each. Only surprises that survived the orchestrator's spot-check belong here; an overturned anomaly may appear, corrected ("Core already uses unparenthesized multi-exception clauses, valid from Python 3.14").

```js
const SHA = "eb5024a1f2dc77261add6ac5416e6bfafd4d497a";
const gh = (path, lines) => `https://github.com/home-assistant/core/blob/${SHA}/${path}${lines ? "#" + lines : ""}`;
const STATIONS = [
  { title: "Integration fires the moment", fn: "EventEntity._trigger_event",
    path: "homeassistant/components/event/__init__.py", lines: "L163-L200",
    thread: "Event loop", pattern: "Encoding trick", text: ["…"], code: `…` },
];
const PATTERNS = [{ name: "…", where: "…", path: "…", lines: "L280-L425", text: ["…"], code: `…` }];
const STACK = [{ group: "Runtime", deps: [["aiohttp", "3.14.3", "The web server behind …"]] }];
const SURPRISES = [["@callback runs on trust", "The decorator sets one attribute. …"]];
```

## Evidence rules on the page

- **Every code claim links to `blob/<full-sha>/<path>#L<x>-L<y>`.** Never link a branch. A snippet without a permalink does not ship.
- **Snippets are copies, trimmed, never paraphrased.** Rewriting a function "for clarity" makes the permalink a lie. When layers 1 and 2 show simplified example code (the exemplar's lifecycle stepper), label it as simplified in the section intro.
- **UNVERIFIED claims stay off the page.** They live in the vault note's `## Unverified` section, where a later pass can close them.
- **Links open in a new tab** with `target="_blank" rel="noopener"`.
