#!/usr/bin/env python3
"""
generate_docs.py — Generador de documentación Markdown para Dashboard RPi
Uso: python3 generate_docs.py /ruta/al/proyecto [--out docs/]
Requiere solo stdlib. No importa el código — parseo estático via ast.

Mejoras v2:
- Tabla de contenidos automática al inicio de cada .md
- Cobertura de docstrings por módulo (% documentado en el índice)
- Sección "Dependencias internas" por módulo (imports entre módulos del proyecto)
"""

import ast
import sys
import argparse
import textwrap
from pathlib import Path
from datetime import datetime

# ── Configuración ─────────────────────────────────────────────────────────────

LAYERS = [
    ("core",        "core/"),
    ("ui_main",     "ui/"),
    ("ui_windows",  "ui/windows/"),
    ("config",      "config/"),
    ("utils",       "utils/"),
]

# Prefijos de módulos internos del proyecto (para filtrar imports externos)
INTERNAL_PREFIXES = ("core", "ui", "config", "utils", "main")

# Carpetas a excluir dentro de ui/ (ui/windows/ se trata por separado)
UI_MAIN_EXCLUDE_DIRS = {"windows"}

# ── Helpers AST ───────────────────────────────────────────────────────────────

def get_docstring(node: ast.AST) -> str:
    """Extrae el docstring de un nodo AST o devuelve cadena vacía."""
    return ast.get_docstring(node) or ""


def format_arg(arg: ast.arg, defaults_map: dict) -> str:
    """Formatea un argumento con su anotación y valor por defecto si existe."""
    parts = [arg.arg]
    if arg.annotation:
        parts.append(f": {ast.unparse(arg.annotation)}")
    if arg.arg in defaults_map:
        parts.append(f" = {defaults_map[arg.arg]}")
    return "".join(parts)


def get_function_signature(node: ast.FunctionDef) -> str:
    """Construye la firma completa de una función/método."""
    args = node.args
    all_args = []

    n_args = len(args.args)
    n_defaults = len(args.defaults)
    defaults_map = {}
    for i, default in enumerate(args.defaults):
        arg_index = n_args - n_defaults + i
        try:
            defaults_map[args.args[arg_index].arg] = ast.unparse(default)
        except Exception:
            pass

    for arg in args.args:
        all_args.append(format_arg(arg, defaults_map))

    if args.vararg:
        all_args.append(f"*{args.vararg.arg}")

    kw_defaults = {}
    for i, kw_arg in enumerate(args.kwonlyargs):
        if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
            try:
                kw_defaults[kw_arg.arg] = ast.unparse(args.kw_defaults[i])
            except Exception:
                pass
    for kw_arg in args.kwonlyargs:
        all_args.append(format_arg(kw_arg, kw_defaults))

    if args.kwarg:
        all_args.append(f"**{args.kwarg.arg}")

    return_ann = ""
    if node.returns:
        try:
            return_ann = f" -> {ast.unparse(node.returns)}"
        except Exception:
            pass

    return f"({', '.join(all_args)}){return_ann}"


def get_class_attributes(node: ast.ClassDef) -> list[tuple[str, str]]:
    """
    Extrae atributos definidos en __init__ via self.xxx = ...
    Devuelve lista de (nombre, valor_repr).
    """
    attrs = []
    seen = set()
    for item in ast.walk(node):
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            for stmt in ast.walk(item):
                if (
                    isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Attribute)
                    and isinstance(stmt.targets[0].value, ast.Name)
                    and stmt.targets[0].value.id == "self"
                ):
                    attr_name = stmt.targets[0].attr
                    if attr_name not in seen:
                        seen.add(attr_name)
                        try:
                            val = ast.unparse(stmt.value)
                        except Exception:
                            val = "..."
                        attrs.append((attr_name, val))
    return attrs


def is_private(name: str) -> bool:
    return name.startswith("_")


# ── Cobertura de docstrings ────────────────────────────────────────────────────

def compute_coverage(tree: ast.Module) -> tuple[int, int]:
    """
    Cuenta funciones/métodos/clases documentados vs total.
    Devuelve (documentados, total).
    """
    documented = 0
    total = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            total += 1
            if ast.get_docstring(node):
                documented += 1
    return documented, total


def coverage_badge(documented: int, total: int) -> str:
    """Genera un indicador visual de cobertura."""
    if total == 0:
        return "N/A"
    pct = int(documented / total * 100)
    if pct >= 80:
        icon = "🟢"
    elif pct >= 50:
        icon = "🟡"
    else:
        icon = "🔴"
    return f"{icon} {pct}%"


