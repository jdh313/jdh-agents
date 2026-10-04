---
name: penpot
description: "Gotchas and versioning rules for driving Penpot through the penpot MCP tools. Use before the first mcp__penpot__ call in a session."
---

# Penpot

## Versions

Save a named version without being asked, with `await penpot.currentFile.saveVersion("<label>")`:

- right after a design change or decision is settled;
- right before anything irreversible: deleting boards or pages, bulk renames, mass text edits.

Label it with what changed ("Health tab split; Issues rename"), confirm it with `findVersions()`, and mention it in the reply.

## Gotchas

- **Text edits can render stale.** Penpot can keep drawing a text's old string (and width) after `characters` is set, while reads return the new value. Only `export_shape` proves the change landed.
- **Force a re-layout in two steps:** set a *different* string, wait about 1s, set the final string, wait again. A same-call `c + " "` then `c` is not reliable. An auto-width text still reporting its old `width` is the tell.
- **`openPage` is async.** After `penpot.openPage(p)`, wait about 1.5s before modifying shapes, or the call fails with "Cannot modify a page that is not currently active". Work one page per `execute_code` call; sleeps inside loops over many shapes hit the 120s task timeout.
- **A suspended tab looks like a hang.** "No heartbeat" means the browser suspended the Penpot tab. Ask the user to focus it, then retry.
