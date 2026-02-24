Justificación de las expresiones regulares

Las expresiones regulares se usaron para identificar de forma clara y no ambigua los léxicos del lenguaje.
Los patrones para BIN, OCT y HEX son los que hacen que los números solo contengan dígitos válidos.
El token ID es el que hace que los identificadores sigan una estructura válida y no se confundan con números.
Los operadores y paréntesis se definieron con expresiones simples para reconocer bien la estructura de la expresión.
El token ERROR es el que detecta cualquier símbolo no válido y errores léxicos.

Justificación de los casos aceptados y rechazados

Las expresiones aceptadas tienen solo símbolos que coinciden con los patrones definidos entonces pueden ser tokenizadas sin errores.
Las expresiones rechazadas tienen caracteres o combinaciones que no son de ninguna base numérica válida o no cumplen las reglas léxicas, lo que activa el token ERROR.

Estrategia de manejo de errores

El manejo de errores se basa en detectar el primer carácter inválido durante la tokenización.

Al encontrar un token ERROR, el analizador lanza una excepción con un mensaje claro diciendo el símbolo desconocido y esto evita que el análisis continúe y  al igual que la identificación del problema.

Justificación de la gramática regular.

La gramática realizada para dar solución al ejercicio es una combinación de tres gramáticas distintas, una para cada sistema de numeración (binario, octal y hexadecimal). Cada una fue diseñada respetando las restricciones propias de su sistema, particularmente en cuanto al conjunto de símbolos permitidos. De esta manera, se garantiza que las cadenas generadas por la gramática correspondan únicamente a números válidos dentro de cada sistema de numeración.
