#!/usr/bin/env python3
"""
Conversor de iconos Nerd Font
Acepta codepoints en cualquier formato y genera el escape Unicode listo
para pegar en config/settings.py → clase Icons.
"""


def surrogate_to_codepoint(high: int, low: int) -> int:
    return 0x10000 + (high - 0xD800) * 0x400 + (low - 0xDC00)


def is_surrogate_high(v: int) -> bool:
    return 0xD800 <= v <= 0xDBFF


def is_surrogate_low(v: int) -> bool:
    return 0xDC00 <= v <= 0xDFFF


def parse_input(raw: str) -> list[int]:
    """
    Acepta cualquiera de estos formatos (con o sin espacios/comas entre valores):
      \\udb81\\udda9
      \\uDB81\\uDDA9
      \\U000F06A9
      0xF06A9
      F06A9
      udb81 udda9
    Devuelve lista de enteros (1 o 2 valores según si es surrogate pair o directo).
    """
    import re
    # Normalizar: quitar backslashes, separar por espacios/comas
    cleaned = raw.replace("\\u", " ").replace("\\U", " ").replace(",", " ")
    tokens  = [t.strip() for t in cleaned.split() if t.strip()]

    values = []
    for token in tokens:
        token = token.lstrip("uU0x")
        try:
            values.append(int(token, 16))
        except ValueError:
            raise ValueError(f"No puedo parsear '{token}' como valor hexadecimal")
    return values


def convert(raw: str) -> dict:
    values = parse_input(raw)

    if len(values) == 2 and is_surrogate_high(values[0]) and is_surrogate_low(values[1]):
        # Par surrogate UTF-16
        cp     = surrogate_to_codepoint(values[0], values[1])
        method = "surrogate UTF-16"
        calc   = (
            f"  high = 0x{values[0]:04X} → 0x{values[0]:04X} - 0xD800 = 0x{values[0]-0xD800:03X}\n"
            f"  low  = 0x{values[1]:04X} → 0x{values[1]:04X} - 0xDC00 = 0x{values[1]-0xDC00:03X}\n"
            f"  cp   = 0x10000 + (0x{values[0]-0xD800:03X} × 0x400) + 0x{values[1]-0xDC00:03X} = 0x{cp:05X}"
        )
    elif len(values) == 1:
        cp     = values[0]
        method = "codepoint directo"
        calc   = f"  cp   = 0x{cp:05X}"
    else:
        raise ValueError(
            f"Formato no reconocido: se esperaba 1 codepoint o un par surrogate (high+low), "
            f"se recibieron {len(values)} valores: {[hex(v) for v in values]}"
        )

    char         = chr(cp)
    escape_upper = f"\\U{cp:08X}"
    escape_lower = f"\\u{cp:04x}" if cp <= 0xFFFF else None

    return {
        "cp":           cp,
        "char":         char,
        "escape":       escape_upper,
        "escape_lower": escape_lower,
        "method":       method,
        "calc":         calc,
    }


def format_result(name: str, result: dict) -> str:
    lines = [
        "",
        f"  Método   : {result['method']}",
        f"  Cálculo  :",
        result['calc'],
        f"  Codepoint: U+{result['cp']:05X}",
        f"  Carácter : {result['char']}",
        "",
        "  ── Para settings.py → clase Icons ──────────────────────────────",
        f'  {name.upper():<20}= "{result["escape"]}"          # {result["char"]}',
        "",
    ]
    return "\n".join(lines)


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        Nerd Font Icon Converter — settings.py            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  Formatos aceptados:")
    print("    \\udb81\\udda9   (surrogate pair, copiar tal cual de nerdfonts.com)")
    print("    \\U000F06A9     (escape Unicode directo)")
    print("    F06A9          (hex plano)")
    print("    0xF06A9        (hex con prefijo)")
    print()
    print("  Escribe 'q' para salir.")
    print()

    while True:
        try:
            raw = input("  Codepoint : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Saliendo.")
            break

        if raw.lower() in ("q", "quit", "exit", "salir"):
            print("  Saliendo.")
            break

        if not raw:
            continue

        name = input("  Nombre    : ").strip() or "NUEVO_ICONO"

        try:
            result = convert(raw)
            print(format_result(name, result))
        except ValueError as e:
            print(f"\n  ✗ Error: {e}\n")
            continue

        otro = input("  ¿Otro icono? [S/n]: ").strip().lower()
        if otro in ("n", "no"):
            print("  Saliendo.")
            break
        print()


if __name__ == "__main__":
    main()
