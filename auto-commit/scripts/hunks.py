#!/usr/bin/env python3
"""List the hunks of a git patch and rebuild a patch from a subset of them.

Usage:
  hunks.py list <patch>              print one line per hunk with its ID
  hunks.py pick <patch> H1 H4 ...    print a patch containing only those hunks

Files whose header carries more than content changes (new, deleted, renamed,
copied, mode change, binary) are listed as a single unsplittable unit.
"""
import sys

UNSPLITTABLE = ("new file", "deleted file", "rename ", "copy ", "old mode",
                "new mode", "similarity", "Binary files", "GIT binary patch")


def parse(text):
    """Return a list of (header_lines, [hunk_lines, ...], splittable) per file."""
    files, cur = [], None
    for line in text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            cur = [[line], [], True]
            files.append(cur)
        elif cur is None:
            continue
        elif line.startswith("@@") and cur[2]:
            cur[1].append([line])
        elif cur[1]:
            cur[1][-1].append(line)
        else:
            cur[0].append(line)
            if line.startswith(UNSPLITTABLE):
                cur[2] = False
    return files


def units(files):
    """Yield (id, path, header, hunks) where hunks is the list this ID covers."""
    n = 0
    for header, hunks, splittable in files:
        path = header[0].split(" b/", 1)[-1].strip()
        if splittable and hunks:
            for h in hunks:
                n += 1
                yield f"H{n}", path, header, [h]
        else:
            n += 1
            yield f"H{n}", path, header, hunks


def summary(header, hunks):
    if not hunks or not hunks[0][0].startswith("@@"):
        kinds = [l.strip() for l in header[1:] if l.startswith(UNSPLITTABLE)]
        return "whole file: " + (", ".join(kinds) or "header only")
    body = [l for h in hunks for l in h[1:]]
    adds = sum(l.startswith("+") for l in body)
    dels = sum(l.startswith("-") for l in body)
    first = next((l[1:].strip() for l in body if l[:1] in "+-" and l[1:].strip()), "")
    return f"{hunks[0][0].split('@@')[1].strip()} +{adds}/-{dels}  {first[:70]}"


def main(argv):
    if len(argv) < 3 or argv[1] not in ("list", "pick"):
        sys.exit(__doc__)
    with open(argv[2], encoding="utf-8", errors="surrogateescape") as f:
        files = parse(f.read())
    all_units = list(units(files))

    if argv[1] == "list":
        for uid, path, header, hunks in all_units:
            print(f"{uid}\t{path}\t{summary(header, hunks)}")
        return

    wanted = set(argv[3:])
    unknown = wanted - {u[0] for u in all_units}
    if unknown:
        sys.exit(f"unknown hunk IDs: {' '.join(sorted(unknown))}")
    out, last_header = [], None
    for uid, _, header, hunks in all_units:
        if uid not in wanted:
            continue
        if header is not last_header:
            out.extend(header)
            last_header = header
        for h in hunks:
            out.extend(h)
    sys.stdout.write("".join(out))


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="surrogateescape")
    main(sys.argv)
