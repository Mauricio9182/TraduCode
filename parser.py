import ply.yacc as yacc
from lexer import tokens, error_table, symbol_table
from dictionary import translate_word

# =============================================
# TRADUCODE - ANALIZADOR SINTÁCTICO
# =============================================

syntax_errors = []
semantic_errors = []
translation_result = []

# =============================================
# REGLAS GRAMATICALES
# =============================================

# =============================================
# ORACIÓN COMPLETA
# =============================================
def p_sentence(p):
    '''sentence : subject predicate
                | subject predicate complement
                | interjection
                | sentence PUNTUACION
                | INTERJECCION SUSTANTIVO
                | INTERJECCION SUSTANTIVO PUNTUACION
                | ADVERBIO VERBO PRONOMBRE ADVERBIO
                | ADVERBIO VERBO PRONOMBRE ADVERBIO PUNTUACION'''

    p[0] = ' '.join(str(x) for x in p[1:] if x)

# =============================================
# SUJETO
# =============================================
def p_subject_pronoun(p):
    'subject : PRONOMBRE'

    p[0] = translate_word(p[1]) or p[1]

def p_subject_article_noun(p):
    'subject : ARTICULO SUSTANTIVO'

    p[0] = f"{translate_word(p[1]) or p[1]} {translate_word(p[2]) or p[2]}"

def p_subject_article_adj_noun(p):
    'subject : ARTICULO ADJETIVO SUSTANTIVO'

    p[0] = f"{translate_word(p[1]) or p[1]} {translate_word(p[3]) or p[3]} {translate_word(p[2]) or p[2]}"

def p_subject_noun(p):
    'subject : SUSTANTIVO'

    p[0] = translate_word(p[1]) or p[1]

# =============================================
# PREDICADO
# =============================================
def p_predicate_verb(p):
    'predicate : VERBO'

    p[0] = translate_word(p[1]) or p[1]

def p_predicate_verb_complement(p):
    'predicate : VERBO complement'

    p[0] = f"{translate_word(p[1]) or p[1]} {p[2]}"

def p_predicate_verb_adverb(p):
    'predicate : VERBO ADVERBIO'

    p[0] = f"{translate_word(p[1]) or p[1]} {translate_word(p[2]) or p[2]}"

# =============================================
# COMPLEMENTO
# =============================================
def p_complement_noun(p):
    'complement : SUSTANTIVO'

    p[0] = translate_word(p[1]) or p[1]

def p_complement_article_noun(p):
    'complement : ARTICULO SUSTANTIVO'

    p[0] = f"{translate_word(p[1]) or p[1]} {translate_word(p[2]) or p[2]}"

def p_complement_adj(p):
    'complement : ADJETIVO'

    p[0] = translate_word(p[1]) or p[1]

def p_complement_prep_article_noun(p):
    'complement : PREPOSICION ARTICULO SUSTANTIVO'

    p[0] = f"{translate_word(p[1]) or p[1]} {translate_word(p[2]) or p[2]} {translate_word(p[3]) or p[3]}"

def p_complement_prep_noun(p):
    'complement : PREPOSICION SUSTANTIVO'

    p[0] = f"{translate_word(p[1]) or p[1]} {translate_word(p[2]) or p[2]}"

def p_complement_adverb(p):
    'complement : ADVERBIO'

    p[0] = translate_word(p[1]) or p[1]

def p_complement_prep_alone(p):
    'complement : PREPOSICION'

    p[0] = translate_word(p[1]) or p[1]

# =============================================
# INTERJECCIÓN
# =============================================
def p_interjection(p):
    'interjection : INTERJECCION'

    p[0] = translate_word(p[1]) or p[1]

# =============================================
# VACÍO
# =============================================
def p_empty(p):
    'empty :'
    pass

# =============================================
# ERROR SINTÁCTICO
# =============================================
def p_error(p):

    if p:
        syntax_errors.append({
            'tipo': 'Error Sintáctico',
            'palabra': str(p.value),
            'linea': p.lineno,
            'descripcion': f"Estructura inválida cerca de: '{p.value}'"
        })

    else:
        syntax_errors.append({
            'tipo': 'Error Sintáctico',
            'palabra': 'EOF',
            'linea': 0,
            'descripcion': 'Oración incompleta o estructura inválida'
        })

# =============================================
# IMPRIMIR ERRORES
# =============================================
def print_syntax_errors():

    print("\n========== ERRORES SINTÁCTICOS ==========")

    if not syntax_errors:
        print("  (sin errores)")

    else:
        for e in syntax_errors:
            print(f"{e['tipo']} | {e['palabra']} | línea {e['linea']} | {e['descripcion']}")

# =============================================
# CREAR PARSER
# =============================================
parser = yacc.yacc()