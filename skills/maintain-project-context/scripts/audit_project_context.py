#!/usr/bin/env python3
"""Read-only project-context inventory and candidate-signal audit."""

import argparse
import hashlib
import json
import os
import re
import string
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import unescape as html_unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote


MIN_PYTHON = (3, 9)
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".venv",
    "build",
    "coverage",
    "dist",
    "log",
    "node_modules",
    "tmp",
    "vendor",
}
TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".mdx",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".csv",
    ".tsv",
}
STRUCTURED_TEXT_EXTENSIONS = {".csv", ".json", ".toml", ".tsv", ".yaml", ".yml"}
MAX_MULTILINE_LINK_SCAN_CHARS = 1024 * 1024
DEFAULT_MAX_CONTENT_BYTES = 8 * 1024 * 1024
HTML_RESOURCE_ATTRIBUTES: Dict[str, Set[str]] = {
    "a": {"href", "ping"},
    "area": {"href", "ping"},
    "audio": {"src"},
    "blockquote": {"cite"},
    "body": {"background"},
    "button": {"formaction"},
    "del": {"cite"},
    "embed": {"src"},
    "form": {"action"},
    "frame": {"src"},
    "iframe": {"src"},
    # The HTML tree builder rewrites an HTML-namespace <image> start tag to
    # <img>; Python's HTMLParser keeps the literal name.
    "image": {"src", "srcset"},
    "img": {"src", "srcset"},
    "input": {"formaction", "src"},
    "ins": {"cite"},
    "link": {"href", "imagesrcset"},
    "object": {"data"},
    "q": {"cite"},
    "script": {"src"},
    "source": {"src", "srcset"},
    "table": {"background"},
    "tbody": {"background"},
    "td": {"background"},
    "tfoot": {"background"},
    "th": {"background"},
    "thead": {"background"},
    "track": {"src"},
    "tr": {"background"},
    "video": {"poster", "src"},
}
SVG_RESOURCE_ATTRIBUTES: Dict[str, Set[str]] = {
    # SVG2 uses href; xlink:href remains common in existing documentation.
    "a": {"href", "xlink:href"},
    "animate": {"href", "xlink:href"},
    "animatemotion": {"href", "xlink:href"},
    "animatetransform": {"href", "xlink:href"},
    "feimage": {"href", "xlink:href"},
    "filter": {"href", "xlink:href"},
    "image": {"href", "xlink:href"},
    "lineargradient": {"href", "xlink:href"},
    "mpath": {"href", "xlink:href"},
    "pattern": {"href", "xlink:href"},
    "radialgradient": {"href", "xlink:href"},
    "script": {"href", "xlink:href"},
    "set": {"href", "xlink:href"},
    "textpath": {"href", "xlink:href"},
    "use": {"href", "xlink:href"},
}
HTML_VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "frame",
    "hr",
    "image",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
SVG_HTML_INTEGRATION_POINTS = {"desc", "foreignobject", "title"}
HTML_RAW_TEXT_ELEMENTS = {
    "iframe",
    "noembed",
    "noframes",
    "plaintext",
    "script",
    "style",
    "textarea",
    "title",
    "xmp",
}
LIFECYCLE_OPAQUE_HTML_ELEMENTS = {
    "iframe",
    "noembed",
    "noframes",
    "script",
    "style",
    "template",
    "title",
}
FOREIGN_CONTENT_HTML_BREAKOUT_TAGS = {
    "b",
    "big",
    "blockquote",
    "body",
    "br",
    "center",
    "code",
    "dd",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "hr",
    "i",
    "img",
    "li",
    "listing",
    "menu",
    "meta",
    "nobr",
    "ol",
    "p",
    "pre",
    "ruby",
    "s",
    "small",
    "span",
    "strike",
    "strong",
    "sub",
    "sup",
    "table",
    "tt",
    "u",
    "ul",
    "var",
}
TASK_ID_TOKEN_WRAPPERS = "`*_[](){}<>.,:;!?\"'"
DATED_HEADING_RE = re.compile(r"^\s*#{1,6}\s+.*\b20\d{2}-\d{2}-\d{2}\b", re.I)
MARKDOWN_HEADING_RE = re.compile(r"^[ ]{0,3}(#{1,6})(?:[ \t]+|$)")
MARKDOWN_SETEXT_RE = re.compile(r"^[ ]{0,3}(=+|-+)[ \t]*$")
MARKDOWN_THEMATIC_BREAK_RE = re.compile(
    r"^[ ]{0,3}(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})$"
)
MARKDOWN_FENCE_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")
MARKDOWN_FRONT_MATTER_START_RE = re.compile(r"^\ufeff?---[ \t]*(?:\r?\n)?$")
MARKDOWN_FRONT_MATTER_END_RE = re.compile(r"^(?:---|\.\.\.)[ \t]*(?:\r?\n)?$")
MARKDOWN_NON_PARAGRAPH_PREFIX_RE = re.compile(
    r"^[ ]{0,3}(?:[-+*][ \t]+|\d{1,9}[.)][ \t]+|>[ \t]?)"
)
MARKDOWN_LIST_ITEM_RE = re.compile(
    r"^(?P<indent>[ ]{0,3})(?P<marker>[-+*]|\d{1,9}[.)])(?P<padding>[ \t]+)"
)
UNRESOLVED_RE = re.compile(
    r"\b(?:TODO|FIXME|BLOCKED|UNRESOLVED|OPEN QUESTION|PENDING)\b|"
    r"\b(?:блокер|заблокирован|нереш[её]н|открыт(?:ый|ые)? вопрос)\w*",
    re.I,
)
SUPERSEDED_RE = re.compile(
    r"\b(?:superseded|deprecated|obsolete|replaced by)\b|"
    r"\b(?:устарел\w*|замен[её]н\w*|больше не актуал\w*)",
    re.I,
)
STATUS_RE = re.compile(
    r"\b(?:merged|completed|complete|done|closed|cancelled|canceled)\b|"
    r"\b(?:заверш[её]н\w*|выполнен\w*|закрыт\w*|отмен[её]н\w*|слит\w*)",
    re.I,
)
MARKDOWN_REFERENCE_SHORTCUT_RE = re.compile(
    r"(?<!!)!?\[((?:\\.|[^\]\\])+)\](?!\[)"
)
MARKDOWN_REFERENCE_DEFINITION_RE = re.compile(
    r"^[ ]{0,3}\[((?:\\.|[^\]\\])+)\]:"
)
MARKDOWN_REFERENCE_CONTINUATION_PREFIX_RE = re.compile(r"^[ ]{1,3}")
MARKDOWN_CHARACTER_REFERENCE_RE = re.compile(
    r"&(?:#[xX][0-9A-Fa-f]{1,8}|#[0-9]{1,8}|[A-Za-z][A-Za-z0-9]{1,31});"
)
MARKDOWN_HTML_COMMENT_BLOCK_START_RE = re.compile(r"^[ ]{0,3}<!--")
MARKDOWN_RAW_HTML_TAG_RE = re.compile(
    r"^[ ]{0,3}<(?P<tag>script|pre|style|textarea)(?:[ \t>]|$)", re.I
)
MARKDOWN_HTML_BLOCK_TAG_RE = re.compile(
    r"^[ ]{0,3}</?(?:address|article|aside|base|basefont|blockquote|body|caption|"
    r"center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|"
    r"figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|"
    r"legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|"
    r"param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|"
    r"track|ul)(?:[ \t/>]|$)",
    re.I,
)
MARKDOWN_COMPLETE_HTML_OPENING_TAG_RE = re.compile(
    r"^[ ]{0,3}<[A-Za-z][A-Za-z0-9-]*"
    r"(?:[ \t]+[A-Za-z_:][A-Za-z0-9_.:-]*"
    r"(?:[ \t]*=[ \t]*(?:[^ \t\"'=<>`]+|'[^']*'|\"[^\"]*\"))?)*"
    r"[ \t]*/?>[ \t]*$"
)
MARKDOWN_COMPLETE_HTML_CLOSING_TAG_RE = re.compile(
    r"^[ ]{0,3}</[A-Za-z][A-Za-z0-9-]*[ \t]*>[ \t]*$"
)
MARKDOWN_COMPLETE_HTML_DECLARATION_RE = re.compile(
    r"^<![A-Z]+(?:[ \t\r\n]+[^>]*)?>$"
)
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
SUPERSESSION_FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s*)?superseded by\s*:\s*(.*?)\s*$",
    re.I,
)
EMPTY_SUPERSESSION_VALUES = {
    "",
    "none",
    "n/a",
    "na",
    "not applicable",
    "adr link or none",
}


@dataclass
class AuditFile:
    absolute_path: Path
    relative_path: str
    scope: str
    size: int
    modified_at: str
    age_days: int
    location_state: str
    protected: bool
    binary: bool
    git_state: str = "not_checked"
    line_count: Optional[int] = None
    nonblank_lines: Optional[int] = None
    markdown_heading_count: int = 0
    task_heading_count: int = 0
    task_id_count: int = 0
    max_section_lines: int = 0
    dated_heading_count: int = 0
    unresolved_marker_count: int = 0
    superseded_marker_count: int = 0
    completed_marker_count: int = 0
    status_only_signal: bool = False
    task_ids: List[str] = field(default_factory=list)
    broken_targets: List[str] = field(default_factory=list)
    incoming_link_count: int = 0
    incoming_link_coverage: str = "not_checked"
    duplicate_group: Optional[str] = None
    fingerprint: Optional[str] = None
    link_parse_incomplete: bool = False


@dataclass(frozen=True)
class MarkdownReferenceTargetMatch:
    """Small match-compatible value for parsed reference destinations."""

    groups: Tuple[Optional[str], ...]
    end_position: int

    def group(self, index: int) -> Optional[str]:
        return self.groups[index - 1]

    def end(self) -> int:
        return self.end_position


class MarkdownHtmlTargetParser(HTMLParser):
    """Collect non-executable local-reference candidates from raw HTML."""

    def __init__(
        self,
        base_href: Optional[str] = None,
        base_seen: bool = False,
        template_depth: int = 0,
        element_stack: Optional[Sequence[Tuple[str, str]]] = None,
        template_raw_text_tag: Optional[str] = None,
    ) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: Set[Tuple[str, Optional[str]]] = set()
        self.base_href = base_href
        self.base_seen = base_seen
        self.template_depth = template_depth
        self.element_stack = list(element_stack or ())
        self.template_raw_text_tag = template_raw_text_tag
        self.resource_parse_incomplete = False
        self.declarative_shadow_template_seen = False

    def child_namespace(self) -> str:
        if not self.element_stack:
            return "html"
        parent_tag, parent_namespace = self.element_stack[-1]
        if (
            parent_namespace == "svg"
            and parent_tag in SVG_HTML_INTEGRATION_POINTS
        ):
            return "html"
        return parent_namespace

    def element_namespace(self, normalized_tag: str) -> str:
        namespace = self.child_namespace()
        if namespace == "html" and normalized_tag == "svg":
            return "svg"
        if namespace == "html" and normalized_tag == "math":
            return "mathml"
        return namespace

    def apply_foreign_content_breakout(
        self,
        normalized_tag: str,
        first_attributes: Dict[str, Optional[str]],
    ) -> None:
        namespace = self.child_namespace()
        font_breakout = normalized_tag == "font" and any(
            name in first_attributes for name in {"color", "face", "size"}
        )
        if namespace == "html" or not (
            normalized_tag in FOREIGN_CONTENT_HTML_BREAKOUT_TAGS
            or font_breakout
        ):
            return
        while self.element_stack and self.element_stack[-1][1] != "html":
            self.element_stack.pop()

    def handle_element(
        self,
        tag: str,
        attrs: List[Tuple[str, Optional[str]]],
        *,
        push: Optional[bool],
    ) -> None:
        normalized_tag = tag.casefold()
        first_attributes: Dict[str, Optional[str]] = {}
        for name, value in attrs:
            first_attributes.setdefault(name.casefold(), value)
        if self.template_depth:
            if self.template_raw_text_tag is not None:
                return
            if normalized_tag == "template":
                self.template_depth += 1
            elif normalized_tag in HTML_RAW_TEXT_ELEMENTS:
                self.template_raw_text_tag = normalized_tag
            return
        self.apply_foreign_content_breakout(normalized_tag, first_attributes)
        namespace = self.element_namespace(normalized_tag)
        if normalized_tag == "template" and namespace == "html":
            if (first_attributes.get("shadowrootmode") or "").casefold() in {
                "open",
                "closed",
            }:
                self.resource_parse_incomplete = True
                self.declarative_shadow_template_seen = True
            self.template_depth = 1
            return
        if push is None:
            push = namespace == "html"
        if (
            namespace == "html"
            and normalized_tag == "meta"
            and (first_attributes.get("http-equiv") or "").casefold() == "refresh"
            and first_attributes.get("content")
        ):
            # Refresh content has a separate URL grammar. Until it is parsed,
            # do not certify repository-reference coverage.
            self.resource_parse_incomplete = True
        if normalized_tag in {"pre", "style"}:
            # CSS has its own URL grammar, while CommonMark HTML blocks keep
            # nested HTML inside pre outside this bounded parser. Do not
            # certify reference coverage when either body stays opaque.
            self.resource_parse_incomplete = True
        if first_attributes.get("style"):
            # CSS declarations can carry repository references through more
            # than url(), including image-set() string images. Keep coverage
            # conservative until the full style-attribute grammar is parsed.
            self.resource_parse_incomplete = True
        namespace_resource_map = (
            HTML_RESOURCE_ATTRIBUTES
            if namespace == "html"
            else SVG_RESOURCE_ATTRIBUTES if namespace == "svg" else {}
        )
        namespace_resource_attributes = namespace_resource_map.get(
            normalized_tag, set()
        )
        all_known_resource_attributes = (
            HTML_RESOURCE_ATTRIBUTES.get(normalized_tag, set())
            | SVG_RESOURCE_ATTRIBUTES.get(normalized_tag, set())
        )
        if any(
            first_attributes.get(attribute)
            for attribute in (
                all_known_resource_attributes - namespace_resource_attributes
            )
        ):
            # A known HTML/SVG resource-shaped element appeared in another
            # namespace. Do not invent an incoming edge or certify coverage.
            self.resource_parse_incomplete = True
        resource_attributes = namespace_resource_attributes
        if namespace == "html" and normalized_tag == "input":
            input_type = (first_attributes.get("type") or "text").casefold()
            if input_type == "image":
                resource_attributes = {"formaction", "src"}
            elif input_type == "submit":
                resource_attributes = {"formaction"}
            else:
                resource_attributes = set()
        elif namespace == "html" and normalized_tag == "button":
            button_type = (
                first_attributes.get("type") or "submit"
            ).casefold()
            resource_attributes = (
                set()
                if button_type in {"button", "reset"}
                else {"formaction"}
            )
        seen_resource_attributes: Set[str] = set()
        for name, value in attrs:
            normalized_name = name.casefold()
            if value and "url(" in value.casefold():
                self.resource_parse_incomplete = True
            if normalized_tag == "iframe" and normalized_name == "srcdoc" and value:
                # srcdoc is a nested HTML document with its own resource graph.
                self.resource_parse_incomplete = True
            if (
                normalized_tag == "script"
                and namespace == "html"
                and normalized_name in {"href", "xlink:href"}
                and value
            ):
                # Without carrying HTML/SVG namespaces, do not treat SVG-only
                # script references as valid in an HTML script context.
                self.resource_parse_incomplete = True
            if (
                namespace == "html"
                and normalized_tag == "base"
                and normalized_name == "href"
            ):
                if not self.base_seen:
                    self.base_seen = True
                    self.base_href = value or ""
                continue
            if normalized_name not in resource_attributes:
                continue
            # HTML keeps the first duplicate attribute. Later duplicates must
            # not manufacture extra repository references.
            if normalized_name in seen_resource_attributes:
                continue
            seen_resource_attributes.add(normalized_name)
            if not value:
                continue
            if normalized_name in {"srcset", "imagesrcset"}:
                self.targets.update(
                    (target, self.base_href)
                    for target in html_srcset_targets(value)
                )
            elif normalized_name == "ping":
                self.targets.update(
                    (target, self.base_href) for target in value.split()
                )
            else:
                self.targets.add((value, self.base_href))
        if push and not (
            namespace == "html" and normalized_tag in HTML_VOID_ELEMENTS
        ):
            self.element_stack.append((normalized_tag, namespace))

    def handle_starttag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        self.handle_element(tag, attrs, push=True)

    def handle_startendtag(
        self, tag: str, attrs: List[Tuple[str, Optional[str]]]
    ) -> None:
        if tag.casefold() == "template" and self.child_namespace() == "html":
            # HTML ignores the XML-style slash for non-void template.
            self.handle_starttag(tag, attrs)
            return
        if self.template_depth:
            # HTML also ignores the slash on raw-text children inside inert
            # template content, so preserve that state until its real end tag.
            self.handle_element(tag, attrs, push=None)
            return
        # HTML ignores the XML-style slash for non-void elements; foreign
        # content honors it.
        self.handle_element(tag, attrs, push=None)

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.casefold()
        if self.template_depth and self.template_raw_text_tag is not None:
            if normalized_tag == self.template_raw_text_tag:
                self.template_raw_text_tag = None
            return
        if normalized_tag == "template" and self.template_depth:
            self.template_depth -= 1
            return
        for index in range(len(self.element_stack) - 1, -1, -1):
            if self.element_stack[index][0] == normalized_tag:
                del self.element_stack[index:]
                return


