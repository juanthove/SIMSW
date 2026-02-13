from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
from typing import Iterable


SUPPORTED_EXTENSIONS: set[str] = {
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".html",
    ".htm",
    ".cshtml",
    ".razor",
    ".py",
    ".java",
    ".cs",
    ".php",
    ".rb",
    ".go",
    ".kt",
    ".sql",
    ".sh",
}

SKIP_FOLDERS: set[str] = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "bin",
    "obj",
    "target",
    "venv",
    ".venv",
    "pycache",
    "__pycache__",
    ".next",
    "_next",
    ".nuxt",
    "hts-cache",
}

CONTEXT_SIZE = 400
MAX_FILE_SIZE_BYTES = 2_000_000
MAX_CORPUS_FILES = 500


@dataclass(slots=True)
class PotentialFragment:
    file_name: str
    code_fragment: str
    start_pos: int
    end_pos: int
    keyword: str
    extension: str

    def to_dict(self) -> dict:
        return asdict(self)


def _keyword_to_regex(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword)
    if re.fullmatch(r"[A-Za-z0-9_. ]+", keyword):
        return re.compile(r"(?<!\w)" + escaped + r"(?!\w)", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def _merge_keywords(*groups: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for group in groups:
        for kw in group:
            normalized = kw.strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(normalized)
    return merged


def _compile_patterns(keywords: Iterable[str]) -> list[tuple[str, re.Pattern[str]]]:
    return [(kw, _keyword_to_regex(kw)) for kw in _merge_keywords(keywords)]


COMMON_KEYWORDS: list[str] = [
    "eval",
    "exec",
    "execute",
    "system",
    "shell_exec",
    "passthru",
    "assert",
    "pickle.loads",
    "yaml.load",
    "deserialize",
    "unserialize",
    "md5",
    "sha1",
    "random",
    "token",
    "password",
    "secret",
    "api_key",
    "private_key",
    "access_token",
    "innerHTML",
    "outerHTML",
    "document.write",
    "insertAdjacentHTML",
    "dangerouslySetInnerHTML",
    "v-html",
    "select",
    "insert",
    "update",
    "delete",
    "drop",
    "union",
    "where",
    "order by",
    "group by",
]

PYTHON_KEYWORDS: list[str] = [
    "eval",
    "exec",
    "compile",
    "execfile",
    "os.system",
    "subprocess.Popen",
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_output",
    "subprocess.getoutput",
    "subprocess.getstatusoutput",
    "runpy.run_module",
    "runpy.run_path",
    "pickle.loads",
    "pickle.load",
    "dill.loads",
    "yaml.load",
    "yaml.unsafe_load",
    "marshal.loads",
    "shelve.open",
    "tempfile.mktemp",
    "input",
    "__import__",
    "importlib.import_module",
    "request.args",
    "request.form",
    "request.get_json",
    "request.values",
    "request.cookies",
    "request.headers",
    "request.data",
    "request.files",
    "request.args.get",
    "request.form.get",
    "flask.request",
    "django.http",
    "cursor.execute",
    "raw",
    "mark_safe",
    "(debug=True)"
]

JAVASCRIPT_KEYWORDS: list[str] = [
    "eval",
    "Function",
    "new Function",
    "setTimeout",
    "setInterval",
    "setImmediate",
    "innerHTML",
    "outerHTML",
    "document.write",
    "insertAdjacentHTML",
    "dangerouslySetInnerHTML",
    "srcdoc",
    "localStorage",
    "sessionStorage",
    "postMessage",
    "window.postMessage",
    "atob",
    "btoa",
    "decodeURIComponent",
    "window.location",
    "location.hash",
    "location.search",
    "location.href",
    "window.open",
    "fetch",
    "XMLHttpRequest",
    "$.ajax",
    "$http",
    "child_process.exec",
    "child_process.execFile",
    "child_process.spawn",
    "child_process.fork",
    "vm.runInThisContext",
    "vm.runInNewContext",
    "vm.Script",
    "Buffer.from",
    "res.send",
    "res.write",
    "require",
]

DOTNET_KEYWORDS: list[str] = [
    "Authorize",
    "AllowAnonymous",
    "HttpGet",
    "HttpPost",
    "ValidateAntiForgeryToken",
    "IgnoreAntiforgeryToken",
    "ModelState.IsValid",
    "Request.Query",
    "Request.Form",
    "Request.Headers",
    "Request.Cookies",
    "Request.Body",
    "FromBody",
    "FromQuery",
    "RedirectToAction",
    "Console.WriteLine",
    "Password",
    "Username",
    "SignInAsync",
    "SignOutAsync",
    "AddAuthentication",
    "AddAuthorization",
    "AddCookie",
    "ClaimsIdentity",
    "ClaimTypes.Role",
    "UseAuthentication",
    "UseAuthorization",
    "Html.Raw",
    "Process.Start",
    "Environment.GetEnvironmentVariable",
    "File.ReadAllText",
    "File.WriteAllText",
    "BinaryFormatter.Deserialize",
    "JsonSerializer.Deserialize",
    "XmlSerializer",
    "SqlConnection",
    "SqlCommand",
    "ExecuteReader",
    "ExecuteNonQuery",
    "FromSqlRaw",
    "FromSqlInterpolated",
    "ExecuteSqlRaw",
    "AddWithValue",
    "connection string",
    "ConnectionStrings",
]

MARKUP_KEYWORDS: list[str] = [
    "<script",
    "onerror",
    "onclick",
    "onload",
    "javascript:",
    "v-html",
    "@Html.Raw",
    "Html.Raw",
    "dangerouslySetInnerHTML",
]

SQL_KEYWORDS: list[str] = [
    "select",
    "insert",
    "update",
    "delete",
    "drop",
    "union",
    "exec",
    "execute",
    "xp_cmdshell",
    "information_schema",
]

SHELL_KEYWORDS: list[str] = [
    "curl",
    "wget",
    "nc",
    "ncat",
    "bash -c",
    "sh -c",
    "chmod 777",
    "sudo",
    "eval",
    "exec",
]

CORPUS_DOTNET_DIRS = [Path("PC#")]
CORPUS_JS_DIRS = [Path("uruBotH"), Path("urubotAIH")]

CORPUS_SKIP_DIRS = {
    "bin",
    "obj",
    "node_modules",
    "wwwroot/lib",
    "_next/static",
    "hts-cache",
    "images.prismic.io",
    "assets.zyrosite.com",
}

CORPUS_HINTS = {
    "auth",
    "token",
    "password",
    "secret",
    "cookie",
    "session",
    "request",
    "response",
    "sql",
    "query",
    "form",
    "command",
    "exec",
    "deserialize",
    "serialize",
    "hash",
    "redirect",
    "header",
    "signin",
    "signout",
    "antiforgery",
    "html",
    "script",
    "storage",
    "location",
    "message",
    "fetch",
    "http",
    "api",
    "key",
    "file",
    "process",
    "environment",
}


def _is_in_corpus_skip(path: Path) -> bool:
    path_str = str(path).replace("\\", "/").lower()
    return any(skip in path_str for skip in CORPUS_SKIP_DIRS)


def _collect_corpus_keywords(dirs: Iterable[Path], suffixes: set[str]) -> list[str]:
    candidates: set[str] = set()
    processed = 0

    call_chain_re = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b")
    attr_re = re.compile(r"\[\s*([A-Za-z_][A-Za-z0-9_]*)")
    html_event_re = re.compile(r"\bon[a-z]{3,}\s*=", re.IGNORECASE)

    for base_dir in dirs:
        if not base_dir.exists() or not base_dir.is_dir():
            continue
        for current_root, subdirs, files in os.walk(base_dir, topdown=True):
            current_root_path = Path(current_root)
            if _is_in_corpus_skip(current_root_path):
                subdirs[:] = []
                continue

            subdirs[:] = [d for d in subdirs if not _is_in_corpus_skip(current_root_path / d)]

            for file_name in files:
                path = current_root_path / file_name
                if path.suffix.lower() not in suffixes:
                    continue
                if _is_in_corpus_skip(path):
                    continue
                try:
                    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                        continue
                    content = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

                for match in call_chain_re.finditer(content):
                    candidates.add(match.group(0))
                for match in attr_re.finditer(content):
                    candidates.add(match.group(1))
                if "<script" in content.lower():
                    candidates.add("<script")
                for match in html_event_re.finditer(content):
                    candidates.add(match.group(0).rstrip("=").strip())

                processed += 1
                if processed >= MAX_CORPUS_FILES:
                    break
            if processed >= MAX_CORPUS_FILES:
                break
        if processed >= MAX_CORPUS_FILES:
            break

    filtered: list[str] = []
    for token in sorted(candidates, key=str.lower):
        lowered = token.lower()
        if len(token) < 3 or len(token) > 80:
            continue
        if not any(ch.isalpha() for ch in token):
            continue
        if any(hint in lowered for hint in CORPUS_HINTS):
            filtered.append(token)

    return filtered


def _build_patterns() -> dict[str, list[tuple[str, re.Pattern[str]]]]:
    extra_dotnet = _collect_corpus_keywords(CORPUS_DOTNET_DIRS, {".cs", ".cshtml", ".razor"})
    extra_js = _collect_corpus_keywords(CORPUS_JS_DIRS, {".js", ".jsx", ".ts", ".tsx", ".html", ".htm"})

    return {
        "generic": _compile_patterns(COMMON_KEYWORDS),
        "python": _compile_patterns(_merge_keywords(PYTHON_KEYWORDS, COMMON_KEYWORDS)),
        "javascript": _compile_patterns(_merge_keywords(JAVASCRIPT_KEYWORDS, COMMON_KEYWORDS, extra_js)),
        "dotnet": _compile_patterns(_merge_keywords(DOTNET_KEYWORDS, COMMON_KEYWORDS, extra_dotnet)),
        "markup": _compile_patterns(_merge_keywords(MARKUP_KEYWORDS, COMMON_KEYWORDS, extra_js)),
        "sql": _compile_patterns(_merge_keywords(SQL_KEYWORDS, COMMON_KEYWORDS)),
        "shell": _compile_patterns(_merge_keywords(SHELL_KEYWORDS, COMMON_KEYWORDS)),
    }


PATTERNS = _build_patterns()


def _context_window(
    content: str,
    match_start: int,
    match_end: int,
    window_size: int = CONTEXT_SIZE,
) -> tuple[str, int, int]:
    half = window_size // 2
    start = max(0, match_start - half)
    end = min(len(content), match_end + half)
    return content[start:end], start, end


def _scan_content_with_patterns(
    content: str,
    file_path: Path,
    patterns: list[tuple[str, re.Pattern[str]]],
) -> list[PotentialFragment]:
    findings: list[PotentialFragment] = []
    all_matches: list[tuple[int, int, str]] = []

    for keyword, pattern in patterns:
        for match in pattern.finditer(content):
            all_matches.append((match.start(), match.end(), keyword))

    all_matches.sort(key=lambda item: (item[0], item[1], item[2].lower()))

    next_search_from = 0
    for match_start, match_end, keyword in all_matches:
        if match_start < next_search_from:
            continue

        fragment, start, end = _context_window(content, match_start, match_end)
        findings.append(
            PotentialFragment(
                file_name=str(file_path),
                code_fragment=fragment,
                start_pos=start,
                end_pos=end,
                keyword=keyword,
                extension=file_path.suffix.lower(),
            )
        )

        # Continue scanning from the end of the current context to avoid
        # duplicate matches (e.g. SELECT + WHERE + FROM inside one block).
        next_search_from = end

    findings.sort(key=lambda item: (item.file_name, item.start_pos, item.keyword.lower()))
    return findings


def scan_python_file(content: str, file_path: Path) -> list[PotentialFragment]:
    return _scan_content_with_patterns(content, file_path, PATTERNS["python"])


def scan_javascript_file(content: str, file_path: Path) -> list[PotentialFragment]:
    return _scan_content_with_patterns(content, file_path, PATTERNS["javascript"])


def scan_dotnet_file(content: str, file_path: Path) -> list[PotentialFragment]:
    return _scan_content_with_patterns(content, file_path, PATTERNS["dotnet"])


def scan_markup_file(content: str, file_path: Path) -> list[PotentialFragment]:
    return _scan_content_with_patterns(content, file_path, PATTERNS["markup"])


def scan_sql_file(content: str, file_path: Path) -> list[PotentialFragment]:
    return _scan_content_with_patterns(content, file_path, PATTERNS["sql"])


def scan_shell_file(content: str, file_path: Path) -> list[PotentialFragment]:
    return _scan_content_with_patterns(content, file_path, PATTERNS["shell"])


def scan_generic_file(content: str, file_path: Path) -> list[PotentialFragment]:
    return _scan_content_with_patterns(content, file_path, PATTERNS["generic"])


def analyze_file(file_path: Path) -> list[PotentialFragment]:
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
            return []
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    suffix = file_path.suffix.lower()

    if suffix == ".py":
        return scan_python_file(content, file_path)
    if suffix == ".cs":
        return scan_dotnet_file(content, file_path)
    if suffix in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte"}:
        return scan_javascript_file(content, file_path)
    if suffix in {".html", ".htm", ".cshtml", ".razor"}:
        return scan_markup_file(content, file_path)
    if suffix == ".sql":
        return scan_sql_file(content, file_path)
    if suffix == ".sh":
        return scan_shell_file(content, file_path)
    return scan_generic_file(content, file_path)


def iter_supported_files(root: Path, extensions: set[str] | None = None) -> Iterable[Path]:
    selected = {ext.lower() for ext in (extensions or SUPPORTED_EXTENSIONS)}

    for current_root, dirs, files in os.walk(root, topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_FOLDERS]
        for file_name in files:
            path = Path(current_root) / file_name
            if path.suffix.lower() in selected:
                yield path


def scan_directory(directory_path: str, extensions: set[str] | None = None) -> list[PotentialFragment]:
    root = Path(directory_path)
    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")

    results: list[PotentialFragment] = []
    for file_path in iter_supported_files(root, extensions=extensions):
        results.extend(analyze_file(file_path))
    return results


def scan_multiple_directories(
    directory_paths: Iterable[str],
    extensions: set[str] | None = None,
) -> list[PotentialFragment]:
    all_results: list[PotentialFragment] = []
    for directory_path in directory_paths:
        all_results.extend(scan_directory(directory_path, extensions=extensions))
    return all_results


def findings_to_dicts(findings: Iterable[PotentialFragment]) -> list[dict]:
    return [finding.to_dict() for finding in findings]
