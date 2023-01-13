## notion-notes

This program extracts annotations (highlights, comments, etc.) from a PDF file,
and exports them to JSON, then post the highlighted text with your comment to a notion page.

### Before you start

you need to create notion integration and get the token and database id from the notion api page
[notion api](https://developers.notion.com/docs/getting-started), don't worry it is just a few steps.

### Installation

```bash
git clone https://github.com/amir-ammar/notion-notes.git
cd notion-notes
pip3 install -r requirements.txt
```

### Usage

```bash
cd notion-notes
python3 notion.py --token <your token> --database <your database id> --pdf <your pdf file> --title <your title>
```

### Help

See `python3 notion.py --help` for more information.

### Dependencies

- Python >= 3.7
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six)

### Known issues and limitations

- While it is generally reliable, pdfminer (the underlying PDF parser) is
  not infallible at extracting text from a PDF. It has been known to fail
  in several different ways:

  - Sometimes it misses or misplaces individual characters, resulting in
    annotations with some or all of the text missing (in the latter case,
    you'll see a warning).

  - Sometimes the characters are captured, but not spaces between the words.
    Tweaking the advanced layout analysis parameters (e.g., `--word-margin`)
    may help with this.

  - Sometimes it extracts all the text but renders it out of order, for
    example, reporting that text at the top of a second column comes before
    text at the end of the first column. This causes pdfannots to return the
    annotations out of order, or to report the wrong outlines (section
    headings) for annotations. You can mostly work around this issue by using
    the `--cols` parameter to force a fixed page layout for the document
    (e.g. `--cols=2` for a typical 2-column document).

- If an annotation (such as a StrikeOut) covers solely whitespace, no text is
  extracted for the annotation, and it will be skipped (with a warning). This
  is an artifact of the way pdfminer reports whitespace with only an implicit
  position defined by surrounding characters.

- When extracting text, we remove all hyphens that immediately precede a line
  break and join the adjacent words. This usually produces the best results
  with LaTeX multi-column documents (e.g. "soft-`\n`ware" becomes "software"),
  but sometimes the hyphen needs to stay (e.g. "memory-`\n`mapped", which will be
  extracted as "memorymapped"), and we can't tell the difference. To disable
  this behaviour, pass `--keep-hyphens`.
