import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os

# ==========================================
# 1. TIPOS DE TOKEN Y CLASES
# ==========================================

class TipoToken:
    # Palabras Clave
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    BOOL = 'BOOL'
    VOID = 'VOID'
    RETURN = 'RETURN'
    DEF = 'DEF'        # Agregado para funciones
    READ = 'READ'
    WRITE = 'WRITE'
    
    # Literales e Identificadores
    ID = 'ID'
    NUMERO_ENTERO = 'NUMERO_ENTERO'
    NUMERO_FLOTANTE = 'NUMERO_FLOTANTE'
    CADENA_LITERAL = 'CADENA_LITERAL'
    BOOLEANO_LITERAL = 'BOOLEANO_LITERAL' # Para true/false
    
    # Operadores y Símbolos
    SUMA = '+'
    RESTA = '-'
    MULTIPLICACION = '*'
    DIVISION = '/'
    MODULO = '%'
    MAYOR_QUE = '>'
    MENOR_QUE = '<'
    MAYOR_IGUAL = '>='
    MENOR_IGUAL = '<='
    IGUAL_QUE = '=='
    DIFERENTE_QUE = '!='
    ASIGNACION = '='
    PARENTESIS_IZQ = '('
    PARENTESIS_DER = ')'
    LLAVE_IZQ = '{'
    LLAVE_DER = '}'
    DOS_PUNTOS = ':'
    COMA = ','
    PUNTO_Y_COMA = ';'
    
    # Control
    NUEVA_LINEA = 'NEWLINE'
    INDENTAR = 'INDENT'
    DESINDENTAR = 'DEDENT'
    FIN_ARCHIVO = 'EOF'
    DESCONOCIDO = 'UNKNOWN'

class Token:
    def __init__(self, tipo, valor, linea, col_inicio, col_fin):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.col_inicio = col_inicio
        self.col_fin = col_fin

    def __str__(self):
        # Formato para el archivo .out: <ID> line 1, col 1-5: 'variable'
        if self.tipo in [TipoToken.NUEVA_LINEA, TipoToken.INDENTAR, TipoToken.DESINDENTAR, TipoToken.FIN_ARCHIVO]:
             return f"<{self.tipo}> line {self.linea}, col {self.col_inicio}-{self.col_fin}"
        return f"<{self.tipo}> line {self.linea}, col {self.col_inicio}-{self.col_fin}: '{self.valor}'"

class ErrorLexico:
    def __init__(self, linea, columna, mensaje):
        self.linea = linea
        self.columna = columna
        self.mensaje = mensaje

    def __str__(self):
        # Formato: line , col : ERROR
        return f"line {self.linea}, col {self.columna}: ERROR {self.mensaje}"

# ==========================================
# 2. ANALIZADOR LÉXICO
# ==========================================

