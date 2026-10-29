from bisect import bisect_right
from dataclasses import dataclass
import unicodedata
import regex
from markdown_it import MarkdownIt


@dataclass(frozen=True)
class Block:
    start: int
    end: int
    kind: str
    section: tuple[str, ...]
    index: int


@dataclass
class Document:
    original: str
    text: str
    spans: list[tuple[int, int]]
    original_lines: list[int]
    blocks: list[Block]

    def source_range(self, start, end):
        first, last = self.spans[start][0], self.spans[end - 1][1]
        return (
            first,
            last,
            bisect_right(self.original_lines, first),
            bisect_right(self.original_lines, last - 1),
        )


def normalize(original: str) -> Document:
    text, spans = [], []
    for match in regex.finditer(r"\X", original):
        cluster = match.group()
        if match.start() == 0 and cluster == "\ufeff":
            continue
        normalized = (
            unicodedata.normalize("NFC", cluster)
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )
        text.append(normalized)
        spans.extend([(match.start(), match.end())] * len(normalized))
    canonical = "".join(text)
    original_lines = [0] + [m.end() for m in regex.finditer(r"\r\n|\r|\n", original)]
    line_offsets = [0] + [m.end() for m in regex.finditer("\n", canonical)]
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = parser.parse(canonical)
    blocks, section = [], []
    for index, token in enumerate(tokens):
        if token.level != 0 or token.nesting == -1 or not token.map:
            continue
        if token.type == "heading_open":
            depth = int(token.tag[1:])
            title = tokens[index + 1].content
            section = section[: depth - 1] + [title]
        first, last = token.map
        start = line_offsets[first] if first < len(line_offsets) else len(canonical)
        end = line_offsets[last] if last < len(line_offsets) else len(canonical)
        blocks.append(Block(start, end, token.type, tuple(section), len(blocks)))
    return Document(original, canonical, spans, original_lines, blocks)
