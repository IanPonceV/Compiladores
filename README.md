1. FUNCIONAMIENTO DEL CÓDIGO: 

Decidimos armar el programa completo en Python y usamos la librería tkinter para crear una interfaz gráfica que fuera fácil de usar. La idea es que cuando alguien carga un archivo de texto con el código fuente, el programa lo lee letra por letra de principio a fin. Al darle al botón de analizar, nuestro código empieza a agrupar esos caracteres para formar palabras con sentido, que nosotros llamamos tokens, y guarda en qué línea y columna exacta aparecieron. Mientras va leyendo, el programa también va contando los espacios al principio de cada línea para saber si estamos entrando a un bloque de código nuevo, como dentro de un ciclo o condicional, y avisa cuando entramos o salimos de esos bloques. Al final, la interfaz muestra dos cosas: una tabla limpia con todos los tokens válidos que encontró y una consola roja abajo donde avisa si hubo algún error. Además, para cumplir con el entregable, hacemos que el programa guarde automáticamente un archivo .out con la lista de tokens en la misma carpeta donde estaba el archivo original.

2. ANÁLISIS DE LA GRAMÁTICA Y DECISIONES DEL DISEÑO: 

Para que nuestro lenguaje MiniLang pudiera entender cosas básicas como variables, operaciones matemáticas, condicionales y ciclos, tuvimos que armar lo que una Gramática Libre de Contexto. La decisión más importante que tomamos aquí fue escribir las reglas de manera que evitemos la recursividad por la izquierda. También tuvimos mucho cuidado de separar las operaciones matemáticas en distintos niveles. Por ejemplo, pusimos la multiplicación y la división en un grupo más profundo que la suma y la resta, para asegurarnos de que la computadora respete la jerarquía de operaciones de las matemáticas.

A continuación, le compartimos cómo quedó estructurada nuestra gramática:

<Program> ::= <StatementList>
<StatementList> ::= <Statement> <StatementList> | ε
<Statement> ::= <VarDecl> | <Assignment> | <IfStmt> | <WhileStmt> | <FuncDecl> | <FuncCall> | <IOStmt>

<VarDecl> ::= <Type> "ID" "=" <Expression> "NEWLINE"
<Type> ::= "int" | "float" | "string" | "bool"
<Assignment> ::= "ID" "=" <Expression> "NEWLINE"

<IfStmt> ::= "if" <Condition> ":" "NEWLINE" "INDENT" <StatementList> "DEDENT" <ElseClause>
<ElseClause> ::= "else" ":" "NEWLINE" "INDENT" <StatementList> "DEDENT" | ε

<WhileStmt> ::= "while" <Condition> ":" "NEWLINE" "INDENT" <StatementList> "DEDENT"

<FuncDecl> ::= "def" "ID" "(" <ParamList> ")" ":" "NEWLINE" "INDENT" <StatementList> "DEDENT"
<ParamList> ::= <Type> "ID" <MoreParams> | ε
<MoreParams> ::= "," <Type> "ID" <MoreParams> | ε

<FuncCall> ::= "ID" "(" <ArgList> ")" "NEWLINE"
<ArgList> ::= <Expression> <MoreArgs> | ε
<MoreArgs> ::= "," <Expression> <MoreArgs> | ε

<IOStmt> ::= "Read" "(" "ID" ")" "NEWLINE" | "Write" "(" <Expression> ")" "NEWLINE"

<Condition> ::= <Expression> <RelOp> <Expression>
<RelOp> ::= ">" | "<" | "==" | "!=" | ">=" | "<="

<Expression> ::= <Term> <ExprPrime>
<ExprPrime> ::= "+" <Term> <ExprPrime> | "-" <Term> <ExprPrime> | ε
<Term> ::= <Factor> <TermPrime>
<TermPrime> ::= "*" <Factor> <TermPrime> | "/" <Factor> <TermPrime> | "%" <Factor> <TermPrime> | ε
<Factor> ::= "ID" | <Number> | "STRING_LITERAL" | "BOOLEAN_LITERAL" | "(" <Expression> ")"
<Number> ::= "INT" | "FLOAT"

3. EXPRESIONES REGULARES Y REGLAS LÉXICAS: 

Para que el programa supiera reconocer qué parte del texto es un número, qué parte es una variable y qué parte es un símbolo, usamos expresiones regulares, que funcionan como moldes para la búsqueda. Por ejemplo, para encontrar palabras clave usamos un molde que busca palabras exactas como int, float o if. Para los nombres de las variables, le dijimos que busque cualquier palabra que empiece con una letra o guion bajo, aunque luego en el código nos aseguramos de cortarla si se pasa de los 31 caracteres. Para los números, programamos para reconocer secuencias de dígitos normales para los enteros, y secuencias que tengan un punto en medio para los flotantes. Los textos entre comillas los buscamos indicando que agarre todo lo que esté entre dos comillas dobles, y para los operadores como el más, menos o igual, simplemente hicimos que busque esos símbolos exactos. Y por ultimo, le dijimos que si ve un símbolo de numeral, ignore todo lo que sigue en esa línea porque se reconoce como comentario.