def html_template_is_declarative_shadow_root(token: str) -> bool:
    """Return whether a complete template token declares a shadow root."""
    parser = MarkdownHtmlTargetParser()
    parser.feed(token)
    parser.close()
    return parser.declarative_shadow_template_seen


def html_srcset_targets(raw: str) -> Set[str]:
    """Return srcset URLs without splitting commas inside data URLs."""
    targets: Set[str] = set()
    cursor = 0
    while cursor < len(raw):
        while cursor < len(raw) and (raw[cursor].isspace() or raw[cursor] == ","):
            cursor += 1
        if cursor >= len(raw):
            break
        url_start = cursor
        while cursor < len(raw) and not raw[cursor].isspace():
            cursor += 1
        url = raw[url_start:cursor]
        ended_with_separator = url.endswith(",")
        url = url.rstrip(",")
        if url:
            targets.add(url)
        if ended_with_separator:
            continue
        while cursor < len(raw) and raw[cursor] != ",":
            cursor += 1
        if cursor < len(raw):
            cursor += 1
    return targets


def html_raw_text_closing_suffix(raw: str, tag: str) -> Optional[str]:
    """Return a fragment beginning at the first valid raw-text closing tag."""
    if tag == "plaintext":
        return None
    closing_prefix = f"</{tag}"
    search_cursor = 0
    while True:
        candidate = raw.casefold().find(closing_prefix, search_cursor)
        if candidate < 0:
            return None
        boundary = candidate + len(closing_prefix)
        if boundary < len(raw) and raw[boundary] not in " \t>":
            search_cursor = candidate + 2
            continue
        candidate_end = markdown_inline_html_token_end(raw, candidate)
        if candidate_end is not None and re.fullmatch(
            rf"</{re.escape(tag)}[ \t]*>",
            raw[candidate:candidate_end],
            re.I,
        ):
            return raw[candidate:]
        search_cursor = candidate + 2


def html_raw_text_has_non_commonmark_closer(raw: str, tag: str) -> bool:
    """Detect a browser-significant closer that CommonMark keeps in a raw block."""
    closing_prefix = f"</{tag}"
    search_cursor = 0
    lowered = raw.casefold()
    while True:
        candidate = lowered.find(closing_prefix, search_cursor)
        if candidate < 0:
            return False
        boundary = candidate + len(closing_prefix)
        if boundary >= len(raw):
            return True
        boundary_character = raw[boundary]
        if boundary_character == ">":
            search_cursor = boundary + 1
            continue
        if boundary_character in " \t\r\n\f/":
            return True
        search_cursor = candidate + 2


def html_visible_signal_text_with_state(
    raw: str,
    raw_text_state: Optional[
        Tuple[str, int, Optional[str], Tuple[str, ...]]
    ] = None,
) -> Tuple[
    str, Optional[Tuple[str, int, Optional[str], Tuple[str, ...]]]
]:
    """Strip raw HTML while keeping inline raw-text element bodies opaque."""
    pieces: List[str] = []
    cursor = 0
    while cursor < len(raw):
        if raw_text_state is not None:
            (
                raw_text_tag,
                raw_text_depth,
                template_raw_text_tag,
                template_foreign_stack,
            ) = raw_text_state
            if raw_text_tag == "template":
                search_cursor = cursor
                while True:
                    candidate = raw.find("<", search_cursor)
                    if candidate < 0:
                        return html_unescape("".join(pieces)), raw_text_state
                    candidate_end = markdown_inline_html_token_end(raw, candidate)
                    if candidate_end is None:
                        search_cursor = candidate + 1
                        continue
                    token = raw[candidate:candidate_end]
                    if template_raw_text_tag is not None:
                        if re.fullmatch(
                            rf"</{re.escape(template_raw_text_tag)}[ \t]*>",
                            token,
                            re.I,
                        ):
                            template_raw_text_tag = None
                            raw_text_state = (
                                raw_text_tag,
                                raw_text_depth,
                                template_raw_text_tag,
                                template_foreign_stack,
                            )
                    elif template_foreign_stack:
                        closing_tag = re.fullmatch(
                            r"</([A-Za-z][A-Za-z0-9-]*)[ \t]*>",
                            token,
                            re.I,
                        )
                        opening_tag = re.match(
                            r"<([A-Za-z][A-Za-z0-9-]*)", token
                        )
                        if closing_tag is not None:
                            normalized_closing = closing_tag.group(1).casefold()
                            if normalized_closing in template_foreign_stack:
                                matching_index = len(template_foreign_stack) - 1 - (
                                    template_foreign_stack[::-1].index(
                                        normalized_closing
                                    )
                                )
                                template_foreign_stack = template_foreign_stack[
                                    :matching_index
                                ]
                        elif (
                            opening_tag is not None
                            and not re.search(r"/[ \t]*>$", token)
                        ):
                            template_foreign_stack += (
                                opening_tag.group(1).casefold(),
                            )
                        raw_text_state = (
                            raw_text_tag,
                            raw_text_depth,
                            template_raw_text_tag,
                            template_foreign_stack,
                        )
                    elif re.fullmatch(r"</template[ \t]*>", token, re.I):
                        raw_text_depth -= 1
                        cursor = candidate_end
                        if raw_text_depth == 0:
                            raw_text_state = None
                            break
                        raw_text_state = (
                            raw_text_tag,
                            raw_text_depth,
                            template_raw_text_tag,
                            template_foreign_stack,
                        )
                    elif re.match(r"<template(?:[ \t/>]|$)", token, re.I):
                        # HTML ignores a self-closing slash on template.
                        raw_text_depth += 1
                        raw_text_state = (
                            raw_text_tag,
                            raw_text_depth,
                            template_raw_text_tag,
                            template_foreign_stack,
                        )
                    else:
                        opening_tag = re.match(
                            r"<([A-Za-z][A-Za-z0-9-]*)", token
                        )
                        if (
                            opening_tag is not None
                            and opening_tag.group(1).casefold() in {"math", "svg"}
                            and not re.search(r"/[ \t]*>$", token)
                        ):
                            template_foreign_stack = (
                                opening_tag.group(1).casefold(),
                            )
                            raw_text_state = (
                                raw_text_tag,
                                raw_text_depth,
                                template_raw_text_tag,
                                template_foreign_stack,
                            )
                        elif (
                            opening_tag is not None
                            and opening_tag.group(1).casefold()
                            in HTML_RAW_TEXT_ELEMENTS
                        ):
                            template_raw_text_tag = (
                                opening_tag.group(1).casefold()
                            )
                            raw_text_state = (
                                raw_text_tag,
                                raw_text_depth,
                                template_raw_text_tag,
                                template_foreign_stack,
                            )
                    search_cursor = candidate_end
                continue
            closing_prefix = f"</{raw_text_tag}"
            search_cursor = cursor
            closing_start = -1
            closing_end: Optional[int] = None
            while True:
                candidate = raw.lower().find(closing_prefix, search_cursor)
                if candidate < 0:
                    break
                boundary = candidate + len(closing_prefix)
                if boundary < len(raw) and raw[boundary] not in " \t>":
                    search_cursor = candidate + 2
                    continue
                candidate_end = markdown_inline_html_token_end(raw, candidate)
                if (
                    candidate_end is not None
                    and raw[candidate:candidate_end].lower().startswith(
                        closing_prefix
                    )
                ):
                    closing_start = candidate
                    closing_end = candidate_end
                    break
                search_cursor = candidate + 2
            if closing_start < 0 or closing_end is None:
                return html_unescape("".join(pieces)), raw_text_state
            cursor = closing_end
            raw_text_state = None
            continue
        opening = raw.find("<", cursor)
        if opening < 0:
            pieces.append(raw[cursor:])
            break
        html_end = markdown_inline_html_token_end(raw, opening)
        if html_end is None:
            # Malformed HTML-like text is rendered literally. Preserve this
            # opener and continue so a later valid raw-HTML token can still be
            # removed from lifecycle signals.
            pieces.append(raw[cursor : opening + 1])
            cursor = opening + 1
            continue
        pieces.append(raw[cursor:opening])
        token = raw[opening:html_end]
        opening_tag = re.match(r"<([A-Za-z][A-Za-z0-9-]*)", token)
        if (
            opening_tag is not None
            and opening_tag.group(1).casefold()
            in LIFECYCLE_OPAQUE_HTML_ELEMENTS
            and not (
                opening_tag.group(1).casefold() == "template"
                and html_template_is_declarative_shadow_root(token)
            )
        ):
            raw_text_state = (opening_tag.group(1).casefold(), 1, None, ())
        cursor = html_end
    return html_unescape("".join(pieces)), raw_text_state


def html_visible_signal_text(raw: str) -> str:
    """Strip complete CommonMark raw HTML from one standalone text fragment."""
    visible, _ = html_visible_signal_text_with_state(raw)
    return visible


def strip_html_comments(raw: str, in_comment: bool = False) -> Tuple[str, bool]:
    """Mask HTML comments, preserving enough state for multiline blocks."""
    pieces: List[str] = []
    cursor = 0
    while cursor < len(raw):
        if in_comment:
            closing = raw.find("-->", cursor)
            if closing < 0:
                pieces.append(" " * (len(raw) - cursor))
                return "".join(pieces), True
            pieces.append(" " * (closing + 3 - cursor))
            cursor = closing + 3
            in_comment = False
            continue
        opening = raw.find("<!--", cursor)
        if opening < 0:
            pieces.append(raw[cursor:])
            break
        pieces.append(raw[cursor:opening])
        closing = raw.find("-->", opening + 4)
        if closing < 0:
            pieces.append(" " * (len(raw) - opening))
            return "".join(pieces), True
        pieces.append(" " * (closing + 3 - opening))
        cursor = closing + 3
    return "".join(pieces), in_comment


