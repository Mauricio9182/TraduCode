from flask import Flask, render_template, request, jsonify
import ply.lex as lex_module
import requests
from semantic import validate_semantics
from dictionary import (
    classify_word, translate_word, full_dict_en_es,
    nouns, verbs, adjectives, articles, pronouns,
    adverbs, prepositions, conjunctions, interjections, contractions
)

app = Flask(__name__)

# =============================================
# TOKENS
# =============================================
tokens = [
    'ARTICULO', 'SUSTANTIVO', 'VERBO', 'ADJETIVO',
    'PRONOMBRE', 'ADVERBIO', 'PREPOSICION', 'CONJUNCION',
    'INTERJECCION', 'CONTRACCION', 'PUNTUACION', 'DESCONOCIDO',
]

# =============================================
# LEXER
# =============================================
error_table = []
symbol_table = {}

def t_WORD(t):
    r"[a-zA-Z]+\'?[a-zA-Z]*|[.,!?;:\"'\(\)\-]"
    word = t.value.lower()
    category = classify_word(t.value)
    translation = translate_word(t.value)
    t.type = category

    if word not in symbol_table:
        symbol_table[word] = {
            'palabra': t.value,
            'categoria': category,
            'traduccion': translation if translation else '???',
            'linea': t.lexer.lineno
        }

    if category == 'DESCONOCIDO':
        error_table.append({
            'tipo': 'Error Léxico',
            'palabra': t.value,
            'linea': t.lexer.lineno,
            'columna': find_column(t),
            'descripcion': f"Palabra no encontrada en el diccionario: '{t.value}'"
        })
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t\r'

def t_error(t):
    error_table.append({
        'tipo': 'Error Léxico',
        'palabra': t.value[0],
        'linea': t.lexer.lineno,
        'columna': find_column(t),
        'descripcion': f"Carácter no reconocido: '{t.value[0]}'"
    })
    t.lexer.skip(1)

def find_column(t):
    last_newline = t.lexer.lexdata.rfind('\n', 0, t.lexpos)
    if last_newline < 0:
        last_newline = -1
    return t.lexpos - last_newline

lexer = lex_module.lex()

# =============================================
# PARSER + ÁRBOL
# =============================================
import ply.yacc as yacc

syntax_errors = []
tree_nodes = []
tree_edges = []
node_counter = [0]
translation_parts = []

def reset_all():
    global tree_nodes, tree_edges, translation_parts
    error_table.clear()
    symbol_table.clear()
    syntax_errors.clear()
    tree_nodes = []
    tree_edges = []
    translation_parts = []
    node_counter[0] = 0
    lexer.lineno = 1

def new_node(label, parent=None):
    node_id = f"n{node_counter[0]}"
    node_counter[0] += 1
    tree_nodes.append({'id': node_id, 'label': label})
    if parent:
        tree_edges.append({'from': parent, 'to': node_id})
    return node_id

def trans(word):
    return translate_word(word) or word

def p_sentence(p):
    '''sentence : subject predicate
                | subject predicate complement
                | interjection
                | sentence PUNTUACION'''
    root = new_node('sentence')
    for item in p[1:]:
        if item and isinstance(item, str):
            new_node(item, root)
    translation_parts.append(' '.join(str(x) for x in p[1:] if x and x not in '.,!?'))
    p[0] = root

def p_subject_pronoun(p):
    'subject : PRONOMBRE'
    node = new_node('subject')
    new_node(f'PRONOMBRE: {p[1]}', node)
    p[0] = trans(p[1])

def p_subject_article_noun(p):
    'subject : ARTICULO SUSTANTIVO'
    node = new_node('subject')
    new_node(f'ARTICULO: {p[1]}', node)
    new_node(f'SUSTANTIVO: {p[2]}', node)
    p[0] = f"{trans(p[1])} {trans(p[2])}"

def p_subject_article_adj_noun(p):
    'subject : ARTICULO ADJETIVO SUSTANTIVO'
    node = new_node('subject')
    new_node(f'ARTICULO: {p[1]}', node)
    new_node(f'ADJETIVO: {p[2]}', node)
    new_node(f'SUSTANTIVO: {p[3]}', node)
    p[0] = f"{trans(p[1])} {trans(p[3])} {trans(p[2])}"

def p_subject_noun(p):
    'subject : SUSTANTIVO'
    node = new_node('subject')
    new_node(f'SUSTANTIVO: {p[1]}', node)
    p[0] = trans(p[1])

def p_predicate_verb(p):
    'predicate : VERBO'
    node = new_node('predicate')
    new_node(f'VERBO: {p[1]}', node)
    p[0] = trans(p[1])

