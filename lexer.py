import ply.lex as lex
from dictionary import classify_word, translate_word, full_dict_en_es

# =============================================
# TRADUCODE - ANALIZADOR LÉXICO
# =============================================

# Tabla de tokens
tokens = [
    'ARTICULO',
    'SUSTANTIVO',
    'VERBO',
    'ADJETIVO',
    'PRONOMBRE',
    'ADVERBIO',
    'PREPOSICION',
    'CONJUNCION',
    'INTERJECCION',
    'CONTRACCION',
    'PUNTUACION',
    'DESCONOCIDO',
]

# Tablas
error_table = []
symbol_table = {}
token_list = []

# =============================================
# REGLA PRINCIPAL
# =============================================
def t_WORD(t):
    r'[a-zA-Z]+\'?[a-zA-Z]*|[.,!?;:\"\'\(\)\-]'

    word = t.value.lower()

    # Detectar puntuación
    if t.value in '.,!?;:"()-':
        category = 'PUNTUACION'
        translation = t.value
    else:
        category = classify_word(t.value)
        translation = translate_word(t.value)

    t.type = category

    # Agregar a tabla de símbolos
    if word not in symbol_table:
        symbol_table[word] = {
            'palabra': t.value,
            'categoria': category,
            'traduccion': translation if translation else '???',
            'linea': t.lexer.lineno
        }

    # Registrar error solo si NO es puntuación
    if category == 'DESCONOCIDO' and t.value not in '.,!?;:"()-':
        error_table.append({
            'tipo': 'Error Léxico',
            'palabra': t.value,
            'linea': t.lexer.lineno,
            'columna': find_column(t),
            'descripcion': f"Palabra no encontrada en el diccionario: '{t.value}'"
        })

    return t

# =============================================
# RASTREAR LÍNEAS
# =============================================
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# =============================================
# IGNORAR ESPACIOS
# =============================================
t_ignore = ' \t\r'

# =============================================
# ERROR LÉXICO
# =============================================
def t_error(t):
    error_table.append({
        'tipo': 'Error Léxico',
        'palabra': t.value[0],
        'linea': t.lexer.lineno,
        'columna': find_column(t),
        'descripcion': f"Carácter no reconocido: '{t.value[0]}'"
    })

    t.lexer.skip(1)

# =============================================
# CALCULAR COLUMNA
# =============================================
def find_column(t):
    last_newline = t.lexer.lexdata.rfind('\n', 0, t.lexpos)

    if last_newline < 0:
        last_newline = -1

    return t.lexpos - last_newline

# =============================================
# CREAR LEXER
# =============================================
lexer = lex.lex()