def undocumented_list(tree: ast.Module) -> list[str]:
    """Devuelve lista de nombres de funciones/métodos/clases sin docstring."""
    missing = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not ast.get_docstring(node):
                missing.append(f"`{node.name}()` _(función)_")
        elif isinstance(node, ast.ClassDef):
            if not ast.get_docstring(node):
                missing.append(f"`{node.name}` _(clase)_")
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not ast.get_docstring(item):
                        missing.append(f"`{node.name}.{item.name}()` _(método)_")
    return missing


# ── Dependencias internas ──────────────────────────────────────────────────────

def get_internal_imports(tree: ast.Module) -> list[str]:
    """
    Extrae imports de módulos internos del proyecto.
    Filtra stdlib y dependencias externas por prefijo.
    """
    deps = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module
            if any(mod == p or mod.startswith(p + ".") for p in INTERNAL_PREFIXES):
                deps.add(mod)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                if any(mod == p or mod.startswith(p + ".") for p in INTERNAL_PREFIXES):
                    deps.add(mod)
    return sorted(deps)


# ── Tabla de contenidos ────────────────────────────────────────────────────────

def make_anchor(text: str) -> str:
    """Genera un anchor Markdown compatible con GitHub/Obsidian."""
    anchor = text.lower()
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-_ ")
    anchor = "".join(c if c in allowed else "" for c in anchor)
    anchor = anchor.strip().replace(" ", "-")
    while "--" in anchor:
        anchor = anchor.replace("--", "-")
    return anchor


def build_toc(tree: ast.Module) -> list[str]:
    """
    Construye la tabla de contenidos del módulo.
    Incluye funciones de módulo y clases con sus métodos públicos.
    """
    toc = []
    toc.append("## Tabla de contenidos\n")

    mod_fns = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    public_fns = [f for f in mod_fns if not is_private(f.name)]
    if public_fns:
        toc.append("**Funciones**")
        for fn in public_fns:
            anchor = make_anchor(f"funcion-{fn.name}")
            toc.append(f"- [`{fn.name}()`](#{anchor})")
        toc.append("")

    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    for cls in classes:
        anchor = make_anchor(f"clase-{cls.name}")
        toc.append(f"**Clase [`{cls.name}`](#{anchor})**")
        methods = [
            m for m in cls.body
            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not is_private(m.name)
        ]
        for method in methods:
            m_anchor = make_anchor(f"{method.name}{get_function_signature(method)}")
            toc.append(f"  - [`{method.name}()`](#{m_anchor})")
        toc.append("")

    return toc


# ── Renderizado Markdown ───────────────────────────────────────────────────────

def render_docstring(doc: str, indent: str = "") -> str:
    if not doc:
        return ""
    lines = textwrap.dedent(doc).strip().splitlines()
    return "\n".join(f"{indent}{line}" for line in lines) + "\n"


def render_function(node: ast.FunctionDef, level: int = 3, is_method: bool = False) -> str:
    sig = get_function_signature(node)
    prefix = "#" * level
    doc = get_docstring(node)

    lines = []
    lines.append(f"{prefix} `{node.name}{sig}`\n")
    if doc:
        lines.append(render_docstring(doc))
    else:
        lines.append("> ⚠️ _Sin documentar_\n")
    return "\n".join(lines)


