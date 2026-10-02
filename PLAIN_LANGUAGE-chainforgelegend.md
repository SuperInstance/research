# PLAIN_LANGUAGE — ChainForgeLegend for captains, mechanics, deckhands

You don't need to know React. You don't need to know Quilt. This is the
short version.

## What this is

A small web page. You can type a line of text, hit Enter (or click Add),
and it shows up on a list. Click Remove and the line disappears. That's
it.

It's the same kind of thing you might use to write down a deck-check
list, or to track ice time on a boat, or to keep a short todo list
during a shift.

## What you can do with it

- Open the page
- Type something
- Hit Enter
- See it on the list
- Remove it when it's done
- That's the whole program

If you want to keep the list across sessions or share it with someone
else, that part isn't built yet — the original version doesn't do it,
and we didn't add it. The list lives in your browser tab while the tab
is open.

## Small example

Say you're doing a deck inspection and you want to keep track of what
you've checked. You'd open the page, type "Cleats — port", hit Enter,
type "Cleats — starboard", hit Enter, and so on. When you're done,
you click Remove on each item to clear it. Or you close the tab and
open a fresh one next time.

That sounds almost too small to bother documenting. **It is small.**
That's why it's a good starting point. Every useful web page is one of
these plus a thousand small decisions about what the buttons do, where
the data lives, and what happens when you reload.

## What you could do today

If you wanted, you could:

1. **Use it as-is.** Open the page, type your list. No setup.
2. **Replace the design.** Change the colors, change the labels,
   change what gets saved. The code is in `src/App.jsx` and
   `src/components/ChainforgelegendContainer.jsx`. Open them, edit them,
   refresh the page. No build step required for CSS edits.
3. **Add saving.** Right now the list disappears on reload. You could
   add `localStorage.setItem('list', JSON.stringify(items))` in the
   `useEffect` and it'd persist across sessions. Five lines of code.
4. **Make it a tool for your crew.** Customize the placeholder text to
   match your workflow, save it as a PWA on the boat's tablet, done.

That's the whole landscape.

## If you only have 60 seconds

- A list. Type, Enter, Remove. That's all.
- The list is local. It does not sync. It does not save.
- The code is small and obvious. Open it, change it, it's yours.
- The "Quilt" part is how we describe the program in engineering
  language, not a thing you need to use or understand to operate this.
  If you're an engineer and you want to know about the cell-graph, read
  `QUILT.md`. If you want the upstream story, read `UPSTREAM.md`.

## What's not here yet

This program is intentionally tiny. It does not:

- Save to disk
- Sync to other devices
- Have user accounts
- Send notifications
- Talk to anything else

Those are all reasonable next steps. None of them are wired up. If you
need one of them, the upstream is a fine place to start adding it — the
code is small enough that you can read the whole thing in five minutes.

---

Read time: ~2 minutes. Build time if you start from scratch: ~5 minutes
to get it running. Open the page, type, Enter, Remove. You're done.