def p_predicate_verb_complement(p):
    'predicate : VERBO complement'
    node = new_node('predicate')
    new_node(f'VERBO: {p[1]}', node)
    if p[2]:
        new_node(str(p[2]), node)
    p[0] = f"{trans(p[1])} {p[2]}"

def p_predicate_verb_adverb(p):
    'predicate : VERBO ADVERBIO'
    node = new_node('predicate')
    new_node(f'VERBO: {p[1]}', node)
    new_node(f'ADVERBIO: {p[2]}', node)
    p[0] = f"{trans(p[1])} {trans(p[2])}"

def p_predicate_verb_pronoun(p):
    'predicate : VERBO PRONOMBRE'
    node = new_node('predicate')
    new_node(f'VERBO: {p[1]}', node)
    new_node(f'PRONOMBRE: {p[2]}', node)
    p[0] = f"{trans(p[1])} {trans(p[2])}"

def p_complement_noun(p):
    'complement : SUSTANTIVO'
    node = new_node('complement')
    new_node(f'SUSTANTIVO: {p[1]}', node)
    p[0] = trans(p[1])

def p_complement_article_noun(p):
    'complement : ARTICULO SUSTANTIVO'
    node = new_node('complement')
    new_node(f'ARTICULO: {p[1]}', node)
    new_node(f'SUSTANTIVO: {p[2]}', node)
    p[0] = f"{trans(p[1])} {trans(p[2])}"

def p_complement_adj(p):
    'complement : ADJETIVO'
    node = new_node('complement')
    new_node(f'ADJETIVO: {p[1]}', node)
    p[0] = trans(p[1])

def p_complement_prep_article_noun(p):
    'complement : PREPOSICION ARTICULO SUSTANTIVO'
    node = new_node('complement')
    new_node(f'PREPOSICION: {p[1]}', node)
    new_node(f'ARTICULO: {p[2]}', node)
    new_node(f'SUSTANTIVO: {p[3]}', node)
    p[0] = f"{trans(p[1])} {trans(p[2])} {trans(p[3])}"

def p_complement_prep_noun(p):
    'complement : PREPOSICION SUSTANTIVO'
    node = new_node('complement')
    new_node(f'PREPOSICION: {p[1]}', node)
    new_node(f'SUSTANTIVO: {p[2]}', node)
    p[0] = f"{trans(p[1])} {trans(p[2])}"

def p_complement_adverb(p):
    'complement : ADVERBIO'
    node = new_node('complement')
    new_node(f'ADVERBIO: {p[1]}', node)
    p[0] = trans(p[1])

def p_interjection(p):
    'interjection : INTERJECCION'
    node = new_node('interjection')
    new_node(f'INTERJECCION: {p[1]}', node)
    p[0] = trans(p[1])

def p_empty(p):
    'empty :'
    pass

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

parser = yacc.yacc()

# =============================================
# FLASK ROUTES
# =============================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def do_translate():
    data = request.get_json()
    text = data.get('text', '')

    reset_all()

    # Tokenizar
    temp_lexer = lexer.clone()
    temp_lexer.lineno = 1
    temp_lexer.input(text)
    tokens_list = []
    while True:
        tok = temp_lexer.token()
        if not tok:
            break
        tokens_list.append({
            'palabra': tok.value,
            'tipo': tok.type,
            'linea': tok.lineno
        })

    error_table.clear()

    # Parsear línea por línea
    lexer.lineno = 1
    lines = text.strip().split('\n')
    for line in lines:
        if line.strip():
            parser.parse(line.strip(), lexer=lexer)

    # VALIDAR SEMÁNTICA
    semantic_errors = validate_semantics(tokens_list)    

    # Traducción con MyMemory API
    try:
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={
                "q": text,
                "langpair": "en|es"
            },
            timeout=5
        )
        if response.status_code == 200:
            translation = response.json().get("responseData", {}).get("translatedText", "")
            if not translation:
                translation = ' '.join(translation_parts)
        else:
            translation = ' '.join(translation_parts)
    except:
        translation = ' '.join(translation_parts)

    return jsonify({
        'tokens': tokens_list,
        'symbols': list(symbol_table.values()),
        'lexic_errors': error_table,
        'syntax_errors': syntax_errors,
        'semantic_errors': semantic_errors,
        'tree_nodes': tree_nodes,
        'tree_edges': tree_edges,
        'translation': translation,
        'success': len(syntax_errors) == 0 and len(error_table) == 0
    })

@app.route('/load_file', methods=['POST'])
def load_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    content = file.read().decode('utf-8')
    return jsonify({'content': content})

if __name__ == '__main__':
    app.run(debug=True)