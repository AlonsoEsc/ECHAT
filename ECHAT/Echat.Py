from flask import Flask, render_template, request, jsonify, session
import openai

# Configura tu clave de API de OpenAI
openai.api_key = 'API-KEY'

# Diccionario de palabras clave organizado por categorías para abarcar temas del idioma inglés
english_keywords = {
    "Saludo": [
        "hola", "buenos días", "buenas tardes", "buenas noches", "qué tal", "cómo estás", "saludos"
    ],
    "Solicitudes de ejemplos o listas": [
        "ejemplo", "lista", "muestra", "puedes darme ejemplos", "dame una lista", "quiero ejemplos", "ejemplos", "listas"
    ],
    "Gramática general": [
        "inglés", "idioma", "gramática", "estructura gramatical", "reglas gramaticales", "oración", 
        "sintaxis", "morfología", "sujeto", "predicado", "objeto directo", "objeto indirecto", 
        "estructura de la oración", "estructura formal", "estructura informal", "frase", "significado",
        "función gramatical", "pronombre", "modificador", "adverbio", "conjunción", "preposición"
    ],
    "Partes de la oración": [
        "sustantivo", "adjetivo", "adverbio", "verbo", "pronombre", "artículo", "determinante", 
        "conjunción", "preposición", "interjección", "sujeto tácito", "marcador discursivo"
    ],
    "Tiempos verbales": [
        "presente", "pasado", "futuro", "presente simple", "pasado simple", "futuro simple", 
        "presente continuo", "pasado continuo", "futuro continuo", "presente perfecto", 
        "pasado perfecto", "futuro perfecto", "tiempos verbales", "formas del verbo"
    ],
    "Formas del verbo": [
        "forma afirmativa", "forma negativa", "forma interrogativa", "imperativo", "infinitivo", 
        "participio", "condicional", "primer condicional", "segundo condicional", 
        "tercer condicional", "oraciones condicionales", "modo subjuntivo", "gerundio"
    ],
    "Verbos auxiliares y modales": [
        "auxiliar", "verbo auxiliar", "to be", "to have", "to do", "verbos modales", "can", "could","ING","ing", 
        "shall", "should", "may", "might", "will", "would", "must", "ought to", "uso de auxiliares", 
        "uso de modales"
    ],
    "Vocabulario y léxico": [
        "vocabulario", "palabra", "significado de palabra", "sinónimos", "antónimos", 
        "expresiones comunes", "expresiones idiomáticas", "slang", "jerga", "phrasal verbs", 
        "expresiones cotidianas", "vocabulario básico", "vocabulario avanzado", "expresiones populares",
        "lista de palabras", "palabras de transición", "palabras de enlace", "traducir", "Traductor", "Traduce"
    ],
    "Pronunciación y fonética": [
        "pronunciación", "fonética", "fonología", "acentuación", "silabeo", "transcripción fonética", 
        "homófonos", "diferencias de acento", "inglés británico", "inglés americano", "sonidos en inglés", 
        "modulación"
    ],
    "Puntuación y signos": [
        "puntuación", "signos de puntuación", "coma", "punto", "punto y coma", "dos puntos", "paréntesis", 
        "comillas", "signo de interrogación", "signo de exclamación", "punto de interrupción", 
        "diéresis", "uso de mayúsculas", "reglas de puntuación", "separación silábica"
    ],
    "Tipos de oraciones": [
        "oración afirmativa", "oración negativa", "oración interrogativa", "oración exclamativa", 
        "oraciones simples", "oraciones compuestas", "oraciones complejas", "oraciones subordinadas", 
        "coordinación", "subordinación", "frase declarativa", "frase imperativa"
    ],
    "Preguntas y respuestas": [
        "wh-questions", "yes/no questions", "preguntas indirectas", "formulación de preguntas", 
        "respuesta a preguntas", "cómo preguntar", "cómo responder"
    ],
    "Estilos y registro": [
        "registro formal", "registro informal", "inglés conversacional", "inglés académico", 
        "lenguaje técnico", "inglés coloquial", "tonos de comunicación", "estilo de escritura", 
        "inglés estándar", "dialectos del inglés"
    ],
    "Redacción y escritura": [
        "redacción", "estructura del párrafo", "coherencia", "cohesión", "argumentación", 
        "escritura narrativa", "escritura descriptiva", "escritura persuasiva", "tipos de ensayos", 
        "conectores lógicos", "transiciones", "orden lógico"
    ],
    "Comprensión lectora y práctica auditiva": [
        "comprensión de lectura", "análisis de textos", "comprensión auditiva", "escucha activa", 
        "práctica auditiva", "identificación de ideas principales", "resumen", "paráfrasis", 
        "preguntas de comprensión", "lectura crítica", "escuchar en inglés"
    ],
    "Funciones comunicativas": [
        "pedir información", "dar instrucciones", "expresar opinión", "disculparse", "expresar acuerdo", 
        "expresar desacuerdo", "dar sugerencias", "dar consejos", "expresar preferencias", 
        "hablar sobre experiencias", "hacer comparaciones", "expresar probabilidad", "expresar obligación"
    ],
    "Práctica del idioma": [
        "practicar inglés", "mejorar gramática", "mejorar vocabulario", "consejos para aprender inglés", 
        "aprender inglés", "ejercicios de inglés", "ejercicios de gramática", "ejercicios de vocabulario", 
        "aprender tiempos verbales", "consejos de pronunciación", "ejemplos en inglés"
    ],
    "Niveles de competencia": [
        "nivel básico de inglés", "nivel intermedio de inglés", "nivel avanzado de inglés", 
        "inglés A1", "inglés A2", "inglés B1", "inglés B2", "inglés C1", "inglés C2", 
        "principiante", "intermedio", "avanzado"
    ],
    "Errores comunes y consejos": [
        "errores comunes en inglés", "cómo evitar errores", "errores de gramática", "errores de vocabulario", 
        "errores de pronunciación", "consejos de gramática", "consejos de vocabulario", 
        "corrección de errores", "ejemplos de errores comunes"
    ],
    "Traducción": [
        "traduce", "traducción", "traducir"
    ],
    "Correcciones":
    [
        "Dime cual es el error", "corrige", "muestrame el error", "ayudame a corregir", "Enseñame el error"
    ]
}

