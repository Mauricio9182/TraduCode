def validate_semantics(tokens):

    semantic_errors = []

    for i, token in enumerate(tokens):

        palabra = token['palabra']
        tipo = token['tipo']
        linea = token['linea']

        # ADJETIVO como sujeto
        if i == 0 and tipo == 'ADJETIVO':
            semantic_errors.append({
                'tipo': 'Error Semántico',
                'palabra': palabra,
                'linea': linea,
                'descripcion': 'Un adjetivo no puede ser sujeto'
            })

        # ADVERBIO como sujeto
        if i == 0 and tipo == 'ADVERBIO':
            semantic_errors.append({
                'tipo': 'Error Semántico',
                'palabra': palabra,
                'linea': linea,
                'descripcion': 'Un adverbio no puede ser sujeto'
            })

        # CONJUNCION como sujeto
        if i == 0 and tipo == 'CONJUNCION':
            semantic_errors.append({
                'tipo': 'Error Semántico',
                'palabra': palabra,
                'linea': linea,
                'descripcion': 'Una conjunción no puede iniciar como sujeto'
            })

        # INTERJECCION como sujeto
        if i == 0 and tipo == 'INTERJECCION':
            semantic_errors.append({
                'tipo': 'Error Semántico',
                'palabra': palabra,
                'linea': linea,
                'descripcion': 'Una interjección no puede ser sujeto'
            })

        # PREPOSICION al final
        if i == len(tokens)-1 and tipo == 'PREPOSICION':
            semantic_errors.append({
                'tipo': 'Error Semántico',
                'palabra': palabra,
                'linea': linea,
                'descripcion': 'La preposición quedó incompleta'
            })

    return semantic_errors