class AnalizadorLexico:
    def __init__(self, codigo_fuente):
        # Normalizar saltos de línea y asegurar terminación
        self.fuente = codigo_fuente.replace('\r\n', '\n') + '\n'
        self.longitud = len(self.fuente)
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        
        # Pila de indentación (Nivel 0 inicial)
        self.pila_indentacion = [0] 
        
        self.tokens = []
        self.errores = []
        
        # Mapa de palabras reservadas
        self.palabras_clave = {
            "if": TipoToken.IF, "else": TipoToken.ELSE, "while": TipoToken.WHILE,
            "int": TipoToken.INT, "float": TipoToken.FLOAT, "string": TipoToken.STRING,
            "bool": TipoToken.BOOL, "void": TipoToken.VOID, "return": TipoToken.RETURN,
            "def": TipoToken.DEF, "Read": TipoToken.READ, "Write": TipoToken.WRITE,
            "true": TipoToken.BOOLEANO_LITERAL, "false": TipoToken.BOOLEANO_LITERAL
        }

    def analizar(self):
        inicio_de_linea = True # Chequeo para verificar indentación

        while self.posicion < self.longitud:
            caracter = self.fuente[self.posicion]

            # ------------------------------------------------
            # 1. MANEJO DE INDENTACIÓN (Solo tras NEWLINE o inicio)
            # ------------------------------------------------
            if inicio_de_linea:
                # Si es línea vacía (solo enter), lo pasamos
                if caracter == '\n':
                    self.posicion += 1
                    self.linea += 1
                    self.columna = 1
                    continue
                
                # Si es comentario al inicio de línea, se ignora toda la línea
                if caracter == '#':
                    self.saltar_comentario()
                    continue
                
                # Calcular indentación (espacios y tabs)
                if caracter.isspace():
                    espacios = self.contar_indentacion()
                    # Verificar si la línea tiene contenido real después de los espacios
                    if self.posicion < self.longitud and self.fuente[self.posicion] not in ['\n', '#']:
                        self.procesar_indentacion(espacios)
                        inicio_de_linea = False
                    continue
                else:
                    # Nivel 0 de indentación (sin espacios al inicio)
                    self.procesar_indentacion(0)
                    inicio_de_linea = False
            
            # ------------------------------------------------
            # 2. ESPACIOS EN BLANCO (No al inicio)
            # ------------------------------------------------
            if caracter.isspace():
                if caracter == '\n':
                    # Emitir NEWLINE si la línea tuvo contenido previo válido
                    self.tokens.append(Token(TipoToken.NUEVA_LINEA, "\\n", self.linea, self.columna, self.columna))
                    self.posicion += 1
                    self.linea += 1
                    self.columna = 1
                    inicio_de_linea = True
                else:
                    self.posicion += 1
                    self.columna += 1
                continue

            # ------------------------------------------------
            # 3. COMENTARIOS (En medio de línea)
            # ------------------------------------------------
            if caracter == '#':
                self.saltar_comentario()
                continue 

            # ------------------------------------------------
            # 4. IDENTIFICADORES Y PALABRAS CLAVE
            # ------------------------------------------------
            if caracter.isalpha() or caracter == '_':
                self.escanear_identificador()
                continue

            # ------------------------------------------------
            # 5. NÚMEROS (Enteros y Flotantes)
            # ------------------------------------------------
            if caracter.isdigit():
                self.escanear_numero()
                continue

            # ------------------------------------------------
            # 6. CADENAS (STRINGS)
            # ------------------------------------------------
            if caracter == '"':
                self.escanear_cadena()
                continue

            # ------------------------------------------------
            # 7. OPERADORES Y SÍMBOLOS
            # ------------------------------------------------
            if self.escanear_operador(caracter):
                continue

            # ------------------------------------------------
            # 8. ERROR: CARÁCTER DESCONOCIDO
            # ------------------------------------------------
            self.errores.append(ErrorLexico(self.linea, self.columna, f"Carácter inesperado '{caracter}'"))
            self.posicion += 1
            self.columna += 1

        # AL FINAL DEL ARCHIVO (EOF): Cerrar bloques pendientes
        while len(self.pila_indentacion) > 1:
            self.pila_indentacion.pop()
            self.tokens.append(Token(TipoToken.DESINDENTAR, "", self.linea, self.columna, self.columna))
        
        # Opcional: token EOF
        # self.tokens.append(Token(TipoToken.FIN_ARCHIVO, "", self.linea, self.columna, self.columna))
        
        return self.tokens, self.errores

    def contar_indentacion(self):
        contador = 0
        pos_temporal = self.posicion
        
        # Calcular espacios (Tabs = 4 espacios estándar)
        while pos_temporal < self.longitud and self.fuente[pos_temporal] in [' ', '\t']:
            if self.fuente[pos_temporal] == '\t':
                contador += 4
            else:
                contador += 1
            pos_temporal += 1
        
        # Ajustar posición real del puntero
        chars_consumidos = pos_temporal - self.posicion
        self.posicion = pos_temporal
        self.columna += chars_consumidos
        return contador

    def procesar_indentacion(self, espacios):
        nivel_actual = self.pila_indentacion[-1]
        
        if espacios > nivel_actual:
            # Aumenta nivel -> INDENT
            self.pila_indentacion.append(espacios)
            self.tokens.append(Token(TipoToken.INDENTAR, "", self.linea, 1, espacios))
        
        elif espacios < nivel_actual:
            # Disminuye nivel -> DEDENT(s)
            while espacios < self.pila_indentacion[-1]:
                self.pila_indentacion.pop()
                self.tokens.append(Token(TipoToken.DESINDENTAR, "", self.linea, 1, espacios))
                if len(self.pila_indentacion) == 0: 
                    self.pila_indentacion.append(0)
                    break
            
            # Error de Indentación: Si bajó pero no coincidió con ningún nivel previo
            if self.pila_indentacion[-1] != espacios:
                self.errores.append(ErrorLexico(self.linea, 1, "Indentación inválida (no coincide con niveles previos)"))
                # Recuperación: forzar el nivel al más cercano (ya hecho por el while)

    def saltar_comentario(self):
        # Ignorar hasta el salto de línea, pero NO consumir el \n (para que el loop principal lo vea)
        while self.posicion < self.longitud and self.fuente[self.posicion] != '\n':
            self.posicion += 1

    def escanear_identificador(self):
        col_inicio = self.columna
        pos_inicio = self.posicion
        
        while self.posicion < self.longitud and (self.fuente[self.posicion].isalnum() or self.fuente[self.posicion] == '_'):
            self.posicion += 1
            self.columna += 1
        
        lexema = self.fuente[pos_inicio:self.posicion]
        
        # Validación longitud máxima 31
        if len(lexema) > 31:
            self.errores.append(ErrorLexico(self.linea, col_inicio, "Identificador excede 31 caracteres (truncado)"))
            lexema = lexema[:31] # Truncar identificador

        tipo_token = self.palabras_clave.get(lexema, TipoToken.ID)
        
        # Caso especial: true/false son literales booleanos, no palabras clave de control
        if lexema in ["true", "false"]:
            tipo_token = TipoToken.BOOLEANO_LITERAL

        self.tokens.append(Token(tipo_token, lexema, self.linea, col_inicio, self.columna - 1))

    def escanear_numero(self):
        col_inicio = self.columna
        pos_inicio = self.posicion
        es_flotante = False
        
        # Parte entera
        while self.posicion < self.longitud and self.fuente[self.posicion].isdigit():
            self.posicion += 1
            self.columna += 1
            
        # Parte decimal
        if self.posicion < self.longitud and self.fuente[self.posicion] == '.':
            es_flotante = True
            self.posicion += 1
            self.columna += 1
            
            # Verificar digitos tras el punto
            if self.posicion >= self.longitud or not self.fuente[self.posicion].isdigit():
                 self.errores.append(ErrorLexico(self.linea, self.columna, "Número flotante mal formado (se esperaba dígito tras punto)"))
            
            while self.posicion < self.longitud and self.fuente[self.posicion].isdigit():
                self.posicion += 1
                self.columna += 1
        
        lexema = self.fuente[pos_inicio:self.posicion]
        tipo = TipoToken.NUMERO_FLOTANTE if es_flotante else TipoToken.NUMERO_ENTERO
        self.tokens.append(Token(tipo, lexema, self.linea, col_inicio, self.columna - 1))

    def escanear_cadena(self):
        col_inicio = self.columna
        self.posicion += 1; self.columna += 1 # Comilla inicial
        pos_inicio_contenido = self.posicion
        
        while self.posicion < self.longitud and self.fuente[self.posicion] != '"' and self.fuente[self.posicion] != '\n':
            self.posicion += 1
            self.columna += 1
            
        if self.posicion >= self.longitud or self.fuente[self.posicion] == '\n':
            # Error: String sin cerrar antes de fin de línea
            self.errores.append(ErrorLexico(self.linea, col_inicio, "Cadena sin cerrar antes de fin de línea"))
            lexema = self.fuente[pos_inicio_contenido:self.posicion]
            # Recuperamos emitiendo el token hasta donde llegó
            self.tokens.append(Token(TipoToken.CADENA_LITERAL, lexema + '"', self.linea, col_inicio, self.columna - 1))
            return

        lexema = self.fuente[pos_inicio_contenido:self.posicion]
        self.posicion += 1; self.columna += 1 # Comilla cierre
        self.tokens.append(Token(TipoToken.CADENA_LITERAL, lexema + '"', self.linea, col_inicio, self.columna - 1))

    def escanear_operador(self, caracter):
        col_inicio = self.columna
        siguiente_char = self.fuente[self.posicion + 1] if self.posicion + 1 < self.longitud else ''
        
        # Mapeo de operadores dobles
        dobles = {
            '>=': TipoToken.MAYOR_IGUAL, '<=': TipoToken.MENOR_IGUAL, 
            '==': TipoToken.IGUAL_QUE, '!=': TipoToken.DIFERENTE_QUE
        }
        # Mapeo de operadores simples
        simples = {
            '+': TipoToken.SUMA, '-': TipoToken.RESTA, '*': TipoToken.MULTIPLICACION, '/': TipoToken.DIVISION,
            '%': TipoToken.MODULO, '(': TipoToken.PARENTESIS_IZQ, ')': TipoToken.PARENTESIS_DER, 
            '{': TipoToken.LLAVE_IZQ, '}': TipoToken.LLAVE_DER, ';': TipoToken.PUNTO_Y_COMA, 
            ',': TipoToken.COMA, ':': TipoToken.DOS_PUNTOS,
            '>': TipoToken.MAYOR_QUE, '<': TipoToken.MENOR_QUE, '=': TipoToken.ASIGNACION
        }

        # Intentar coincidencia doble primero (ej: ==)
        combinacion = caracter + siguiente_char
        if combinacion in dobles:
            self.tokens.append(Token(dobles[combinacion], combinacion, self.linea, col_inicio, col_inicio + 2))
            self.posicion += 2
            self.columna += 2
            return True
        
        # Intentar coincidencia simple (ej: =)
        if caracter in simples:
            self.tokens.append(Token(simples[caracter], caracter, self.linea, col_inicio, col_inicio + 1))
            self.posicion += 1
            self.columna += 1
            return True
            
        return False