def render_class(node: ast.ClassDef) -> str:
    lines = []
    doc = get_docstring(node)

    bases = []
    for base in node.bases:
        try:
            bases.append(ast.unparse(base))
        except Exception:
            pass
    base_str = f"({', '.join(bases)})" if bases else ""

    lines.append(f"## Clase `{node.name}{base_str}`\n")
    if doc:
        lines.append(render_docstring(doc))
    else:
        lines.append("> ⚠️ _Clase sin documentar_\n")

    # Atributos de instancia
    attrs = get_class_attributes(node)
    public_attrs = [(n, v) for n, v in attrs if not is_private(n)]
    private_attrs = [(n, v) for n, v in attrs if is_private(n)]

    if public_attrs:
        lines.append("### Atributos públicos\n")
        lines.append("| Atributo | Valor inicial |")
        lines.append("|----------|---------------|")
        for name, val in public_attrs:
            val_escaped = val.replace("|", "\\|")
            lines.append(f"| `{name}` | `{val_escaped}` |")
        lines.append("")

    if private_attrs:
        lines.append("### Atributos privados\n")
        lines.append("| Atributo | Valor inicial |")
        lines.append("|----------|---------------|")
        for name, val in private_attrs:
            val_escaped = val.replace("|", "\\|")
            lines.append(f"| `{name}` | `{val_escaped}` |")
        lines.append("")

    # Métodos
    methods = [
        item for item in node.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    public_methods = [m for m in methods if not is_private(m.name)]
    private_methods = [m for m in methods if is_private(m.name)]

    if public_methods:
        lines.append("### Métodos públicos\n")
        for method in public_methods:
            lines.append(render_function(method, level=4, is_method=True))

    if private_methods:
        lines.append("<details>\n<summary>Métodos privados</summary>\n")
        for method in private_methods:
            lines.append(render_function(method, level=4, is_method=True))
        lines.append("</details>\n")

    return "\n".join(lines)


def render_module(source: str, module_name: str, rel_path: str) -> str:
    """Parsea el source de un módulo y genera su Markdown completo."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return f"# {module_name}\n\n> ⚠️ Error de sintaxis: {e}\n"

    lines = []

    # ── Cabecera ──
    lines.append(f"# `{module_name}`\n")
    lines.append(f"> **Ruta**: `{rel_path}`\n")

    documented, total = compute_coverage(tree)
    badge = coverage_badge(documented, total)
    lines.append(f"> **Cobertura de documentación**: {badge} ({documented}/{total})\n")

    mod_doc = get_docstring(tree)
    if mod_doc:
        lines.append(render_docstring(mod_doc))

    lines.append("---\n")

    # ── Tabla de contenidos ──
    has_fns = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in tree.body)
    has_cls = any(isinstance(n, ast.ClassDef) for n in tree.body)
    if has_fns or has_cls:
        lines.extend(build_toc(tree))
        lines.append("---\n")

    # ── Dependencias internas ──
    internal_deps = get_internal_imports(tree)
    if internal_deps:
        lines.append("## Dependencias internas\n")
        for dep in internal_deps:
            lines.append(f"- `{dep}`")
        lines.append("")

    # ── Imports completos ──
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                imports.append(ast.unparse(node))
            except Exception:
                pass
    if imports:
        lines.append("## Imports\n")
        lines.append("```python")
        for imp in imports[:15]:
            lines.append(imp)
        if len(imports) > 15:
            lines.append(f"# ... y {len(imports) - 15} más")
        lines.append("```\n")

    # ── Constantes de módulo ──
    constants = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not is_private(target.id):
                    try:
                        val = ast.unparse(node.value)
                        constants.append((target.id, val))
                    except Exception:
                        pass
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and not is_private(node.target.id):
                try:
                    val = ast.unparse(node.value) if node.value else "..."
                    ann = ast.unparse(node.annotation)
                    constants.append((f"{node.target.id}: {ann}", val))
                except Exception:
                    pass

    if constants:
        lines.append("## Constantes / Variables de módulo\n")
        lines.append("| Nombre | Valor |")
        lines.append("|--------|-------|")
        for name, val in constants[:30]:
            val_short = val[:80] + "..." if len(val) > 80 else val
            val_escaped = val_short.replace("|", "\\|")
            lines.append(f"| `{name}` | `{val_escaped}` |")
        lines.append("")

    # ── Elementos sin documentar (colapsado) ──
    missing = undocumented_list(tree)
    if missing:
        lines.append(f"<details>\n<summary>⚠️ Sin documentar ({len(missing)} elementos)</summary>\n")
        for item in missing:
            lines.append(f"- {item}")
        lines.append("\n</details>\n")

    # ── Funciones de módulo ──
    mod_functions = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if mod_functions:
        public_fns = [f for f in mod_functions if not is_private(f.name)]
        private_fns = [f for f in mod_functions if is_private(f.name)]

        if public_fns:
            lines.append("## Funciones\n")
            for fn in public_fns:
                lines.append(render_function(fn, level=3, is_method=False))

        if private_fns:
            lines.append("<details>\n<summary>Funciones privadas</summary>\n")
            for fn in private_fns:
                lines.append(render_function(fn, level=3, is_method=False))
            lines.append("</details>\n")

    # ── Clases ──
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    for cls in classes:
        lines.append(render_class(cls))

    return "\n".join(lines)


# ── Recolección de archivos ────────────────────────────────────────────────────

def collect_py_files(root: Path, subdir: str, exclude_dirs: set = None) -> list[Path]:
    """Recolecta todos los .py de un subdirectorio."""
    target = root / subdir
    if not target.exists():
        return []

    files = []
    exclude_dirs = exclude_dirs or set()

    for py_file in sorted(target.rglob("*.py")):
        parts = py_file.relative_to(target).parts
        if any(part in exclude_dirs for part in parts[:-1]):
            continue
        if "__pycache__" in py_file.parts:
            continue
        files.append(py_file)

    return files


# ── Generación de docs ─────────────────────────────────────────────────────────

def module_name_from_path(root: Path, py_file: Path) -> str:
    rel = py_file.relative_to(root)
    parts = list(rel.with_suffix("").parts)
    return ".".join(parts)


def layer_display_name(layer_key: str) -> str:
    names = {
        "core":       "Core — Servicios y monitores",
        "ui_main":    "UI — Módulos principales",
        "ui_windows": "UI — Ventanas",
        "config":     "Config",
        "utils":      "Utils",
    }
    return names.get(layer_key, layer_key)


def generate(project_root: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    index_lines = []
    index_lines.append("# Dashboard RPi — Documentación de código\n")
    index_lines.append(f"> Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    index_lines.append("> Script: `generate_docs.py` · Parseo estático via `ast` — sin ejecución del código\n")
    index_lines.append("\n---\n")

    total_files = 0
    total_classes = 0
    total_functions = 0
    total_methods = 0
    total_doc = 0
    total_doc_total = 0

    for layer_key, layer_subdir in LAYERS:
        exclude_dirs = UI_MAIN_EXCLUDE_DIRS if layer_key == "ui_main" else None
        py_files = collect_py_files(project_root, layer_subdir, exclude_dirs)

        if not py_files:
            continue

        layer_name = layer_display_name(layer_key)
        layer_out_dir = out_dir / layer_key
        layer_out_dir.mkdir(exist_ok=True)

        index_lines.append(f"## {layer_name}\n")
        index_lines.append("| Módulo | Clases | Métodos | Funciones | Cobertura |")
        index_lines.append("|--------|--------|---------|-----------|-----------|")

        for py_file in py_files:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            mod_name = module_name_from_path(project_root, py_file)
            rel_path = str(py_file.relative_to(project_root))

            try:
                tree = ast.parse(source)
                n_classes = len([n for n in tree.body if isinstance(n, ast.ClassDef)])
                n_functions = len([n for n in tree.body
                                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
                n_methods = sum(
                    len([m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))])
                    for cls in tree.body if isinstance(cls, ast.ClassDef)
                )
                documented, doc_total = compute_coverage(tree)
                badge = coverage_badge(documented, doc_total)
                total_classes += n_classes
                total_functions += n_functions
                total_methods += n_methods
                total_doc += documented
                total_doc_total += doc_total
            except SyntaxError:
                n_classes = n_functions = n_methods = 0
                badge = "⚠️ SyntaxError"

            safe_name = mod_name.replace(".", "_")
            out_file = layer_out_dir / f"{safe_name}.md"

            md_content = render_module(source, mod_name, rel_path)
            out_file.write_text(md_content, encoding="utf-8")
            total_files += 1

            rel_link = f"{layer_key}/{safe_name}.md"
            index_lines.append(
                f"| [`{mod_name}`]({rel_link}) | {n_classes} | {n_methods} | {n_functions} | {badge} |"
            )

        index_lines.append("")

    # Resumen global
    global_badge = coverage_badge(total_doc, total_doc_total)
    index_lines.insert(3,
        f"> **{total_files} módulos** · **{total_classes} clases** · "
        f"**{total_methods} métodos** · **{total_functions} funciones** · "
        f"Cobertura global: **{global_badge}**\n"
    )

    (out_dir / "INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

    print(f"\n✅ Documentación generada en: {out_dir.resolve()}")
    print(f"   {total_files} módulos · {total_classes} clases · {total_methods} métodos · {total_functions} funciones")
    print(f"   Cobertura global: {global_badge} ({total_doc}/{total_doc_total})")
    print(f"   Índice: {out_dir / 'INDEX.md'}")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Genera documentación Markdown desde docstrings via AST."
    )
    parser.add_argument(
        "project_root",
        help="Ruta raíz del proyecto Dashboard RPi"
    )
    parser.add_argument(
        "--out",
        default="docs",
        help="Directorio de salida (default: docs/)"
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"❌ No existe: {project_root}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = project_root / out_dir

    print(f"📂 Proyecto: {project_root}")
    print(f"📄 Salida:   {out_dir}")
    generate(project_root, out_dir)


if __name__ == "__main__":
    main()