def fail(message: str, code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def parse_age_buckets(raw: str) -> List[int]:
    try:
        values = sorted({int(value.strip()) for value in raw.split(",") if value.strip()})
    except ValueError:
        fail("--age-buckets must contain comma-separated integers")
    if not values or any(value <= 0 for value in values):
        fail("--age-buckets values must be positive")
    return values


def compile_task_id_pattern(raw: Optional[str]) -> Optional[re.Pattern]:
    if not raw:
        return None
    try:
        return re.compile(raw)
    except re.error as error:
        fail(f"--task-id-regex is invalid: {error}")
    return None


def configured_task_ids(
    line: str,
    task_id_pattern: Optional[re.Pattern],
    defined_reference_labels: Optional[Set[str]] = None,
) -> Set[str]:
    if task_id_pattern is None:
        return set()
    # Inspect only rendered-visible text. Raw inline destinations and titles
    # are metadata and must not create task chronology signals.
    candidate_sources = [
        html_visible_signal_text(
            markdown_visible_signal_text(line, defined_reference_labels)
        )
    ]
    candidates = {
        raw.strip(TASK_ID_TOKEN_WRAPPERS)
        for source in candidate_sources
        for raw in source.replace("][", "] [").split()
    }
    return {
        candidate
        for candidate in candidates
        if candidate and task_id_pattern.fullmatch(candidate)
    }


def markdown_front_matter_end(path: Path) -> Optional[int]:
    """Return the inclusive closing line number for valid leading front matter."""
    with path.open("r", encoding="utf-8") as handle:
        first_line = handle.readline()
        if not MARKDOWN_FRONT_MATTER_START_RE.match(first_line):
            return None
        for line_number, line in enumerate(handle, start=2):
            if MARKDOWN_FRONT_MATTER_END_RE.match(line):
                return line_number
    # A leading thematic break without a closing delimiter is ordinary body
    # content, not an unterminated metadata block that hides the whole file.
    return None


def markdown_fence_closes(line: str, character: str, minimum_length: int) -> bool:
    candidate = line.rstrip("\r\n")
    match = re.fullmatch(r"[ ]{0,3}([`~]+)[ \t]*", candidate)
    return bool(
        match
        and match.group(1)[0] == character
        and set(match.group(1)) == {character}
        and len(match.group(1)) >= minimum_length
    )


def markdown_fence_opens(line: str) -> Optional[re.Match]:
    """Return a valid CommonMark fence opener, excluding invalid info strings."""
    match = MARKDOWN_FENCE_RE.match(line)
    if not match:
        return None
    if match.group(1)[0] == "`" and "`" in line[match.end() :]:
        return None
    return match


def markdown_visible_signal_text(
    line: str, defined_reference_labels: Optional[Set[str]] = None
) -> str:
    """Keep rendered link labels while removing non-rendered destinations."""
    links = markdown_inline_links(line)
    if links:
        pieces: List[str] = []
        cursor = 0
        for start, end, label, _ in links:
            pieces.extend(
                (
                    line[cursor:start],
                    markdown_visible_signal_text(
                        label, defined_reference_labels
                    ),
                )
            )
            cursor = end
        pieces.append(line[cursor:])
        visible = "".join(pieces)
    else:
        visible = line
    reference_links = markdown_reference_links(visible)
    if not reference_links:
        return visible
    pieces = []
    cursor = 0
    for start, end, label, reference_label, _ in reference_links:
        raw_label = reference_label or label
        is_defined = (
            defined_reference_labels is None
            or (
                markdown_reference_label_is_valid(raw_label)
                and normalize_reference_label(raw_label)
                in defined_reference_labels
            )
        )
        rendered = (
            markdown_visible_signal_text(label, defined_reference_labels)
            if is_defined
            else visible[start:end]
        )
        pieces.extend((visible[cursor:start], rendered))
        cursor = end
    pieces.append(visible[cursor:])
    return "".join(pieces)


def markdown_mask_inline_links(line: str) -> str:
    """Hide complete inline-link spans before scanning for reference uses."""
    links = markdown_inline_links(line)
    if not links:
        return line
    pieces: List[str] = []
    cursor = 0
    for start, end, label, _ in links:
        pieces.append(line[cursor:start])
        is_image = line[start : start + 1] == "!"
        nested_reference_labels = (
            set() if is_image else markdown_reference_use_labels(label)
        )
        pieces.append(
            label if nested_reference_labels else " " * (end - start)
        )
        cursor = end
    pieces.append(line[cursor:])
    return "".join(pieces)


def markdown_character_is_escaped(line: str, position: int) -> bool:
    backslashes = 0
    cursor = position - 1
    while cursor >= 0 and line[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def markdown_mask_escaped_html_openers(line: str) -> str:
    """Prevent escaped `<` characters from starting raw-HTML parsing."""
    characters = list(line)
    for position, character in enumerate(line):
        if character == "<" and markdown_character_is_escaped(line, position):
            characters[position] = " "
    return "".join(characters)


def markdown_reference_label_is_valid(raw: str) -> bool:
    if not normalize_reference_label(raw) or len(raw) > 999:
        return False
    return not any(
        character in "[]" and not markdown_character_is_escaped(raw, position)
        for position, character in enumerate(raw)
    )


def markdown_reference_use_labels(
    line: str,
    *,
    include_images: bool = True,
    include_links: bool = True,
) -> Set[str]:
    labels: Set[str] = set()
    visible = list(line)
    for start, end, label, reference_label, is_image in markdown_reference_links(
        line, include_escaped=True
    ):
        visible[start:end] = " " * (end - start)
        opening = start + 1 if is_image else start
        if markdown_character_is_escaped(line, opening):
            continue
        if not is_image:
            labels.update(
                markdown_reference_use_labels(
                    label, include_images=True, include_links=False
                )
            )
        if is_image and not include_images:
            continue
        if not is_image and not include_links:
            continue
        raw_label = reference_label or label
        if not markdown_reference_label_is_valid(raw_label):
            continue
        labels.add(normalize_reference_label(raw_label))
    without_explicit_references = "".join(visible)
    for match in MARKDOWN_REFERENCE_SHORTCUT_RE.finditer(
        without_explicit_references
    ):
        opening = match.start()
        if without_explicit_references[opening : opening + 1] == "!":
            opening += 1
            is_image = True
        else:
            is_image = False
        if markdown_character_is_escaped(without_explicit_references, opening):
            continue
        if is_image and not include_images:
            continue
        if not is_image and not include_links:
            continue
        raw_label = match.group(1)
        if markdown_reference_label_is_valid(raw_label):
            labels.add(normalize_reference_label(raw_label))
    return labels


def markdown_has_multiline_reference_label_start(line: str) -> bool:
    """Detect a full-reference label that continues past this physical line."""
    cursor = 0
    while cursor < len(line):
        opening = line.find("[", cursor)
        if opening < 0:
            return False
        if markdown_character_is_escaped(line, opening):
            cursor = opening + 1
            continue
        label_end = markdown_link_label_end(line, opening)
        if label_end is None:
            cursor = opening + 1
            continue
        reference_opening = label_end + 1
        if (
            reference_opening < len(line)
            and line[reference_opening] == "["
            and markdown_link_label_end(line, reference_opening) is None
        ):
            return True
        cursor = label_end + 1
    return False


def markdown_unclosed_reference_label_continues(
    lines: Sequence[str],
    start_index: int,
    line: str,
    container_tokens: Sequence[Tuple[str, int]],
) -> bool:
    """Detect an unfinished first/shortcut label closed later in its paragraph."""
    cursor = 0
    while cursor < len(line):
        opening = line.find("[", cursor)
        if opening < 0:
            return False
        if markdown_character_is_escaped(line, opening):
            cursor = opening + 1
            continue
        if markdown_link_label_end(line, opening) is not None:
            cursor = opening + 1
            continue
        combined = line[opening:]
        for future_index in range(start_index + 1, len(lines)):
            future_line = markdown_paragraph_continuation(
                lines[future_index], container_tokens
            )
            if (
                future_line is None
                or not future_line.strip()
                or markdown_line_interrupts_paragraph(future_line)
            ):
                break
            combined += "\n" + future_line.rstrip("\r\n")
            if len(combined) > MAX_MULTILINE_LINK_SCAN_CHARS:
                return True
            if markdown_link_label_end(combined, 0) is not None:
                return True
        cursor = opening + 1
    return False


def markdown_link_label_end(line: str, opening: int) -> Optional[int]:
    depth = 1
    cursor = opening + 1
    while cursor < len(line):
        character = line[cursor]
        if character == "\\":
            if (
                cursor + 1 < len(line)
                and line[cursor + 1] in string.punctuation
            ):
                cursor += 2
            else:
                cursor += 1
            continue
        if character == "<":
            html_end = markdown_inline_html_token_end(line, cursor)
            if html_end is not None:
                cursor = html_end
                continue
        if character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                return cursor
        cursor += 1
    return None


def markdown_inline_html_token_end(line: str, opening: int) -> Optional[int]:
    """Return the end of a complete same-line CommonMark raw-HTML token."""
    if line.startswith("<?", opening):
        terminator = line.find("?>", opening + 2)
        return terminator + 2 if terminator >= 0 else None
    if line.startswith("<![CDATA[", opening):
        terminator = line.find("]]>", opening + 9)
        return terminator + 3 if terminator >= 0 else None
    if re.match(r"<![A-Z]", line[opening:]):
        terminator = line.find(">", opening + 3)
        if terminator < 0:
            return None
        candidate = line[opening : terminator + 1]
        return (
            terminator + 1
            if MARKDOWN_COMPLETE_HTML_DECLARATION_RE.fullmatch(candidate)
            else None
        )

    cursor = opening + 1
    if cursor < len(line) and line[cursor] == "/":
        cursor += 1
    if cursor >= len(line) or not line[cursor].isalpha():
        return None
    cursor += 1
    while cursor < len(line) and (
        line[cursor].isalnum() or line[cursor] in "-"
    ):
        cursor += 1
    quote: Optional[str] = None
    while cursor < len(line):
        character = line[cursor]
        if quote is not None:
            if character == quote:
                quote = None
        elif character in "\"'":
            quote = character
        elif character == ">":
            candidate = line[opening : cursor + 1]
            if (
                MARKDOWN_COMPLETE_HTML_OPENING_TAG_RE.fullmatch(candidate)
                or MARKDOWN_COMPLETE_HTML_CLOSING_TAG_RE.fullmatch(candidate)
            ):
                return cursor + 1
            return None
        elif character in "\r\n<":
            return None
        cursor += 1
    return None


def markdown_has_incomplete_html_token(line: str) -> bool:
    """Detect a tag-like opener that cannot be parsed within this line."""
    cursor = 0
    while cursor < len(line):
        opening = line.find("<", cursor)
        if opening < 0:
            return False
        if markdown_character_is_escaped(line, opening):
            cursor = opening + 1
            continue
        name_start = opening + 1
        if name_start < len(line) and line[name_start] == "/":
            name_start += 1
        if name_start >= len(line) or not line[name_start].isalpha():
            cursor = opening + 1
            continue
        html_end = markdown_inline_html_token_end(line, opening)
        if html_end is None:
            return True
        cursor = html_end
    return False


def markdown_complete_html_tokens(line: str) -> List[str]:
    """Return only complete CommonMark raw-HTML tokens from one line."""
    tokens: List[str] = []
    cursor = 0
    while cursor < len(line):
        opening = line.find("<", cursor)
        if opening < 0:
            break
        if markdown_character_is_escaped(line, opening):
            cursor = opening + 1
            continue
        html_end = markdown_inline_html_token_end(line, opening)
        if html_end is None:
            cursor = opening + 1
            continue
        tokens.append(line[opening:html_end])
        cursor = html_end
    return tokens


def markdown_reference_links(
    line: str, *, include_escaped: bool = False
) -> List[Tuple[int, int, str, str, bool]]:
    """Parse full and collapsed reference links with balanced link text."""
    links: List[Tuple[int, int, str, str, bool]] = []
    cursor = 0
    while cursor < len(line):
        opening = line.find("[", cursor)
        if opening < 0:
            break
        if (
            markdown_character_is_escaped(line, opening)
            and not include_escaped
        ):
            cursor = opening + 1
            continue
        label_end = markdown_link_label_end(line, opening)
        if label_end is None:
            cursor = opening + 1
            continue
        reference_opening = label_end + 1
        if (
            reference_opening >= len(line)
            or line[reference_opening] != "["
        ):
            cursor = opening + 1
            continue
        reference_end = markdown_link_label_end(line, reference_opening)
        if reference_end is None:
            cursor = opening + 1
            continue
        label = line[opening + 1 : label_end]
        reference_label = line[reference_opening + 1 : reference_end]
        is_image = bool(
            opening > 0
            and line[opening - 1] == "!"
            and not markdown_character_is_escaped(line, opening - 1)
        )
        start = opening - 1 if is_image else opening
        links.append(
            (start, reference_end + 1, label, reference_label, is_image)
        )
        cursor = reference_end + 1
    return links


def markdown_reference_destination_target(
    line: str, start: int
) -> Optional[Tuple[Optional[str], Optional[str], int]]:
    """Parse one reference destination while honoring backslash escapes."""
    cursor = start
    while cursor < len(line) and line[cursor] in " \t":
        cursor += 1
    if cursor >= len(line):
        return None
    if line[cursor] == "<":
        destination_start = cursor + 1
        cursor += 1
        while cursor < len(line):
            if line[cursor] == "\\":
                cursor += 2
                continue
            if line[cursor] == ">":
                return line[destination_start:cursor], None, cursor + 1
            if line[cursor] in "\r\n<":
                return None
            cursor += 1
        return None
    destination_start = cursor
    while cursor < len(line) and line[cursor] not in " \t\r\n":
        if (
            line[cursor] == "\\"
            and cursor + 1 < len(line)
            and line[cursor + 1] in string.punctuation
        ):
            cursor += 2
        else:
            cursor += 1
    if destination_start == cursor:
        return None
    return None, line[destination_start:cursor], cursor


def markdown_reference_definition_target(
    line: str,
) -> Optional[MarkdownReferenceTargetMatch]:
    prefix = MARKDOWN_REFERENCE_DEFINITION_RE.match(line)
    if prefix is None:
        return None
    destination = markdown_reference_destination_target(line, prefix.end())
    if destination is None:
        return None
    angle_target, bare_target, end = destination
    return MarkdownReferenceTargetMatch(
        (prefix.group(1), angle_target, bare_target), end
    )


def markdown_reference_continuation_target(
    line: str,
) -> Optional[MarkdownReferenceTargetMatch]:
    prefix = MARKDOWN_REFERENCE_CONTINUATION_PREFIX_RE.match(line)
    if prefix is None:
        return None
    destination = markdown_reference_destination_target(line, prefix.end())
    if destination is None:
        return None
    angle_target, bare_target, end = destination
    return MarkdownReferenceTargetMatch((angle_target, bare_target), end)


def markdown_link_title_close(line: str, cursor: int) -> Optional[int]:
    while cursor < len(line) and line[cursor] in " \t\r\n":
        cursor += 1
    if cursor >= len(line):
        return None
    if line[cursor] == ")":
        return cursor
    opener = line[cursor]
    closer = ")" if opener == "(" else opener
    if opener not in "\"'(":
        return None
    cursor += 1
    while cursor < len(line):
        if line[cursor] == "\\":
            cursor += 2
            continue
        if line[cursor] == closer:
            cursor += 1
            while cursor < len(line) and line[cursor] in " \t\r\n":
                cursor += 1
            return cursor if cursor < len(line) and line[cursor] == ")" else None
        cursor += 1
    return None


def markdown_link_destination(
    line: str, opening: int
) -> Optional[Tuple[str, int]]:
    cursor = opening + 1
    while cursor < len(line) and line[cursor] in " \t\r\n":
        cursor += 1
    if cursor >= len(line):
        return None
    if line[cursor] == "<":
        destination_start = cursor + 1
        cursor += 1
        while cursor < len(line):
            if line[cursor] == "\\":
                cursor += 2
                continue
            if line[cursor] == ">":
                target = line[destination_start:cursor]
                closing = markdown_link_title_close(line, cursor + 1)
                return (target, closing + 1) if closing is not None else None
            if line[cursor] in "\r\n<":
                return None
            cursor += 1
        return None

    destination_start = cursor
    parenthesis_depth = 0
    while cursor < len(line):
        character = line[cursor]
        if character == "\\":
            if (
                cursor + 1 < len(line)
                and line[cursor + 1] in string.punctuation
            ):
                cursor += 2
            else:
                cursor += 1
            continue
        if character in "<>":
            return None
        if character == "(":
            parenthesis_depth += 1
        elif character == ")":
            if parenthesis_depth == 0:
                return line[destination_start:cursor], cursor + 1
            parenthesis_depth -= 1
        elif character in " \t\r\n" and parenthesis_depth == 0:
            target = line[destination_start:cursor]
            closing = markdown_link_title_close(line, cursor)
            return (target, closing + 1) if closing is not None else None
        elif parenthesis_depth > 32:
            return None
        cursor += 1
    return None


def markdown_inline_links(line: str) -> List[Tuple[int, int, str, str]]:
    """Parse same-line inline links with bounded balanced destinations."""
    links: List[Tuple[int, int, str, str]] = []
    cursor = 0
    while cursor < len(line):
        opening = line.find("[", cursor)
        if opening < 0:
            break
        if markdown_character_is_escaped(line, opening):
            cursor = opening + 1
            continue
        label_end = markdown_link_label_end(line, opening)
        if label_end is None:
            cursor = opening + 1
            continue
        if label_end + 1 >= len(line):
            break
        label = line[opening + 1 : label_end]
        is_image = bool(
            opening > 0
            and line[opening - 1] == "!"
            and not markdown_character_is_escaped(line, opening - 1)
        )
        nested_links = markdown_inline_links(label)
        if not is_image and any(
            label[start : start + 1] != "!" for start, _, _, _ in nested_links
        ):
            cursor = opening + 1
            continue
        if line[label_end + 1] != "(":
            cursor = label_end + 1
            continue
        parsed = markdown_link_destination(line, label_end + 1)
        if parsed is None:
            cursor = label_end + 1
            continue
        target, end = parsed
        start = opening - 1 if is_image else opening
        links.append((start, end, label, target))
        cursor = end
    return links


def markdown_nested_image_links(label: str) -> List[Tuple[str, str]]:
    """Return nested image labels and targets rendered inside a link label."""
    nested_images: List[Tuple[str, str]] = []
    for start, _, nested_label, raw_target in markdown_inline_links(label):
        if label[start : start + 1] != "!":
            continue
        nested_images.append((nested_label, raw_target))
    return nested_images


def markdown_multiline_inline_links(
    lines: Sequence[str], start_index: int, first_line: str
) -> Tuple[List[Tuple[int, int, str, str]], Dict[int, str], bool]:
    if "[" not in first_line:
        return [], {}, False
    first_content, container_tokens = markdown_container_details(first_line)
    if MARKDOWN_HEADING_RE.match(first_content):
        return [], {}, False
    initial_links = markdown_inline_links(first_content)
    uncovered_positions: Set[int] = set()
    marker_cursor = 0
    while True:
        marker = first_content.find("](", marker_cursor)
        if marker < 0:
            break
        if not any(start <= marker < end for start, end, _, _ in initial_links):
            uncovered_positions.add(marker)
        marker_cursor = marker + 2
    opening_cursor = 0
    while True:
        opening = first_content.find("[", opening_cursor)
        if opening < 0:
            break
        if (
            not markdown_character_is_escaped(first_content, opening)
            and not any(
                start <= opening < end for start, end, _, _ in initial_links
            )
            and markdown_link_label_end(first_content, opening) is None
        ):
            uncovered_positions.add(opening)
        opening_cursor = opening + 1
    if not uncovered_positions:
        return [], {}, False
    combined = first_content
    continuation_segments: List[Tuple[int, int, str]] = [
        (start_index, 0, first_content)
    ]
    for future_index in range(start_index + 1, len(lines)):
        future_line = markdown_paragraph_continuation(
            lines[future_index], container_tokens
        )
        if (
            future_line is None
            or not future_line.strip()
            or markdown_line_interrupts_paragraph(future_line)
        ):
            break
        segment_start = len(combined)
        combined += future_line
        continuation_segments.append((future_index, segment_start, future_line))
        if len(combined) > MAX_MULTILINE_LINK_SCAN_CHARS:
            return [], {}, True
        links = markdown_inline_links(combined)
        if any(
            start <= position < end
            for position in uncovered_positions
            for start, end, _, _ in links
        ):
            hidden_spans: List[Tuple[int, int]] = []
            for link_start, link_end, _, _ in links:
                label_start = (
                    link_start + 1
                    if combined[link_start : link_start + 1] == "!"
                    else link_start
                )
                label_end = markdown_link_label_end(combined, label_start)
                if label_end is not None:
                    hidden_spans.append((label_end + 1, link_end))
            line_overrides: Dict[int, str] = {}
            for line_index, segment_start, content in continuation_segments:
                segment_end = segment_start + len(content)
                visible_parts: List[str] = []
                cursor = segment_start
                for hidden_start, hidden_end in hidden_spans:
                    overlap_start = max(segment_start, hidden_start)
                    overlap_end = min(segment_end, hidden_end)
                    if overlap_start >= overlap_end:
                        continue
                    visible_parts.append(
                        content[cursor - segment_start : overlap_start - segment_start]
                    )
                    cursor = max(cursor, overlap_end)
                visible_parts.append(content[cursor - segment_start :])
                line_overrides[line_index] = "".join(visible_parts)
            return links, line_overrides, False
    return [], {}, False


def decode_markdown_escapes_and_entities(raw: str) -> str:
    decoded: List[str] = []
    cursor = 0
    while cursor < len(raw):
        character = raw[cursor]
        if (
            character == "\\"
            and cursor + 1 < len(raw)
            and raw[cursor + 1] in string.punctuation
        ):
            decoded.append(raw[cursor + 1])
            cursor += 2
            continue
        if character == "&":
            entity = MARKDOWN_CHARACTER_REFERENCE_RE.match(raw, cursor)
            if entity:
                token = entity.group(0)
                replacement = html_unescape(token)
                if replacement != token:
                    decoded.append(replacement)
                    cursor = entity.end()
                    continue
        decoded.append(character)
        cursor += 1
    return "".join(decoded)


def normalize_reference_label(raw: str) -> str:
    return " ".join(decode_markdown_escapes_and_entities(raw).split()).casefold()


def markdown_bare_destination_is_valid(raw: str) -> bool:
    if not raw:
        return False
    depth = 0
    cursor = 0
    while cursor < len(raw):
        character = raw[cursor]
        if character == "\\":
            if cursor + 1 >= len(raw):
                return False
            cursor += 2
            continue
        if character in "<>" or ord(character) < 0x20:
            return False
        if character == "(":
            depth += 1
            if depth > 32:
                return False
        elif character == ")":
            if depth == 0:
                return False
            depth -= 1
        cursor += 1
    return depth == 0


def markdown_indentation_columns(line: str) -> int:
    columns = 0
    for character in line:
        if character == " ":
            columns += 1
        elif character == "\t":
            columns += 4 - (columns % 4)
        else:
            break
    return columns


def markdown_text_columns(text: str) -> int:
    columns = 0
    for character in text:
        if character == "\t":
            columns += 4 - (columns % 4)
        else:
            columns += 1
    return columns


def markdown_list_item_prefix(line: str) -> Optional[Tuple[int, int]]:
    match = MARKDOWN_LIST_ITEM_RE.match(line)
    if not match:
        return None
    padding = match.group("padding")
    marker_prefix = line[: match.start("padding")]
    marker_columns = markdown_text_columns(marker_prefix)
    padding_columns = markdown_text_columns(marker_prefix + padding) - marker_columns
    consumed_padding = padding if padding_columns <= 4 else padding[:1]
    end = match.start("padding") + len(consumed_padding)
    return end, markdown_text_columns(line[:end])


def strip_indentation_columns(line: str, required_columns: int) -> Optional[str]:
    columns = 0
    cursor = 0
    while cursor < len(line) and columns < required_columns:
        character = line[cursor]
        if character == " ":
            columns += 1
        elif character == "\t":
            columns += 4 - (columns % 4)
        else:
            return None
        cursor += 1
    if columns < required_columns:
        return None
    return " " * (columns - required_columns) + line[cursor:]


def markdown_one_block_quote_content(line: str) -> Optional[str]:
    cursor = 0
    spaces = 0
    while cursor < len(line) and line[cursor] == " " and spaces < 3:
        cursor += 1
        spaces += 1
    if cursor >= len(line) or line[cursor] != ">":
        return None
    cursor += 1
    if cursor < len(line) and line[cursor] in " \t":
        cursor += 1
    return line[cursor:]


def markdown_container_details(
    line: str,
) -> Tuple[str, Tuple[Tuple[str, int], ...]]:
    content = line
    tokens: List[Tuple[str, int]] = []
    for _ in range(32):
        quoted_content = markdown_one_block_quote_content(content)
        if quoted_content is not None:
            content = quoted_content
            tokens.append(("quote", 0))
            continue
        list_item = markdown_list_item_prefix(content)
        if list_item is not None:
            end, content_indent = list_item
            content = content[end:]
            tokens.append(("list", content_indent))
            continue
        break
    return content, tuple(tokens)


def markdown_container_continuation(
    line: str, tokens: Sequence[Tuple[str, int]]
) -> Optional[str]:
    content = line
    for kind, width in tokens:
        if kind == "quote":
            quoted_content = markdown_one_block_quote_content(content)
            if quoted_content is None:
                return None
            content = quoted_content
        else:
            if not content.strip():
                content = ""
                continue
            continuation = strip_indentation_columns(content, width)
            if continuation is None:
                return None
            content = continuation
    return content


def markdown_paragraph_continuation(
    line: str, tokens: Sequence[Tuple[str, int]]
) -> Optional[str]:
    content = markdown_container_continuation(line, tokens)
    if content is None:
        current_content, current_tokens = markdown_container_details(line)
        lazy_container_continuation = (
            any(kind in {"list", "quote"} for kind, _ in tokens)
            and not current_tokens
            and bool(current_content.strip())
            and MARKDOWN_HEADING_RE.match(current_content) is None
            and markdown_fence_opens(current_content) is None
            and MARKDOWN_SETEXT_RE.match(current_content) is None
            and MARKDOWN_THEMATIC_BREAK_RE.match(current_content) is None
            and markdown_html_block_start(
                current_content, allow_type_7=False
            ) is None
            and MARKDOWN_REFERENCE_DEFINITION_RE.match(current_content) is None
            and markdown_indentation_columns(current_content) < 4
        )
        return current_content if lazy_container_continuation else None
    if markdown_line_interrupts_paragraph(content):
        return None
    if (
        any(kind == "list" for kind, _ in tokens)
        and markdown_indentation_columns(content) >= 4
    ):
        return None
    return content


def markdown_list_interrupts_paragraph(line: str) -> bool:
    list_match = MARKDOWN_LIST_ITEM_RE.match(line)
    if not list_match:
        return False
    marker = list_match.group("marker")
    list_item = markdown_list_item_prefix(line)
    item_content = line[list_item[0] :] if list_item is not None else ""
    ordered_starts_at_one = not marker[0].isdigit() or int(marker[:-1]) == 1
    return ordered_starts_at_one and bool(item_content.strip())


def markdown_line_interrupts_paragraph(line: str) -> bool:
    return bool(
        MARKDOWN_HEADING_RE.match(line)
        or markdown_fence_opens(line)
        or MARKDOWN_SETEXT_RE.match(line)
        or MARKDOWN_THEMATIC_BREAK_RE.match(line)
        or markdown_html_block_start(line, allow_type_7=False) is not None
        or MARKDOWN_HTML_COMMENT_BLOCK_START_RE.match(line)
        or markdown_one_block_quote_content(line) is not None
        or markdown_list_interrupts_paragraph(line)
    )


def markdown_reference_title_state(raw: str) -> str:
    candidate = raw.strip()
    if not candidate or candidate[0] not in "\"'(":
        return "invalid"
    closer = ")" if candidate[0] == "(" else candidate[0]
    cursor = 1
    while cursor < len(candidate):
        if candidate[cursor] == "\\":
            cursor += 2
            continue
        if candidate[cursor] == closer:
            return "complete" if not candidate[cursor + 1 :].strip() else "invalid"
        cursor += 1
    return "open"


def markdown_multiline_reference_title_lines(
    lines: Sequence[str],
    start_index: int,
    first_fragment: str,
    container_tokens: Sequence[Tuple[str, int]],
) -> Tuple[Optional[Set[int]], bool]:
    if markdown_reference_title_state(first_fragment) != "open":
        return None, False
    combined = first_fragment.strip()
    consumed_lines: Set[int] = set()
    for future_index in range(start_index + 1, len(lines)):
        future_line = markdown_container_continuation(
            lines[future_index], container_tokens
        )
        if future_line is None or not future_line.strip():
            break
        _, nested_tokens = markdown_container_details(future_line)
        if nested_tokens or markdown_line_interrupts_paragraph(future_line):
            break
        combined += "\n" + future_line.rstrip("\r\n")
        consumed_lines.add(future_index)
        if len(combined) > 4096:
            return None, True
        state = markdown_reference_title_state(combined)
        if state == "complete":
            return consumed_lines, False
        if state == "invalid":
            break
    return None, False


def matching_backtick_run_end(
    line: str, start: int, run_length: int
) -> Optional[int]:
    search = start
    while search < len(line):
        close = line.find("`", search)
        if close < 0:
            return None
        close_end = close
        while close_end < len(line) and line[close_end] == "`":
            close_end += 1
        if close_end - close == run_length:
            return close_end
        search = close_end
    return None


def future_paragraph_has_backtick_run(
    lines: Sequence[str],
    start_index: int,
    run_length: int,
    container_tokens: Sequence[Tuple[str, int]],
) -> bool:
    for line_index in range(start_index, len(lines)):
        future_line = markdown_paragraph_continuation(
            lines[line_index], container_tokens
        )
        if (
            future_line is None
            or not future_line.strip()
            or MARKDOWN_HEADING_RE.match(future_line)
            or markdown_fence_opens(future_line)
            or MARKDOWN_SETEXT_RE.match(future_line)
            or MARKDOWN_THEMATIC_BREAK_RE.match(future_line)
            or markdown_html_block_start(
                future_line, allow_type_7=False
            ) is not None
            or MARKDOWN_HTML_COMMENT_BLOCK_START_RE.match(future_line)
            or markdown_line_interrupts_paragraph(future_line)
            or markdown_indentation_columns(future_line) >= 4
        ):
            return False
        if matching_backtick_run_end(future_line, 0, run_length) is not None:
            return True
    return False


def markdown_html_block_start(
    line: str, *, allow_type_7: bool = True
) -> Optional[Tuple[Optional[str], bool]]:
    """Return an end token or blank-line mode for a CommonMark HTML block."""
    raw_tag = MARKDOWN_RAW_HTML_TAG_RE.match(line)
    if raw_tag:
        return f"</{raw_tag.group('tag').lower()}>", False
    candidate = (
        line.lstrip(" ")
        if len(line) - len(line.lstrip(" ")) <= 3
        else line
    )
    lowered = candidate.lower()
    if lowered.startswith("<?"):
        return "?>", False
    if candidate.startswith("<![CDATA["):
        return "]]>", False
    if re.match(r"<![A-Z]", candidate):
        return ">", False
    if MARKDOWN_HTML_BLOCK_TAG_RE.match(line):
        return None, True
    if allow_type_7 and (
        MARKDOWN_COMPLETE_HTML_OPENING_TAG_RE.match(line.rstrip("\r\n"))
        or MARKDOWN_COMPLETE_HTML_CLOSING_TAG_RE.match(line.rstrip("\r\n"))
    ):
        return None, True
    return None


def markdown_inline_comment_is_valid(
    line: str,
    comment_start: int,
    lines: Sequence[str],
    current_line_index: int,
) -> bool:
    """Validate one complete CommonMark inline HTML comment before masking it."""
    fragments = [line[comment_start + 4 :]]
    scanned = len(fragments[0])
    for future_index in range(current_line_index + 1, len(lines)):
        if "-->" in fragments[-1]:
            break
        fragment = lines[future_index]
        scanned += len(fragment)
        if scanned > MAX_MULTILINE_LINK_SCAN_CHARS:
            return False
        fragments.append(fragment)
    remainder = "".join(fragments)
    closing = remainder.find("-->")
    if closing < 0:
        return False
    content = remainder[:closing]
    return bool(
        not content.startswith((">", "->"))
        and "--" not in content
        and not content.endswith("-")
    )


def sanitize_markdown_inline(
    line: str,
    in_comment: bool,
    code_span_length: int,
    lines: Sequence[str],
    next_line_index: int,
) -> Tuple[str, bool, int]:
    """Mask code spans and remove comments in their lexical order."""
    result: List[str] = []
    cursor = 0
    length = len(line)

    def escaped(position: int) -> bool:
        backslashes = 0
        index = position - 1
        while index >= 0 and line[index] == "\\":
            backslashes += 1
            index -= 1
        return backslashes % 2 == 1

    while cursor < length:
        if code_span_length:
            closing_end = matching_backtick_run_end(
                line, cursor, code_span_length
            )
            if closing_end is None:
                result.append(" " * (length - cursor))
                return "".join(result), in_comment, code_span_length
            result.append(" " * (closing_end - cursor))
            cursor = closing_end
            code_span_length = 0
            continue
        if in_comment:
            comment_end = line.find("-->", cursor)
            if comment_end < 0:
                return "".join(result), True, code_span_length
            cursor = comment_end + 3
            in_comment = False
            continue

        comment_start = line.find("<!--", cursor)
        while comment_start >= 0 and (
            escaped(comment_start)
            or not markdown_inline_comment_is_valid(
                line,
                comment_start,
                lines,
                next_line_index - 1,
            )
        ):
            comment_start = line.find("<!--", comment_start + 1)
        code_start = line.find("`", cursor)
        while code_start >= 0 and escaped(code_start):
            code_start = line.find("`", code_start + 1)

        if comment_start < 0 and code_start < 0:
            result.append(line[cursor:])
            break
        if comment_start >= 0 and (code_start < 0 or comment_start < code_start):
            result.append(line[cursor:comment_start])
            cursor = comment_start + 4
            in_comment = True
            continue

        start = code_start
        opening_end = start
        while opening_end < length and line[opening_end] == "`":
            opening_end += 1
        run_length = opening_end - start
        closing_end = matching_backtick_run_end(line, opening_end, run_length)
        if closing_end is None:
            if future_paragraph_has_backtick_run(
                lines,
                next_line_index,
                run_length,
                markdown_container_details(line)[1],
            ):
                result.append(line[cursor:start])
                result.append(" " * (length - start))
                return "".join(result), in_comment, run_length
            result.append(line[cursor:opening_end])
            cursor = opening_end
            continue
        result.append(line[cursor:start])
        result.append(" " * (closing_end - start))
        cursor = closing_end
    return "".join(result), in_comment, code_span_length


def resolve_inside(root: Path, raw: str, label: str, require_exists: bool) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    lexical = Path(os.path.abspath(str(candidate)))
    try:
        lexical_relative = lexical.relative_to(root)
    except ValueError:
        fail(f"{label} is outside --root: {raw}")
    cursor = root
    for part in lexical_relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            fail(f"{label} crosses a symlink boundary: {raw}")
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError:
        fail(f"{label} is outside --root: {raw}")
    if require_exists and not candidate.exists():
        fail(f"{label} does not exist: {raw}")
    return candidate


def contains(path: Path, roots: Sequence[Path]) -> bool:
    for root in roots:
        if path == root or root in path.parents:
            return True
    return False


def secret_like(path: Path) -> bool:
    name = path.name.lower()
    if name == ".env" or name.startswith(".env."):
        return True
    if name in {"id_rsa", "id_ed25519", "credentials.json", "secrets.json"}:
        return True
    if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
        return True
    return bool(re.fullmatch(r"(?:secret|secrets|credentials)\.(?:json|ya?ml|toml)", name))


def looks_binary(path: Path) -> bool:
    if path.stat().st_size == 0:
        return False
    with path.open("rb") as handle:
        sample = handle.read(8192)
    return b"\x00" in sample


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_scope_files(
    scope: Path,
    excluded_dirs: Set[str],
    skipped: Optional[Counter] = None,
    symlink_skip_key: str = "symlink",
    excluded_dir_skip_key: str = "excluded_dir",
    traversal_error_skip_key: str = "traversal_error",
) -> Iterable[Path]:
    if scope.is_symlink():
        if skipped is not None:
            skipped[symlink_skip_key] += 1
        return
    if scope.is_file():
        yield scope
        return
    def record_traversal_error(_: OSError) -> None:
        if skipped is not None:
            skipped[traversal_error_skip_key] += 1

    for directory, dirnames, filenames in os.walk(
        scope, followlinks=False, onerror=record_traversal_error
    ):
        current = Path(directory)
        retained_dirnames: List[str] = []
        for name in sorted(dirnames):
            child = current / name
            if name in excluded_dirs:
                if skipped is not None:
                    skipped[excluded_dir_skip_key] += 1
                continue
            if child.is_symlink():
                if skipped is not None:
                    skipped[symlink_skip_key] += 1
                continue
            retained_dirnames.append(name)
        dirnames[:] = retained_dirnames
        for filename in sorted(filenames):
            path = current / filename
            if path.is_symlink():
                if skipped is not None:
                    skipped[symlink_skip_key] += 1
                continue
            if path.is_file():
                yield path


def location_state(
    path: Path,
    active_roots: Sequence[Path],
    canonical_roots: Sequence[Path],
    protected_roots: Sequence[Path],
    historical_roots: Sequence[Path],
    archive_roots: Sequence[Path],
) -> str:
    # Canonical and active are the primary lifecycle roles. Safety remains
    # independently visible through AuditFile.protected, so an overlapping
    # protected root must not hide lifecycle-specific diagnostic signals.
    if contains(path, canonical_roots):
        return "canonical"
    if contains(path, active_roots):
        return "active"
    if contains(path, protected_roots):
        return "protected"
    if contains(path, archive_roots):
        return "archive"
    if contains(path, historical_roots):
        return "historical"
    return "unclassified"


def run_git(root: Path, args: Sequence[str]) -> Optional[bytes]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def git_inventory(root: Path) -> Tuple[bool, Set[str], Dict[str, str]]:
    inside = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if inside is None or inside.strip() != b"true":
        return False, set(), {}

    tracked_raw = run_git(root, ["ls-files", "-z"])
    status_raw = run_git(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    if tracked_raw is None or status_raw is None:
        return False, set(), {}

    tracked = {
        entry.decode("utf-8", errors="surrogateescape")
        for entry in tracked_raw.split(b"\0")
        if entry
    }
    status: Dict[str, str] = {}
    entries = status_raw.split(b"\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        decoded = entry.decode("utf-8", errors="surrogateescape")
        if len(decoded) < 4:
            continue
        code = decoded[:2]
        path = decoded[3:]
        status[path] = "untracked" if code == "??" else f"modified:{code}"
        if "R" in code or "C" in code:
            if index < len(entries) and entries[index]:
                original = entries[index].decode("utf-8", errors="surrogateescape")
                status[original] = f"modified:{code}"
                index += 1
    return True, tracked, status


def normalize_link_target(
    root: Path,
    source: Path,
    raw_target: str,
    *,
    decode_markdown: bool = True,
) -> Optional[Path]:
    target = raw_target.strip()
    if decode_markdown:
        target = decode_markdown_escapes_and_entities(target)
    target = unquote(target.split("#", 1)[0].split("?", 1)[0].strip())
    if (
        not target
        or target.startswith(("#", "//"))
        or URI_SCHEME_RE.match(target)
    ):
        return None
    if any(token in target for token in ("{", "}", "$")):
        return None
    candidate = root / target.lstrip("/") if target.startswith("/") else source.parent / target
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def inspect_text(
    item: AuditFile,
    root: Path,
    task_id_pattern: Optional[re.Pattern],
) -> Set[Path]:
    links: Set[Path] = set()
    task_ids: Set[str] = set()
    line_count = 0
    nonblank = 0
    open_sections: List[Tuple[int, int]] = []
    markdown = item.absolute_path.suffix.lower() in {".md", ".markdown", ".mdx"}
    html_targets: Set[Tuple[str, Optional[str]]] = set()
    html_base_href: Optional[str] = None
    html_base_seen = False
    html_template_depth = 0
    html_element_stack: List[Tuple[str, str]] = []
    html_template_raw_text_tag: Optional[str] = None
    front_matter_end = (
        markdown_front_matter_end(item.absolute_path) if markdown else None
    )
    # Front matter is intentionally excluded from rendered-content signals, but
    # it can still contain native repository paths (for example `related:`).
    # Until those metadata formats are parsed explicitly, never claim complete
    # incoming-link coverage for a Markdown source that contains front matter.
    if front_matter_end is not None:
        item.link_parse_incomplete = True
    root_block_start: Optional[int] = (
        front_matter_end + 1
        if front_matter_end is not None
        else (1 if markdown else None)
    )
    fence_character: Optional[str] = None
    fence_length = 0
    fence_container_tokens: Tuple[Tuple[str, int], ...] = ()
    html_block_end_token: Optional[str] = None
    html_block_until_blank = False
    html_block_container_tokens: Tuple[Tuple[str, int], ...] = ()
    html_block_comment_open = False
    html_comment_open = False
    html_comment_block_open = False
    html_comment_container_tokens: Tuple[Tuple[str, int], ...] = ()
    inline_code_span_length = 0
    previous_setext_candidate: Optional[
        Tuple[int, str, Set[str], Tuple[Tuple[str, int], ...]]
    ] = None
    paragraph_active = False
    paragraph_container_tokens: Tuple[Tuple[str, int], ...] = ()
    loose_container_tokens: Tuple[Tuple[str, int], ...] = ()
    reference_definitions: Dict[str, str] = {}
    used_reference_labels: Set[str] = set()
    inline_link_candidates: List[Tuple[str, Set[str]]] = []
    signal_lines: List[Tuple[int, str]] = []
    html_only_fragments: List[Tuple[int, str]] = []
    heading_signal_lines: List[str] = []
    pending_reference_label: Optional[str] = None
    pending_reference_container_tokens: Tuple[Tuple[str, int], ...] = ()
    pending_reference_title_container_tokens: Optional[
        Tuple[Tuple[str, int], ...]
    ] = None

    def register_html_fragment(fragment: str) -> None:
        nonlocal html_base_href, html_base_seen, html_template_depth
        nonlocal html_element_stack, html_template_raw_text_tag
        if html_element_stack:
            raw_text_tag, raw_text_namespace = html_element_stack[-1]
            if (
                raw_text_namespace == "html"
                and raw_text_tag in HTML_RAW_TEXT_ELEMENTS
            ):
                suffix = html_raw_text_closing_suffix(
                    fragment, raw_text_tag
                )
                if suffix is None:
                    if html_raw_text_has_non_commonmark_closer(
                        fragment, raw_text_tag
                    ):
                        # A browser can finish this raw-text closing tag in a
                        # later Markdown fragment. Without buffering the HTML
                        # token, do not certify repository-reference coverage.
                        item.link_parse_incomplete = True
                    return
                fragment = suffix
        parser = MarkdownHtmlTargetParser(
            html_base_href,
            html_base_seen,
            html_template_depth,
            html_element_stack,
            html_template_raw_text_tag,
        )
        parser.feed("".join(markdown_complete_html_tokens(fragment)))
        parser.close()
        html_targets.update(parser.targets)
        html_base_href = parser.base_href
        html_base_seen = parser.base_seen
        html_template_depth = parser.template_depth
        html_element_stack = parser.element_stack
        html_template_raw_text_tag = parser.template_raw_text_tag
        if parser.resource_parse_incomplete:
            item.link_parse_incomplete = True
        if markdown_has_incomplete_html_token(fragment):
            item.link_parse_incomplete = True

    def queue_rendered_suffix(fragment: str, line_number: int) -> None:
        sanitized, comment_open, code_span_open = sanitize_markdown_inline(
            fragment,
            False,
            0,
            [fragment],
            1,
        )
        if comment_open or code_span_open:
            item.link_parse_incomplete = True
        if sanitized.strip():
            signal_lines.append((line_number, sanitized))

    def register_heading(
        heading_level: int,
        heading_start: int,
        heading_signal_text: str,
    ) -> None:
        nonlocal root_block_start
        while open_sections and open_sections[-1][0] >= heading_level:
            _, section_start = open_sections.pop()
            item.max_section_lines = max(
                item.max_section_lines, heading_start - section_start
            )
        # Treat content before H2+ and after every H1 as bounded root blocks.
        # H2+ sections include nested descendants without degenerating the
        # metric into the whole document length.
        if heading_level == 1:
            if root_block_start is not None:
                item.max_section_lines = max(
                    item.max_section_lines, heading_start - root_block_start
                )
            root_block_start = heading_start
        else:
            if root_block_start is not None:
                item.max_section_lines = max(
                    item.max_section_lines, heading_start - root_block_start
                )
                root_block_start = None
            open_sections.append((heading_level, heading_start))
        item.markdown_heading_count += 1
        heading_signal_lines.append(heading_signal_text)

    with item.absolute_path.open("r", encoding="utf-8") as handle:
        lines = handle.readlines()
        multiline_link_line_overrides: Dict[int, str] = {}
        multiline_reference_title_hidden_lines: Set[int] = set()
        for line_index, line in enumerate(lines):
            previous_pending_reference_label = pending_reference_label
            previous_pending_reference_container_tokens = (
                pending_reference_container_tokens
            )
            previous_pending_reference_title_container_tokens = (
                pending_reference_title_container_tokens
            )
            pending_reference_label = None
            pending_reference_container_tokens = ()
            pending_reference_title_container_tokens = None
            line_count += 1
            if line.strip():
                nonblank += 1
            if markdown and line_index in multiline_reference_title_hidden_lines:
                continue
            if markdown and line_index in multiline_link_line_overrides:
                line = multiline_link_line_overrides[line_index]
                if not line.strip():
                    continue
                # A visible suffix after a multiline link remains part of the
                # opening paragraph even when it starts with block-like text.
                line = "x" + line
            if markdown:
                inline_sanitized = False
                container_line, container_tokens = markdown_container_details(line)
                active_loose_container_tokens: Tuple[Tuple[str, int], ...] = ()
                if line.strip() and loose_container_tokens:
                    loose_content = markdown_container_continuation(
                        line, loose_container_tokens
                    )
                    if loose_content is not None:
                        nested_content, nested_tokens = markdown_container_details(
                            loose_content
                        )
                        active_loose_container_tokens = loose_container_tokens
                        container_line = nested_content
                        container_tokens = loose_container_tokens + nested_tokens
                    loose_container_tokens = ()
                paragraph_continuation_line = (
                    markdown_paragraph_continuation(
                        line, paragraph_container_tokens
                    )
                    if paragraph_active
                    else None
                )
                if (
                    html_comment_open
                    and not html_comment_block_open
                    and paragraph_continuation_line is None
                ):
                    html_comment_open = False
                if front_matter_end is not None and line_count <= front_matter_end:
                    paragraph_active = False
                    previous_setext_candidate = None
                    continue
                if fence_character is not None:
                    fence_line = markdown_container_continuation(
                        line, fence_container_tokens
                    )
                    if fence_line is None:
                        fence_character = None
                        fence_length = 0
                        fence_container_tokens = ()
                    elif markdown_fence_closes(
                        fence_line, fence_character, fence_length
                    ):
                        fence_character = None
                        fence_length = 0
                        fence_container_tokens = ()
                        paragraph_active = False
                        previous_setext_candidate = None
                        continue
                    else:
                        paragraph_active = False
                        previous_setext_candidate = None
                        continue
                if html_block_end_token is not None or html_block_until_blank:
                    html_container_line = markdown_container_continuation(
                        line, html_block_container_tokens
                    )
                    if html_container_line is None:
                        html_block_end_token = None
                        html_block_until_blank = False
                        html_block_container_tokens = ()
                        html_block_comment_open = False
                    elif html_block_end_token is not None:
                        lowered_html_line = html_container_line.lower()
                        raw_text_tag = (
                            html_block_end_token[2:-1]
                            if html_block_end_token.startswith("</")
                            else None
                        )
                        if (
                            raw_text_tag in {"script", "style", "textarea"}
                            and html_raw_text_has_non_commonmark_closer(
                                html_container_line, raw_text_tag
                            )
                        ):
                            # CommonMark keeps the type-1 raw block open until
                            # an exact end token, while a browser can close the
                            # raw-text element on an attributed or whitespace-
                            # separated end tag. Do not certify link coverage
                            # when those two parsers diverge.
                            item.link_parse_incomplete = True
                        closing_position = lowered_html_line.find(
                            html_block_end_token
                        )
                        if closing_position >= 0:
                            suffix_start = closing_position + len(
                                html_block_end_token
                            )
                            html_only_fragments.append(
                                (
                                    line_count,
                                    html_container_line[
                                        closing_position:suffix_start
                                    ],
                                )
                            )
                            rendered_suffix = html_container_line[suffix_start:]
                            queue_rendered_suffix(rendered_suffix, line_count)
                            html_block_end_token = None
                            html_block_container_tokens = ()
                        paragraph_active = False
                        previous_setext_candidate = None
                        continue
                    else:
                        sanitized_html_line, html_block_comment_open = (
                            strip_html_comments(
                                html_container_line, html_block_comment_open
                            )
                        )
                        if sanitized_html_line.strip():
                            signal_lines.append((line_count, sanitized_html_line))
                        if not html_container_line.strip():
                            html_block_until_blank = False
                            html_block_container_tokens = ()
                            html_block_comment_open = False
                        paragraph_active = False
                        previous_setext_candidate = None
                        continue
                if html_comment_open and html_comment_block_open:
                    comment_container_line = markdown_container_continuation(
                        line, html_comment_container_tokens
                    )
                    if comment_container_line is None:
                        html_comment_open = False
                        html_comment_block_open = False
                        html_comment_container_tokens = ()
                if html_comment_open:
                    comment_was_block = html_comment_block_open
                    line, html_comment_open, inline_code_span_length = (
                        sanitize_markdown_inline(
                            line,
                            html_comment_open,
                            inline_code_span_length,
                            lines,
                            line_index + 1,
                        )
                    )
                    inline_sanitized = True
                    if comment_was_block:
                        html_comment_block_open = html_comment_open
                        if not html_comment_open:
                            html_comment_container_tokens = ()
                        paragraph_active = False
                        previous_setext_candidate = None
                        continue
                    if not line.strip():
                        html_comment_open = False
                        previous_setext_candidate = None
                        continue
                html_block_start = markdown_html_block_start(
                    container_line,
                    allow_type_7=paragraph_continuation_line is None,
                )
                if html_block_start is not None:
                    end_token, until_blank = html_block_start
                    if end_token is not None:
                        raw_text_tag = end_token[2:-1] if end_token.startswith("</") else None
                        if raw_text_tag in {"pre", "script", "style", "textarea"}:
                            if (
                                raw_text_tag != "pre"
                                and html_raw_text_has_non_commonmark_closer(
                                    container_line, raw_text_tag
                                )
                            ):
                                item.link_parse_incomplete = True
                            tokens = markdown_complete_html_tokens(container_line)
                            closing_position = container_line.lower().find(end_token)
                            if tokens:
                                html_fragment = tokens[0]
                                if closing_position >= 0:
                                    html_fragment = (
                                        tokens[0] + end_token
                                        if raw_text_tag == "pre"
                                        else container_line[
                                            : closing_position + len(end_token)
                                        ]
                                    )
                                html_only_fragments.append(
                                    (line_count, html_fragment)
                                )
                            if closing_position >= 0:
                                suffix_start = closing_position + len(end_token)
                                rendered_suffix = container_line[suffix_start:]
                                queue_rendered_suffix(
                                    rendered_suffix, line_count
                                )
                    elif until_blank:
                        sanitized_html_line, html_block_comment_open = (
                            strip_html_comments(container_line)
                        )
                        if sanitized_html_line.strip():
                            signal_lines.append((line_count, sanitized_html_line))
                    if (
                        end_token is not None
                        and end_token not in container_line.lower()
                    ):
                        html_block_end_token = end_token
                    html_block_until_blank = until_blank
                    if html_block_end_token is not None or html_block_until_blank:
                        html_block_container_tokens = container_tokens
                    inline_code_span_length = 0
                    paragraph_active = False
                    previous_setext_candidate = None
                    continue
                if not inline_sanitized:
                    comment_block_starts = bool(
                        MARKDOWN_HTML_COMMENT_BLOCK_START_RE.match(
                            container_line
                        )
                    )
                    line, html_comment_open, inline_code_span_length = (
                        sanitize_markdown_inline(
                            line,
                            html_comment_open,
                            inline_code_span_length,
                            lines,
                            line_index + 1,
                        )
                    )
                    if comment_block_starts:
                        html_comment_block_open = html_comment_open
                        html_comment_container_tokens = (
                            container_tokens if html_comment_open else ()
                        )
                        paragraph_active = False
                        previous_setext_candidate = None
                        continue
                if not line.strip():
                    blank_container_tokens = (
                        paragraph_container_tokens
                        if paragraph_active
                        else loose_container_tokens
                    )
                    if (
                        any(kind == "list" for kind, _ in blank_container_tokens)
                        and markdown_container_continuation(
                            line, blank_container_tokens
                        )
                        is not None
                    ):
                        loose_container_tokens = blank_container_tokens
                    else:
                        loose_container_tokens = ()
                    paragraph_active = False
                    previous_setext_candidate = None
                    continue
                paragraph_continuation_line = (
                    markdown_paragraph_continuation(
                        line, paragraph_container_tokens
                    )
                    if paragraph_active
                    else None
                )
                if active_loose_container_tokens:
                    loose_content = markdown_container_continuation(
                        line, active_loose_container_tokens
                    )
                    if loose_content is not None:
                        nested_content, nested_tokens = markdown_container_details(
                            loose_content
                        )
                        container_line = nested_content
                        container_tokens = (
                            active_loose_container_tokens + nested_tokens
                        )
                    else:
                        container_line, container_tokens = markdown_container_details(
                            line
                        )
                else:
                    container_line, container_tokens = markdown_container_details(line)
                fence_line = container_line
                fence_match = markdown_fence_opens(fence_line)
                if fence_match:
                    fence_character = fence_match.group(1)[0]
                    fence_length = len(fence_match.group(1))
                    fence_container_tokens = container_tokens
                    paragraph_active = False
                    previous_setext_candidate = None
                    continue
                if (
                    paragraph_continuation_line is None
                    and markdown_indentation_columns(container_line) >= 4
                ):
                    paragraph_active = False
                    previous_setext_candidate = None
                    continue

            semantic_line = line
            inline_links = markdown_inline_links(line)
            if markdown:
                (
                    multiline_links,
                    line_overrides,
                    multiline_scan_incomplete,
                ) = markdown_multiline_inline_links(lines, line_index, line)
                if multiline_scan_incomplete:
                    item.link_parse_incomplete = True
                if multiline_links:
                    inline_links = multiline_links
                    semantic_line = line_overrides.get(line_index, line)
                    multiline_link_line_overrides.update(
                        {
                            index: override
                            for index, override in line_overrides.items()
                            if index != line_index
                        }
                    )

            reference_line = container_line if markdown else line
            definition_prefix_match = (
                MARKDOWN_REFERENCE_DEFINITION_RE.match(reference_line)
                if markdown and paragraph_continuation_line is None
                else None
            )
            if definition_prefix_match and not markdown_reference_label_is_valid(
                definition_prefix_match.group(1)
            ):
                definition_prefix_match = None
            definition_match = (
                markdown_reference_definition_target(reference_line)
                if markdown and paragraph_continuation_line is None
                else None
            )
            if (
                definition_match
                and (
                    not markdown_reference_label_is_valid(
                        definition_match.group(1)
                    )
                    or (
                        definition_match.group(3)
                        and not markdown_bare_destination_is_valid(
                            definition_match.group(3)
                        )
                    )
                )
            ):
                definition_match = None
            if definition_match and (
                definition_suffix := reference_line[definition_match.end() :].strip()
            ):
                definition_title_state = markdown_reference_title_state(
                    definition_suffix
                )
                if definition_title_state == "open":
                    (
                        consumed_title_lines,
                        title_scan_incomplete,
                    ) = markdown_multiline_reference_title_lines(
                        lines, line_index, definition_suffix, container_tokens
                    )
                    if title_scan_incomplete:
                        item.link_parse_incomplete = True
                    if consumed_title_lines is not None:
                        multiline_reference_title_hidden_lines.update(
                            consumed_title_lines
                        )
                    else:
                        definition_match = None
                elif definition_title_state != "complete":
                    definition_match = None
            incomplete_reference_definition = bool(
                definition_prefix_match
                and not reference_line[definition_prefix_match.end() :].strip()
            )
            reference_definition = bool(
                definition_match or incomplete_reference_definition
            )
            reference_container_continues = False
            if markdown and previous_pending_reference_label is not None:
                reference_continuation = markdown_container_continuation(
                    line, previous_pending_reference_container_tokens
                )
                reference_container_continues = bool(
                    reference_continuation is not None
                    and not markdown_container_details(reference_continuation)[1]
                )
            reference_title_continues = False
            if (
                markdown
                and previous_pending_reference_title_container_tokens is not None
            ):
                title_continuation = markdown_container_continuation(
                    line, previous_pending_reference_title_container_tokens
                )
                title_container_continues = bool(
                    title_continuation is not None
                    and not markdown_container_details(title_continuation)[1]
                )
                if title_container_continues:
                    title_state = markdown_reference_title_state(reference_line)
                    if title_state == "complete":
                        reference_title_continues = True
                    elif title_state == "open":
                        (
                            consumed_title_lines,
                            title_scan_incomplete,
                        ) = markdown_multiline_reference_title_lines(
                            lines,
                            line_index,
                            reference_line,
                            previous_pending_reference_title_container_tokens,
                        )
                        if title_scan_incomplete:
                            item.link_parse_incomplete = True
                        if consumed_title_lines is not None:
                            reference_title_continues = True
                            multiline_reference_title_hidden_lines.update(
                                consumed_title_lines
                            )
            continuation_match = (
                markdown_reference_continuation_target(reference_line)
                if reference_container_continues
                else None
            )
            if (
                continuation_match
                and continuation_match.group(2)
                and not markdown_bare_destination_is_valid(
                    continuation_match.group(2)
                )
            ):
                continuation_match = None
            if continuation_match and (
                continuation_suffix := reference_line[
                    continuation_match.end() :
                ].strip()
            ):
                continuation_title_state = markdown_reference_title_state(
                    continuation_suffix
                )
                if continuation_title_state == "open":
                    (
                        consumed_title_lines,
                        title_scan_incomplete,
                    ) = markdown_multiline_reference_title_lines(
                        lines,
                        line_index,
                        continuation_suffix,
                        previous_pending_reference_container_tokens,
                    )
                    if title_scan_incomplete:
                        item.link_parse_incomplete = True
                    if consumed_title_lines is not None:
                        multiline_reference_title_hidden_lines.update(
                            consumed_title_lines
                        )
                    else:
                        continuation_match = None
                elif continuation_title_state != "complete":
                    continuation_match = None
            if reference_title_continues:
                reference_definition = True
            elif continuation_match:
                angle_target = continuation_match.group(1)
                target = (
                    angle_target
                    if angle_target is not None
                    else continuation_match.group(2)
                )
                reference_definitions.setdefault(
                    previous_pending_reference_label, target
                )
                reference_definition = True
                if not reference_line[continuation_match.end() :].strip():
                    pending_reference_title_container_tokens = (
                        previous_pending_reference_container_tokens
                    )
            elif definition_match:
                label = normalize_reference_label(definition_match.group(1))
                angle_target = definition_match.group(2)
                target = (
                    angle_target
                    if angle_target is not None
                    else definition_match.group(3)
                )
                reference_definitions.setdefault(label, target)
                if not reference_line[definition_match.end() :].strip():
                    pending_reference_title_container_tokens = container_tokens
            elif reference_definition:
                label_match = MARKDOWN_REFERENCE_DEFINITION_RE.match(reference_line)
                if label_match:
                    pending_reference_label = normalize_reference_label(
                        label_match.group(1)
                    )
                    pending_reference_container_tokens = container_tokens
            elif markdown:
                reference_use_line = markdown_mask_inline_links(line)
                if markdown_has_multiline_reference_label_start(
                    reference_use_line
                ) or (
                    not multiline_links
                    and markdown_unclosed_reference_label_continues(
                        lines,
                        line_index,
                        reference_use_line,
                        container_tokens,
                    )
                ):
                    item.link_parse_incomplete = True
                used_reference_labels.update(
                    markdown_reference_use_labels(reference_use_line)
                )
            line_task_ids = configured_task_ids(
                "" if reference_definition else semantic_line, task_id_pattern
            )
            task_ids.update(line_task_ids)
            structure_line, structure_tokens = (
                (container_line, container_tokens) if markdown else (line, ())
            )
            if markdown and paragraph_continuation_line is not None:
                structure_line = paragraph_continuation_line
                structure_tokens = paragraph_container_tokens
            previous_container_continues = False
            if previous_setext_candidate is not None:
                previous_tokens = previous_setext_candidate[3]
                continuation = markdown_container_continuation(
                    line, previous_tokens
                )
                continuation_tokens = (
                    markdown_container_details(continuation)[1]
                    if continuation is not None
                    else ()
                )
                if continuation is not None and (
                    not continuation_tokens
                    or MARKDOWN_THEMATIC_BREAK_RE.match(continuation)
                ):
                    previous_container_continues = True
                    structure_line = continuation
            heading_match = (
                MARKDOWN_HEADING_RE.match(structure_line) if markdown else None
            )
            setext_match = (
                MARKDOWN_SETEXT_RE.match(structure_line) if markdown else None
            )
            thematic_break = bool(
                markdown and MARKDOWN_THEMATIC_BREAK_RE.match(structure_line)
            )
            if heading_match:
                heading_level = len(heading_match.group(1))
                register_heading(heading_level, line_count, structure_line)
            elif (
                setext_match
                and previous_setext_candidate is not None
                and previous_container_continues
            ):
                heading_start, heading_text, heading_task_ids, _ = (
                    previous_setext_candidate
                )
                heading_level = 1 if setext_match.group(1).startswith("=") else 2
                register_heading(heading_level, heading_start, heading_text)
                if re.search(r"\b20\d{2}-\d{2}-\d{2}\b", heading_text):
                    item.dated_heading_count += 1
            if heading_match and DATED_HEADING_RE.search(structure_line):
                item.dated_heading_count += 1
            if not reference_definition:
                signal_lines.append((line_count, semantic_line))
            for start, _, label, raw_target in inline_links:
                if line[start : start + 1] != "!":
                    for nested_label, nested_target in markdown_nested_image_links(
                        label
                    ):
                        inline_link_candidates.append(
                            (nested_target, set())
                        )
                blocking_reference_labels = (
                    set()
                    if line[start : start + 1] == "!"
                    else markdown_reference_use_labels(
                        label, include_images=False
                    )
                )
                inline_link_candidates.append(
                    (raw_target, blocking_reference_labels)
                )
            if markdown:
                is_candidate = bool(
                    structure_line.strip()
                    and heading_match is None
                    and setext_match is None
                    and not thematic_break
                    and not reference_definition
                    and not MARKDOWN_NON_PARAGRAPH_PREFIX_RE.match(structure_line)
                )
                if (
                    is_candidate
                    and previous_setext_candidate is not None
                    and previous_container_continues
                ):
                    (
                        heading_start,
                        heading_text,
                        heading_task_ids,
                        previous_tokens,
                    ) = previous_setext_candidate
                    previous_setext_candidate = (
                        heading_start,
                        heading_text + "\n" + structure_line.rstrip("\r\n"),
                        heading_task_ids | line_task_ids,
                        previous_tokens,
                    )
                elif is_candidate:
                    previous_setext_candidate = (
                        line_count,
                        structure_line.rstrip("\r\n"),
                        line_task_ids,
                        structure_tokens,
                    )
                else:
                    previous_setext_candidate = None
                paragraph_heading = MARKDOWN_HEADING_RE.match(structure_line)
                paragraph_active = bool(
                    structure_line.strip()
                    and paragraph_heading is None
                    and setext_match is None
                    and not thematic_break
                    and not reference_definition
                )
                if paragraph_active:
                    if paragraph_continuation_line is None:
                        paragraph_container_tokens = structure_tokens
                else:
                    paragraph_container_tokens = ()
    defined_labels = set(reference_definitions)
    if task_id_pattern is not None:
        task_ids = set()
        item.task_heading_count = sum(
            bool(
                configured_task_ids(
                    heading_line, task_id_pattern, defined_labels
                )
            )
            for heading_line in heading_signal_lines
        )
    prepared_signal_lines: List[Tuple[int, str, str, str]] = []
    inline_raw_text_state: Optional[
        Tuple[str, int, Optional[str], Tuple[str, ...]]
    ] = None
    for signal_line_number, raw_signal_line in signal_lines:
        markdown_signal_line = (
            markdown_visible_signal_text(raw_signal_line, defined_labels)
            if markdown
            else raw_signal_line
        )
        html_signal_input = (
            markdown_mask_escaped_html_openers(markdown_signal_line)
            if markdown
            else markdown_signal_line
        )
        signal_line, inline_raw_text_state = html_visible_signal_text_with_state(
            html_signal_input, inline_raw_text_state
        )
        prepared_signal_lines.append(
            (signal_line_number, raw_signal_line, html_signal_input, signal_line)
        )
    html_events = [
        (line_number, fragment)
        for line_number, fragment in html_only_fragments
    ] + [
        (line_number, html_signal_input)
        for line_number, _, html_signal_input, _ in prepared_signal_lines
    ]
    for _, html_fragment in sorted(html_events, key=lambda event: event[0]):
        register_html_fragment(html_fragment)
    if any(namespace != "html" for _, namespace in html_element_stack):
        # An unclosed foreign-content boundary makes later namespace routing
        # ambiguous, so incoming-reference coverage cannot be certified.
        item.link_parse_incomplete = True
    for _, raw_signal_line, _, signal_line in prepared_signal_lines:
        item.unresolved_marker_count += len(UNRESOLVED_RE.findall(signal_line))
        supersession_field = SUPERSESSION_FIELD_RE.match(signal_line)
        if supersession_field:
            value = supersession_field.group(1).strip().strip("`<>").strip().lower()
            if value not in EMPTY_SUPERSESSION_VALUES:
                item.superseded_marker_count += 1
        else:
            item.superseded_marker_count += len(SUPERSEDED_RE.findall(signal_line))
        item.completed_marker_count += len(STATUS_RE.findall(signal_line))
        if task_id_pattern is not None:
            task_ids.update(
                configured_task_ids(signal_line, task_id_pattern, defined_labels)
            )
    document_base = html_base_href if html_base_seen else None
    for raw_target, _ in html_targets:
        # The first HTML <base> applies document-wide, including to elements
        # that occur before it in source order.
        raw_base = document_base
        target_source = item.absolute_path
        if "\\" in raw_target:
            # Special-scheme browser URLs preprocess backslashes as path
            # separators. Keep cleanup evidence conservative until that URL
            # algorithm is modeled directly.
            item.link_parse_incomplete = True
            continue
        if raw_base is not None:
            if "\\" in raw_base:
                item.link_parse_incomplete = True
                continue
            decoded_base = raw_base.strip()
            base_path_part = unquote(
                decoded_base.split("#", 1)[0].split("?", 1)[0].strip()
            )
            if not base_path_part:
                target_source = item.absolute_path
            elif base_path_part.startswith("//") or URI_SCHEME_RE.match(
                base_path_part
            ):
                item.link_parse_incomplete = True
                continue
            else:
                normalized_base = normalize_link_target(
                    root,
                    item.absolute_path,
                    base_path_part,
                    decode_markdown=False,
                )
                if normalized_base is None:
                    item.link_parse_incomplete = True
                    continue
                target_source = (
                    normalized_base / "__base__"
                    if base_path_part.endswith("/")
                    else normalized_base
                )
        normalized = normalize_link_target(
            root, target_source, raw_target, decode_markdown=False
        )
        if normalized is not None:
            links.add(normalized)
    for raw_target, nested_reference_labels in inline_link_candidates:
        if nested_reference_labels & defined_labels:
            continue
        normalized = normalize_link_target(root, item.absolute_path, raw_target)
        if normalized is not None:
            links.add(normalized)
    for label in used_reference_labels:
        raw_target = reference_definitions.get(label)
        if raw_target is None:
            continue
        normalized = normalize_link_target(root, item.absolute_path, raw_target)
        if normalized is not None:
            links.add(normalized)
    for _, section_start in open_sections:
        item.max_section_lines = max(
            item.max_section_lines, line_count - section_start + 1
        )
    if root_block_start is not None and line_count:
        item.max_section_lines = max(
            item.max_section_lines, line_count - root_block_start + 1
        )
    if item.markdown_heading_count and not item.max_section_lines:
        item.max_section_lines = line_count
    item.line_count = line_count
    item.nonblank_lines = nonblank
    item.status_only_signal = bool(item.completed_marker_count and nonblank <= 40)
    item.task_id_count = len(task_ids)
    item.task_ids = sorted(task_ids)[:20]
    return links


def age_distribution(files: Sequence[AuditFile], buckets: Sequence[int]) -> Dict[str, int]:
    counts: Counter = Counter()
    for item in files:
        lower = 0
        placed = False
        for upper in buckets:
            if item.age_days < upper:
                label = f"<{upper}" if lower == 0 else f"{lower}-{upper - 1}"
                counts[label] += 1
                placed = True
                break
            lower = upper
        if not placed:
            counts[f">={buckets[-1]}"] += 1
    ordered: Dict[str, int] = {}
    lower = 0
    for upper in buckets:
        label = f"<{upper}" if lower == 0 else f"{lower}-{upper - 1}"
        ordered[label] = counts[label]
        lower = upper
    ordered[f">={buckets[-1]}"] = counts[f">={buckets[-1]}"]
    return ordered


def candidate_hints(item: AuditFile) -> List[str]:
    hints: List[str] = []
    if item.size == 0:
        hints.append("empty_file")
    if item.duplicate_group:
        hints.append("exact_duplicate")
    if item.broken_targets:
        hints.append("possible_broken_reference")
    if item.status_only_signal:
        hints.append("status_only_signal")
    if item.superseded_marker_count:
        hints.append("superseded_signal")
    if item.task_heading_count and item.location_state in {"active", "canonical"}:
        hints.append("task_chronology_signal")
    if item.dated_heading_count >= 2 and item.location_state in {"active", "canonical"}:
        hints.append("dated_chronology_signal")
    lifecycle_categories = sum(
        bool(value)
        for value in (
            item.unresolved_marker_count,
            item.superseded_marker_count,
            item.completed_marker_count,
        )
    )
    if lifecycle_categories >= 2 and item.location_state in {"active", "canonical"}:
        hints.append("mixed_lifecycle_signal")
    if hints and item.unresolved_marker_count:
        hints.append("unresolved_markers_present")
    if hints and item.location_state in {"active", "canonical", "protected"}:
        hints.append(f"{item.location_state}_location")
    if hints and item.git_state in {"untracked"}:
        hints.append("untracked_git_state")
    if hints and item.git_state.startswith("modified:"):
        hints.append("modified_git_state")
    return hints


def file_summary(item: AuditFile, hints: Optional[List[str]] = None) -> Dict[str, object]:
    data: Dict[str, object] = {
        "path": item.relative_path,
        "scope": item.scope,
        "bytes": item.size,
        "modified_at": item.modified_at,
        "age_days": item.age_days,
        "location_state": item.location_state,
        "protected": item.protected,
        "git_state": item.git_state,
    }
    if item.line_count is not None:
        data.update(
            {
                "lines": item.line_count,
                "markdown_headings": item.markdown_heading_count,
                "task_headings": item.task_heading_count,
                "task_heading_ratio": (
                    round(item.task_heading_count / item.markdown_heading_count, 4)
                    if item.markdown_heading_count
                    else 0.0
                ),
                "max_section_lines": item.max_section_lines,
                "dated_headings": item.dated_heading_count,
                "unresolved_markers": item.unresolved_marker_count,
                "superseded_markers": item.superseded_marker_count,
                "completed_markers": item.completed_marker_count,
                "task_id_count": item.task_id_count,
                "task_ids": item.task_ids,
                "incoming_links": item.incoming_link_count,
                "incoming_links_coverage": item.incoming_link_coverage,
                "broken_targets": item.broken_targets,
            }
        )
    if item.duplicate_group:
        data["duplicate_group"] = item.duplicate_group
    if hints is not None:
        data["review_hints"] = hints
        data["review_category_hint"] = (
            "broken_reference" if "possible_broken_reference" in hints else "needs_human_decision"
        )
        data["sha256"] = item.fingerprint
    return data


def build_report(args: argparse.Namespace) -> Dict[str, object]:
    root = Path(args.root).expanduser().resolve(strict=True)
    if not root.is_dir():
        fail("--root must be a directory")

    scopes = [resolve_inside(root, raw, "--scope", True) for raw in args.scope]
    reference_roots = [
        resolve_inside(root, raw, "--reference-root", True)
        for raw in args.reference_root
    ]
    active_roots = [resolve_inside(root, raw, "--active-root", False) for raw in args.active_root]
    canonical_roots = [resolve_inside(root, raw, "--canonical", False) for raw in args.canonical]
    protected_roots = [resolve_inside(root, raw, "--protected", False) for raw in args.protected]
    historical_roots = [
        resolve_inside(root, raw, "--historical-root", False) for raw in args.historical_root
    ]
    archive_roots = [resolve_inside(root, raw, "--archive-root", False) for raw in args.archive_root]
    task_id_pattern = compile_task_id_pattern(args.task_id_regex)
    excluded_dirs = DEFAULT_EXCLUDED_DIRS | set(args.exclude_dir)
    now = datetime.now(timezone.utc)

    git_available = False
    tracked: Set[str] = set()
    git_status: Dict[str, str] = {}
    if args.include_git_state:
        git_available, tracked, git_status = git_inventory(root)

    files: List[AuditFile] = []
    seen: Set[Path] = set()
    skipped = Counter()
    scope_counts: Dict[str, Counter] = defaultdict(Counter)

    for scope in scopes:
        scope_label = scope.relative_to(root).as_posix() or "."
        for path in iter_scope_files(
            scope,
            excluded_dirs,
            skipped,
            "scope_symlink",
            "scope_excluded_dir",
            "scope_traversal_error",
        ):
            resolved = path.resolve(strict=False)
            if resolved in seen:
                continue
            seen.add(resolved)
            if secret_like(path):
                skipped["secret_like"] += 1
                continue
            try:
                stat = path.stat()
                binary = looks_binary(path)
            except (OSError, PermissionError):
                skipped["unreadable"] += 1
                continue
            if binary:
                skipped["binary"] += 1
                continue
            relative = path.relative_to(root).as_posix()
            state = location_state(
                path.resolve(strict=False),
                active_roots,
                canonical_roots,
                protected_roots,
                historical_roots,
                archive_roots,
            )
            age_days = max(0, int((now.timestamp() - stat.st_mtime) // 86400))
            item = AuditFile(
                absolute_path=path,
                relative_path=relative,
                scope=scope_label,
                size=stat.st_size,
                modified_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                age_days=age_days,
                location_state=state,
                protected=state in {"protected", "canonical", "active"},
                binary=False,
            )
            if args.include_git_state and git_available:
                item.git_state = git_status.get(
                    relative, "tracked_clean" if relative in tracked else "not_tracked"
                )
            files.append(item)
            scope_counts[scope_label]["files"] += 1
            scope_counts[scope_label]["bytes"] += stat.st_size

    links_by_source: Dict[str, Set[Path]] = {}
    incoming: Counter = Counter()
    link_coverage_status = "not_checked"
    link_source_files_scanned = 0
    external_link_source_files_scanned = 0
    if args.include_content_signals:
        audited_by_path = {
            item.absolute_path.resolve(strict=False): item for item in files
        }
        link_source_paths = {
            path: item.absolute_path
            for path, item in audited_by_path.items()
            if item.absolute_path.suffix.lower() in TEXT_EXTENSIONS
        }
        reference_scan_incomplete = False
        for reference_root in reference_roots:
            for path in iter_scope_files(
                reference_root,
                excluded_dirs,
                skipped,
                "reference_symlink",
                "reference_excluded_dir",
                "reference_traversal_error",
            ):
                resolved = path.resolve(strict=False)
                if resolved in link_source_paths:
                    continue
                if secret_like(path):
                    skipped["reference_secret_like"] += 1
                    reference_scan_incomplete = True
                    continue
                try:
                    if looks_binary(path):
                        skipped["reference_binary"] += 1
                        reference_scan_incomplete = True
                        continue
                except (OSError, PermissionError):
                    skipped["reference_unreadable"] += 1
                    reference_scan_incomplete = True
                    continue
                if path.suffix.lower() not in TEXT_EXTENSIONS:
                    skipped["reference_unsupported_text_extension"] += 1
                    reference_scan_incomplete = True
                    continue
                link_source_paths[resolved] = path

        if (
            skipped["reference_symlink"]
            or skipped["reference_excluded_dir"]
            or skipped["reference_traversal_error"]
        ):
            reference_scan_incomplete = True

        for resolved, source_path in sorted(
            link_source_paths.items(), key=lambda pair: pair[0].as_posix()
        ):
            item = audited_by_path.get(resolved)
            is_external_source = item is None
            try:
                source_size = source_path.stat().st_size
            except (OSError, PermissionError):
                skipped[
                    "reference_unreadable"
                    if is_external_source
                    else "content_unreadable"
                ] += 1
                reference_scan_incomplete = True
                continue
            if item is None:
                item = AuditFile(
                    absolute_path=source_path,
                    relative_path=source_path.relative_to(root).as_posix(),
                    scope="reference-only",
                    size=source_size,
                    modified_at="",
                    age_days=0,
                    location_state="reference-only",
                    protected=True,
                    binary=False,
                )
            if item.absolute_path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if source_size > args.max_content_bytes:
                skipped[
                    "reference_content_too_large"
                    if is_external_source
                    else "content_too_large"
                ] += 1
                reference_scan_incomplete = True
                continue
            if item.absolute_path.suffix.lower() in STRUCTURED_TEXT_EXTENSIONS:
                skipped["reference_unparsed_structured_source"] += 1
                reference_scan_incomplete = True
            elif item.absolute_path.suffix.lower() == ".mdx":
                skipped["reference_unparsed_mdx_source"] += 1
                reference_scan_incomplete = True
            elif item.absolute_path.suffix.lower() == ".txt":
                skipped["reference_unparsed_plain_text_source"] += 1
                reference_scan_incomplete = True
            try:
                targets = inspect_text(item, root, task_id_pattern)
            except UnicodeDecodeError:
                skipped[
                    "reference_content_decode_error"
                    if is_external_source
                    else "content_decode_error"
                ] += 1
                reference_scan_incomplete = True
                continue
            except (OSError, PermissionError):
                skipped[
                    "reference_content_unreadable"
                    if is_external_source
                    else "content_unreadable"
                ] += 1
                reference_scan_incomplete = True
                continue
            if item.link_parse_incomplete:
                skipped["reference_parse_incomplete"] += 1
                reference_scan_incomplete = True
            link_source_files_scanned += 1
            if is_external_source:
                external_link_source_files_scanned += 1
            else:
                links_by_source[item.relative_path] = targets
            for target in targets:
                if target != resolved:
                    incoming[target] += 1

        if not reference_roots:
            link_coverage_status = "scoped_only_incomplete"
        elif reference_scan_incomplete:
            link_coverage_status = "declared_reference_roots_with_skips_incomplete"
        else:
            link_coverage_status = "declared_reference_roots"
        for item in files:
            item.incoming_link_count = incoming[item.absolute_path.resolve(strict=False)]
            item.incoming_link_coverage = link_coverage_status
            broken = [
                target.relative_to(root).as_posix()
                for target in links_by_source.get(item.relative_path, set())
                if not target.exists()
            ]
            item.broken_targets = sorted(broken)[:20]

    same_size: Dict[int, List[AuditFile]] = defaultdict(list)
    for item in files:
        if item.size > 0:
            same_size[item.size].append(item)
    duplicate_groups: List[Dict[str, object]] = []
    for size, group in same_size.items():
        if len(group) < 2:
            continue
        hashes: Dict[str, List[AuditFile]] = defaultdict(list)
        for item in group:
            try:
                hashes[hash_file(item.absolute_path)].append(item)
            except (OSError, PermissionError):
                skipped["hash_unreadable"] += 1
        for digest, matches in hashes.items():
            if len(matches) < 2:
                continue
            group_id = digest[:12]
            paths = sorted(item.relative_path for item in matches)
            for item in matches:
                item.duplicate_group = group_id
            duplicate_groups.append(
                {"id": group_id, "sha256": digest, "bytes_each": size, "paths": paths}
            )
    duplicate_groups.sort(key=lambda group: (-int(group["bytes_each"]), str(group["id"])))

    candidate_rows: List[Tuple[AuditFile, List[str]]] = []
    for item in files:
        hints = candidate_hints(item)
        if hints:
            try:
                item.fingerprint = hash_file(item.absolute_path)
            except (OSError, PermissionError):
                item.fingerprint = None
                hints.append("fingerprint_unavailable")
            candidate_rows.append((item, hints))
    candidate_rows.sort(
        key=lambda row: (
            0 if "possible_broken_reference" in row[1] else 1,
            -row[0].size,
            row[0].relative_path,
        )
    )

    total_candidates = len(candidate_rows)
    selected_candidates = (
        candidate_rows if args.candidate_limit == 0 else candidate_rows[: args.candidate_limit]
    )
    largest = sorted(files, key=lambda item: (-item.size, item.relative_path))[: args.top]
    shown_duplicates = duplicate_groups[: args.top]

    report: Dict[str, object] = {
        "schema_version": 3,
        "generated_at": now.isoformat(),
        "read_only": True,
        "root": str(root),
        "scopes": [scope.relative_to(root).as_posix() or "." for scope in scopes],
        "link_coverage": {
            "status": link_coverage_status,
            "complete_for_declared_roots": link_coverage_status
            == "declared_reference_roots",
            "configuration_match": "not_checked_by_script",
            "reference_roots": [
                path.relative_to(root).as_posix() or "." for path in reference_roots
            ],
            "source_files_scanned": link_source_files_scanned,
            "external_source_files_scanned": external_link_source_files_scanned,
        },
        "options": {
            "content_signals": args.include_content_signals,
            "max_content_bytes": args.max_content_bytes,
            "git_state": args.include_git_state,
            "age_buckets": args.age_buckets,
            "top": args.top,
            "candidate_limit": args.candidate_limit,
            "task_id_regex_configured": task_id_pattern is not None,
        },
        "summary": {
            "files": len(files),
            "bytes": sum(item.size for item in files),
            "lines": (
                sum(item.line_count or 0 for item in files)
                if args.include_content_signals
                else None
            ),
            "candidate_signals": total_candidates,
            "candidate_signals_shown": len(selected_candidates),
            "exact_duplicate_groups": len(duplicate_groups),
            "possible_broken_references": sum(bool(item.broken_targets) for item in files),
            "skipped": dict(sorted(skipped.items())),
            "git_available": git_available if args.include_git_state else None,
        },
        "by_scope": {
            scope: {"files": counts["files"], "bytes": counts["bytes"]}
            for scope, counts in sorted(scope_counts.items())
        },
        "by_location_state": dict(sorted(Counter(item.location_state for item in files).items())),
        "age_distribution_days": age_distribution(files, args.age_buckets),
        "largest_files": [file_summary(item) for item in largest],
        "exact_duplicate_groups": shown_duplicates,
        "candidates": [
            file_summary(item, hints=hints) for item, hints in selected_candidates
        ],
        "notice": (
            "No files were changed. Candidate signals require semantic review; "
            "age and size alone never authorize cleanup."
        ),
    }
    return report


def format_bytes(value: int) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def print_text(report: Dict[str, object]) -> None:
    summary = report["summary"]
    print("Project context audit (read-only)")
    print(f"Root: {report['root']}")
    print(f"Scopes: {', '.join(report['scopes'])}")
    link_coverage = report["link_coverage"]
    if link_coverage["status"] != "not_checked":
        roots = ", ".join(link_coverage["reference_roots"]) or "none"
        print(
            f"Incoming-link coverage: {link_coverage['status']} "
            f"(reference roots: {roots})"
        )
    line_part = f", lines={summary['lines']}" if summary["lines"] is not None else ""
    print(
        f"Files: {summary['files']}, size={format_bytes(summary['bytes'])}{line_part}, "
        f"candidate signals={summary['candidate_signals']}"
    )
    print(f"Location states: {json.dumps(report['by_location_state'], ensure_ascii=False)}")
    print(f"Age buckets (days): {json.dumps(report['age_distribution_days'])}")
    if summary["skipped"]:
        print(f"Skipped: {json.dumps(summary['skipped'], ensure_ascii=False)}")

    print("Largest files:")
    for item in report["largest_files"]:
        structure = ""
        if "markdown_headings" in item:
            structure = (
                f" [headings={item['markdown_headings']}, "
                f"task_headings={item['task_headings']}, "
                f"max_section_lines={item['max_section_lines']}]"
            )
        print(f"  {format_bytes(item['bytes']):>10}  {item['path']}{structure}")

    print("Exact duplicate groups:")
    groups = report["exact_duplicate_groups"]
    if not groups:
        print("  none")
    for group in groups:
        print(f"  {group['id']} ({format_bytes(group['bytes_each'])} each)")
        for path in group["paths"]:
            print(f"    {path}")

    print("Candidate signals:")
    candidates = report["candidates"]
    if not candidates:
        print("  none")
    for item in candidates:
        hints = ", ".join(item["review_hints"])
        print(f"  {item['path']} [{hints}]")
    shown = summary["candidate_signals_shown"]
    total = summary["candidate_signals"]
    if shown < total:
        print(f"  ... {total - shown} more; use --candidate-limit 0 to show all")
    print(report["notice"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only inventory of explicit project-context scopes. "
            "It emits signals, not deletion decisions."
        )
    )
    parser.add_argument("--root", required=True, help="Workspace root")
    parser.add_argument(
        "--scope", action="append", required=True, help="File or directory to audit; repeatable"
    )
    parser.add_argument(
        "--reference-root",
        action="append",
        default=[],
        help=(
            "Configured file or directory scanned only as an incoming-link source; "
            "repeatable"
        ),
    )
    parser.add_argument("--active-root", action="append", default=[], help="Active-context root")
    parser.add_argument("--canonical", action="append", default=[], help="Canonical path")
    parser.add_argument("--protected", action="append", default=[], help="Protected path")
    parser.add_argument(
        "--historical-root", action="append", default=[], help="Historical-context root"
    )
    parser.add_argument("--archive-root", action="append", default=[], help="Archive root")
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Additional directory basename to skip",
    )
    parser.add_argument(
        "--include-content-signals",
        action="store_true",
        help="Count lines and inspect bounded semantic/link signals without printing content",
    )
    parser.add_argument(
        "--max-content-bytes",
        type=int,
        default=DEFAULT_MAX_CONTENT_BYTES,
        help=(
            "Maximum bytes loaded from one content/reference source; larger files "
            "are skipped and reference coverage is marked incomplete"
        ),
    )
    parser.add_argument(
        "--include-git-state",
        action="store_true",
        help="Report tracked, modified, and untracked state when root is a Git worktree",
    )
    parser.add_argument(
        "--task-id-regex",
        help=(
            "Optional project validation regex applied with fullmatch to neutral "
            "identifier tokens"
        ),
    )
    parser.add_argument(
        "--age-buckets",
        default="30,90,180",
        help="Comma-separated display buckets in days; never deletion thresholds",
    )
    parser.add_argument("--top", type=int, default=20, help="Maximum summary rows")
    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=50,
        help="Maximum candidate-signal rows; 0 shows all",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main() -> None:
    if sys.version_info < MIN_PYTHON:
        fail("Python 3.9 or newer is required", code=1)
    parser = build_parser()
    args = parser.parse_args()
    if args.top < 0 or args.candidate_limit < 0:
        fail("--top and --candidate-limit must be zero or greater")
    if args.max_content_bytes <= 0:
        fail("--max-content-bytes must be greater than zero")
    args.age_buckets = parse_age_buckets(args.age_buckets)
    report = build_report(args)
    if args.format == "json":
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        print_text(report)


if __name__ == "__main__":
    main()