# ==========================================
# 3. INTERFAZ GRÁFICA 
# ==========================================

class InterfazMiniLang:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Compilador MiniLang 2026 - Analizador Léxico")
        self.raiz.geometry("1000x700")
        self.archivo_actual = None
        
        # Configuración de estilos
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure("Treeview", font=('Consolas', 10), rowheight=25)
        estilo.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

        # --- Frame Principal ---
        frame_principal = tk.Frame(raiz, bg="#f0f0f0")
        frame_principal.pack(fill=tk.BOTH, expand=True)

        # --- Barra de Herramientas ---
        frame_botones = tk.Frame(frame_principal, bg="#e0e0e0", pady=5)
        frame_botones.pack(fill=tk.X)
        
        self.btn_cargar = tk.Button(frame_botones, text="Cargar Archivo (.mlng)", command=self.cargar_archivo, 
                                    bg="#ffffff", relief=tk.GROOVE, padx=10)
        self.btn_cargar.pack(side=tk.LEFT, padx=10)
        
        self.btn_analizar = tk.Button(frame_botones, text="Ejecutar Análisis", command=self.ejecutar_analisis, 
                                      bg="#dddddd", relief=tk.GROOVE, padx=10)
        self.btn_analizar.pack(side=tk.LEFT, padx=10)

        # --- Paneles Divididos ---
        paneles = tk.PanedWindow(frame_principal, orient=tk.HORIZONTAL, bg="#f0f0f0", sashwidth=5)
        paneles.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. Panel Izquierdo: Editor
        frame_izq = tk.LabelFrame(paneles, text="Entrada (Código Fuente)", font=('Segoe UI', 10, 'bold'), bg="#f0f0f0")
        self.txt_entrada = scrolledtext.ScrolledText(frame_izq, font=('Consolas', 11), undo=True, width=40)
        self.txt_entrada.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        paneles.add(frame_izq)

        # 2. Panel Derecho: Tabla de Tokens
        frame_der = tk.LabelFrame(paneles, text="Salida (Lista de Tokens)", font=('Segoe UI', 10, 'bold'), bg="#f0f0f0")
        
        columnas = ("linea", "col", "tipo", "valor")
        self.tabla = ttk.Treeview(frame_der, columns=columnas, show="headings", selectmode="browse")
        
        self.tabla.heading("linea", text="Lín")
        self.tabla.heading("col", text="Col")
        self.tabla.heading("tipo", text="Tipo")
        self.tabla.heading("valor", text="Valor")
        
        self.tabla.column("linea", width=40, anchor=tk.CENTER)
        self.tabla.column("col", width=60, anchor=tk.CENTER)
        self.tabla.column("tipo", width=120)
        self.tabla.column("valor", width=150)
        
        scroll_y = ttk.Scrollbar(frame_der, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscroll=scroll_y.set)
        
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        paneles.add(frame_der)

        # --- Consola de Errores ---
        frame_errores = tk.LabelFrame(frame_principal, text="Errores Léxicos", font=('Segoe UI', 10, 'bold'), fg="red", bg="#f0f0f0")
        frame_errores.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.txt_errores = tk.Text(frame_errores, height=6, font=('Consolas', 10), bg="#fff5f5")
        self.txt_errores.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos MiniLang", "*.mlng *.ming *.txt"), ("Todos", "*.*")])
        if ruta:
            self.archivo_actual = ruta
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.txt_entrada.delete(1.0, tk.END)
                    self.txt_entrada.insert(tk.END, contenido)
                self.raiz.title(f"Compilador MiniLang - {os.path.basename(ruta)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def ejecutar_analisis(self):
        # Limpiar resultados previos
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.txt_errores.config(state=tk.NORMAL)
        self.txt_errores.delete(1.0, tk.END)

        codigo = self.txt_entrada.get(1.0, tk.END)
        
        # Instanciar y ejecutar
        escanner = AnalizadorLexico(codigo)
        tokens, errores = escanner.analizar()

        # Mostrar Tokens
        contenido_salida = []
        for t in tokens:
            valores_fila = (t.linea, f"{t.col_inicio}-{t.col_fin}", t.tipo, t.valor)
            self.tabla.insert("", tk.END, values=valores_fila)
            contenido_salida.append(str(t))

        # Mostrar Errores
        if errores:
            self.txt_errores.insert(tk.END, f"Se encontraron {len(errores)} errores:\n")
            for err in errores:
                self.txt_errores.insert(tk.END, str(err) + "\n")
        else:
            self.txt_errores.insert(tk.END, "Análisis completado sin errores léxicos.")
        
        self.txt_errores.config(state=tk.DISABLED)

        # Generar archivo .out
        self.guardar_salida(contenido_salida)

    def guardar_salida(self, lineas_tokens):
        nombre_salida = "salida.out"
        if self.archivo_actual:
            nombre_base = os.path.splitext(self.archivo_actual)[0]
            nombre_salida = nombre_base + ".out"
        
        try:
            with open(nombre_salida, "w", encoding='utf-8') as f:
                f.write("\n".join(lineas_tokens))
            messagebox.showinfo("Proceso Terminado", f"Archivo generado exitosamente:\n{nombre_salida}")
        except Exception as e:
            messagebox.showerror("Error de Guardado", f"No se pudo crear el archivo .out: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazMiniLang(root)

    root.mainloop()

