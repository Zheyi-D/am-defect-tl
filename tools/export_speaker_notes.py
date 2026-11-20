"""Export the deck's speaker notes to markdown so the eight presenters can read them anywhere."""

from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
candidates = sorted((ROOT / "reports").glob("slides_draft*.pptx"), key=lambda q: q.stat().st_mtime, reverse=True)
deck = candidates[0] if candidates else None
if deck is None:
    raise SystemExit("no deck found")

prs = Presentation(deck)


def slide_title(slide) -> str:
    """Pick the text box with the largest font — that is the title."""
    best, best_size = "", 0.0
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                size = float(run.font.size.pt) if run.font.size else 0.0
                txt = "".join(r.text for r in para.runs).strip()
                if size > best_size and len(txt) > 4:
                    best, best_size = txt, size
    return best or "(untitled)"


lines = [
    "# Speaker notes — eight parts",
    "",
    f"> Exported from `{deck.name}`; the same text sits in each slide's notes pane.",
    "> Timing appears here only — never on the slides.",
    "",
]

for i, slide in enumerate(prs.slides, start=1):
    note = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
    lines.append(f"## Slide {i} — {slide_title(slide)}")
    lines.append("")
    if note:
        for chunk in note.splitlines():
            chunk = chunk.strip()
            if not chunk:
                continue
            if chunk.startswith("PART "):
                lines.append(f"**{chunk}**")
            elif chunk.startswith("Say:") or chunk.startswith("WHAT:") or chunk.startswith("WHY:") \
                    or chunk.startswith("RESULT:") or chunk.startswith("Caution:") \
                    or chunk.startswith("If ") or chunk.startswith("Follow ") \
                    or chunk.startswith("Walk ") or chunk.startswith("Point ") \
                    or chunk.startswith("Read ") or chunk.startswith("State ") \
                    or chunk.startswith("End ") or chunk.startswith("Then ") \
                    or chunk.startswith("Three ") or chunk.startswith("This ") \
                    or chunk.startswith("Mention ") or chunk.startswith("Do not ") \
                    or chunk.startswith("Keep ") or chunk.startswith("Say ") \
                    or chunk.startswith("And ") or chunk.startswith("But ") \
                    or chunk.startswith("So ") or chunk.startswith("Checkpoint ") \
                    or chunk.startswith("The head ") or chunk.startswith("Adam ") \
                    or chunk.startswith("54 ") or chunk.startswith("Three ") \
                    or chunk.startswith("Measured ") or chunk.startswith("Fair ") \
                    or chunk.startswith("Main suspects ") or chunk.startswith("WHY ") \
                    or chunk.startswith("Open ") or chunk.startswith("1.0000 ") \
                    or chunk.startswith("32,962 ") or chunk.startswith("66/66 ") \
                    or chunk.startswith("Each square ") or chunk.startswith("Walk the ") \
                    or chunk.startswith("Stay ") or chunk.startswith("Thank ") \
                    or chunk.startswith("Read the "):
                lines.append(f"- {chunk}")
            else:
                lines.append(f"- {chunk}")
    lines.append("")

out = ROOT / "reports" / "speaker-notes.md"
out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print(f"wrote {out} ({len(lines)} lines, {len(prs.slides)} slides)")