app = Flask(__name__)
app.secret_key = '$I$T3MAS'

# Función para generar una respuesta de GPT-3.5 enfocada en inglés usando el historial de conversación
def generate_gpt3_response(question, conversation_history, is_translation=False, is_correction = False):
    # Configura el prompt según el tipo de pregunta
    if is_translation:
        prompt = f"Por favor, traduce al inglés la siguiente frase: {question}"
    else:
        prompt = f"Por favor, responde de manera precisa y solo sobre temas de gramática, vocabulario o aprendizaje del idioma inglés: {question}"

    # Agrega el mensaje del usuario actual al historial de mensajes
    conversation_history.append({"role": "user", "content": question})
    
    try:
        # Llamada a la API de OpenAI usando el historial de conversación
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en gramática, vocabulario y aprendizaje del idioma inglés. Responde de manera amigable y útil solo sobre temas de inglés, gramática, vocabulario y proporciona ejemplos o listas si el usuario lo solicita."}
            ] + conversation_history,
            max_tokens=300,
            temperature=0.5   # Temperatura baja para respuestas más precisas y menos aleatorias
        )
        
        # Obtén la respuesta del modelo y agrégala al historial
        ai_response = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    except openai.error.RateLimitError:
        return "Has alcanzado el límite de uso de la API. Inténtalo de nuevo más tarde o verifica tu cuenta de OpenAI."

    except openai.error.AuthenticationError:
        return "Error de autenticación. Verifica tu clave API."

    except Exception as e:
        return f"Ha ocurrido un error: {str(e)}"

# Ruta principal
@app.route("/")
def index():
    return render_template("chat.html")

# Ruta para procesar mensajes de chat
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message").lower()

    # Inicializa el historial de conversación si no existe en la sesión
    if 'conversation_history' not in session:
        session['conversation_history'] = []

    # Detecta si el usuario está solicitando una traducción
    is_translation = any(keyword in user_message for keyword in english_keywords["Traducción"])

    # Verifica si la pregunta está relacionada con el inglés, ejemplos, listas, saludos o traducción
    if not is_translation and not any(keyword in user_message for category in english_keywords.values() for keyword in category):
        return jsonify({"response": "Lo siento, solo puedo responder preguntas relacionadas con la gramática, el aprendizaje del idioma inglés, o solicitudes de ejemplos y listas."})

    # Genera la respuesta usando la función generate_gpt3_response y el historial de conversación
    ai_response = generate_gpt3_response(user_message, session['conversation_history'], is_translation)

    # Actualiza el historial de conversación en la sesión
    session['conversation_history'] = session['conversation_history'][-10:]  # Mantén solo los últimos 10 mensajes para no sobrecargar

    return jsonify({"response": ai_response})

# Ruta para limpiar el historial de conversación (si es necesario)
@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    session.pop('conversation_history', None)
    return jsonify({"response": "Bienvenido a Echat, soy tu asistente para que aprendas de una mejor manera el idioma inglés. Comienza preguntándome algo sobre el idioma."})

if __name__ == "__main__":
    app.run(debug=True)