A continuación las ecpresiones regulares que utilizamos en el proyecto:

a.Palabras Clave (Keywords)
Expresión: \b(int|float|string|bool|if|else|while|Read|Write|def|return|true|false)\b
Explicación: Usamos \b para estar seguros de que el analizador reconozca la palabra exacta. Así evitamos que si declaramos una variable llamada interior, el programa se confunda y crea que la sílaba "int" es una palabra clave.

b.Identificadores (Variables y nombres de funciones)
Expresión: ^[a-zA-Z_][a-zA-Z0-9_]*$
Explicación: La regla obliga a que el nombre empiece exclusivamente con una letra mayúscula, minúscula o un guion bajo. A partir del segundo carácter, ya permitimos que se incluyan números. En la lógica del código nos aseguramos de limitar esto a un máximo de 31 caracteres para cumplir con la regla del proyecto.

c.Números Enteros (INT)
Expresión: ^[0-9]+$
Explicación: Representa una secuencia continua de uno o más dígitos, sin aceptar puntos ni caracteres especiales.

d.Números Flotantes (FLOAT)
Expresión: ^[0-9]+\.[0-9]+$
Explicación: Obliga a que exista al menos un dígito, seguido estrictamente por un punto decimal y finalizando con al menos otro dígito. Esto nos ayuda a detectar errores si alguien escribe algo como 3. sin decimales.

e.Cadenas de Texto (STRING)
Expresión: ^"[^"\n]*"$
Explicación: Indica que la cadena debe empezar con comillas dobles ". La parte [^"\n]* significa que aceptamos cualquier carácter intermedio siempre y cuando no sea otra comilla doble para no cerrar la cadena antes de tiempo y no sea un salto de línea \n. También debe terminar con comillas dobles.

f.Operadores Aritméticos y Relacionales
Expresión: (==|!=|<=|>=|<|>|=|!|\+|-|\*|/|%)
Explicación: Utilizamos el operador lógico OR | para agrupar todos los símbolos válidos. El código nota que los operadores dobles como == o <= se colocan antes que los simples como = o < en la expresión, esto ayuda que el analizador intente emparejar primero los símbolos compuestos antes de partirlos por error.

g.Símbolos Especiales
Expresión: [\{\}\(\);,:]
Explicación: Es una clase de caracteres que reconoce de forma individual las llaves, los paréntesis, el punto y coma, la coma y los dos puntos, los cuales usamos para la estructura de las funciones y separadores.

h.Comentarios de línea
Expresión: ^#.*
Explicación: Inicia con el símbolo de numeral #. El punto y el asterisco .* le indican al analizador que agrupe absolutamente cualquier carácter que siga después del numeral, ignorándolo hasta que termine la línea actual.

4. DECISIONES CLAVE EN LA IMPLEMENTACIÓN: 

Una de las partes más complicadas fue hacer que el programa entendiera los niveles de sangría, que es cuando empujamos el código hacia la derecha dentro de un bloque condicional y para hacerlo, usamos una pila, empezamos con un nivel cero y cada vez que el programa cambia de línea, cuenta cuántos espacios hay al principio. Si hay más espacios de los que teníamos anotados arriba, metemos un dato nuevo a la pila y avisamos que entramos a un nuevo bloque generando un token INDENT. Si de repente hay menos espacios, empezamos a sacar datos hasta quedar al nivel correcto y generamos tokens DEDENT por cada dato que sacamos.

Otra cosa importante que decidimos fue limpiar los saltos de línea. En lugar de generar un token NEWLINE cada vez que el usuario presiona Enter, el programa ignora las líneas que están totalmente en blanco o que solo tienen comentarios. Solo guardamos un NEWLINE si en la línea anterior de verdad se escribió algo de código útil.

5. MANEJO DE ERRORES:

Sabíamos que el compilador jamás debía cerrarse de golpe si encontraba algo mal escrito. Para solucionar esto, programamos como una especie de modo de recuperación. Si el programa se topa con un símbolo raro que no pertenece al lenguaje, simplemente lo anota en la consola de errores, lo descarta y sigue leyendo la siguiente letra como si nada hubiera pasado.

Si el usuario abre unas comillas para escribir un texto pero se le olvida cerrarlas antes de cambiar de línea, el analizador marca el error, pero nosotros decidimos agregarle la comilla faltante de forma invisible para poder guardar ese texto como un token válido y no perder esa información. Con los nombres de variables que son muy largos, el programa lanza la advertencia, agarra los primeros 31 caracteres, descarta el resto y sigue trabajando con ese pedazo cortado. Y si el usuario escribe un número con punto decimal pero se le olvida poner los decimales después del punto, avisamos del error pero rescatamos la parte entera. Con todo esto nos aseguramos de que el programa sea lo mas resistente a errores, intente adivinar la intención del usuario para rescatar todo lo que pueda, y siga funcionando hasta llegar al final.

