import re


def parse_bib(bib_text):
    """
    Parses a BibTeX string. Returns all keys, duplicates, and a cleaned bib string.
    """
    pattern = re.compile(r'@([a-zA-Z_]+)\s*\{\s*([^,\s]+)\s*,')
    matches = list(pattern.finditer(bib_text))

    if not matches:
        return [], [], bib_text

    cleaned_entries = []
    seen = set()
    duplicates = []
    all_keys = []

    cleaned_entries.append(bib_text[:matches[0].start()])

    for i, match in enumerate(matches):
        key = match.group(2)
        start_idx = match.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(bib_text)

        entry_text = bib_text[start_idx:end_idx]
        all_keys.append(key)

        if key not in seen:
            seen.add(key)
            cleaned_entries.append(entry_text)
        else:
            duplicates.append(key)

    return all_keys, duplicates, "".join(cleaned_entries)


def normalize_entry(entry_text, key):
    """
    Converts BibLaTeX specific fields to BibTeX standard and tracks changes.
    """
    changes = []

    # 1. BibLaTeX 'journaltitle' -> BibTeX 'journal'
    if 'journaltitle' in entry_text:
        entry_text = entry_text.replace('journaltitle', 'journal')
        changes.append(f"[{key}] Converted 'journaltitle' to 'journal'")

    # 2. BibLaTeX 'date' (YYYY-MM-DD) -> BibTeX 'year'
    date_match = re.search(r'date\s*=\s*\{(\d{4})[-\d]*\}', entry_text)
    if date_match:
        year = date_match.group(1)
        entry_text = re.sub(r'date\s*=\s*\{[^}]+\}', f'year = {{{year}}}', entry_text)
        changes.append(f"[{key}] Extracted 'year' from 'date'")

    # 3. BibLaTeX '@online' -> BibTeX '@misc'
    if entry_text.strip().startswith('@online'):
        entry_text = entry_text.replace('@online', '@misc', 1)
        changes.append(f"[{key}] Converted '@online' to '@misc'")

    return entry_text, changes


def clean_and_process(bib_text, all_tex_keys):
    """
    The master cleaner: removes duplicates, removes unused, and fixes formatting.
    """
    pattern = re.compile(r'@([a-zA-Z_]+)\s*\{\s*([^,\s]+)\s*,')
    matches = list(pattern.finditer(bib_text))

    final_bib_parts = []
    change_log = []
    seen_keys = set()
    stats = {"duplicates": 0, "unused": 0, "formatted": 0}

    # Initial preamble
    if matches:
        final_bib_parts.append(bib_text[:matches[0].start()])

    for i, match in enumerate(matches):
        key = match.group(2)
        start_idx = match.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(bib_text)
        entry_text = bib_text[start_idx:end_idx]

        # 1. Check Duplicates
        if key in seen_keys:
            stats["duplicates"] += 1
            change_log.append(f"🗑️ Removed Duplicate: {key}")
            continue

        # 2. Check Usage
        if key not in all_tex_keys:
            stats["unused"] += 1
            change_log.append(f"🧹 Removed Unused: {key}")
            continue

        # 3. Normalize Format
        seen_keys.add(key)
        normalized_text, entry_changes = normalize_entry(entry_text, key)

        if entry_changes:
            stats["formatted"] += 1
            change_log.extend(entry_changes)

        final_bib_parts.append(normalized_text)

    return "".join(final_bib_parts), change_log, stats


def prune_bib(bib_text, all_tex_keys):
    pattern = re.compile(r'@([a-zA-Z_]+)\s*\{\s*([^,\s]+)\s*,')
    matches = list(pattern.finditer(bib_text))

    final_parts = []
    log = []
    seen = set()
    entries_map = {}
    stats = {"duplicates": 0, "unused": 0, "verified": 0}

    if matches:
        final_parts.append(bib_text[:matches[0].start()])

    for i, match in enumerate(matches):
        key = match.group(2)
        start_idx = match.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(bib_text)

        raw_entry = bib_text[start_idx:end_idx].strip()
        entries_map[key] = raw_entry

        # IDENTIFY DUPLICATES
        if key in seen:
            stats["duplicates"] += 1
            log.append({"type": "duplicate", "key": key})  # Log as duplicate
            continue

        # IDENTIFY UNUSED
        if key not in all_tex_keys:
            stats["unused"] += 1
            log.append({"type": "unused", "key": key})
            continue

        seen.add(key)
        final_parts.append(bib_text[start_idx:end_idx])
        stats["verified"] += 1
        log.append({"type": "verified", "key": key})

    return "".join(final_parts), log, stats, entries_map


def unify_bib(bib_text, target="bibtex"):
    """
    Normalizes bibliography entries for either BibTeX or BibLaTeX.
    """
    pattern = re.compile(r'@([a-zA-Z_]+)\s*\{\s*([^,\s]+)\s*,')
    matches = list(pattern.finditer(bib_text))

    final_parts = []
    log = []
    stats = {"formatted": 0}

    if matches:
        final_parts.append(bib_text[:matches[0].start()])

    for i, match in enumerate(matches):
        key = match.group(2)
        start_idx = match.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(bib_text)
        entry = bib_text[start_idx:end_idx]

        changed = False

        if target == "bibtex":
            # --- Convert to Legacy BibTeX ---
            if 'journaltitle' in entry:
                entry = entry.replace('journaltitle', 'journal')
                log.append(f"🛠️ [{key}] journaltitle → journal")
                changed = True

            date_match = re.search(r'date\s*=\s*\{(\d{4})[-\d]*\}', entry)
            if date_match:
                year = date_match.group(1)
                entry = re.sub(r'date\s*=\s*\{[^}]+\}', f'year = {{{year}}}', entry)
                log.append(f"🛠️ [{key}] date → year: {year}")
                changed = True

            if entry.strip().startswith('@online'):
                entry = entry.replace('@online', '@misc', 1)
                log.append(f"🛠️ [{key}] @online → @misc")
                changed = True

        else:
            # --- Convert to Modern BibLaTeX ---
            if 'journal =' in entry or 'journal=' in entry:
                entry = entry.replace('journal', 'journaltitle')
                log.append(f"🚀 [{key}] journal → journaltitle")
                changed = True

            if 'year' in entry and 'date' not in entry:
                entry = entry.replace('year', 'date')
                log.append(f"🚀 [{key}] year → date")
                changed = True

            if entry.strip().startswith('@misc') and 'url' in entry:
                entry = entry.replace('@misc', '@online', 1)
                log.append(f"🚀 [{key}] @misc → @online")
                changed = True

        if changed: stats["formatted"] += 1
        final_parts.append(entry)

    return "".join(final_parts), log, stats


def parse_tex(tex_text):
    cite_patterns = [
        r'\\(?:cite|parencite|textcite|nocite|citeauthor|citeyear)\*?\{([^}]+)\}',
        r'\\autocite\*?\{([^}]+)\}'
    ]
    keys = set()
    for pattern in cite_patterns:
        for match in re.finditer(pattern, tex_text):
            for key in match.group(1).split(','):
                keys.add(key.strip())
    return keys