using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

class Token
{
    public string Tipo { get; set; }
    public string Valor { get; set; }

    public Token(string tipo, string valor)
    {
        Tipo = tipo;
        Valor = valor;
    }

    public override string ToString()
    {
        return $"<{Tipo}, {Valor}>";
    }
}

class Lexer
{
    private static readonly List<(string tipo, string patron)> Tokens =
        new List<(string, string)>
        {
            ("BIN", @"[01]+"),
            ("OCT", @"[0-7]+"),
            ("HEX", @"[0-9A-F]+"),
            ("ID",  @"[a-zA-Z_][a-zA-Z0-9_]*"),
            ("MAS", @"\+"),
            ("MENOS", @"-"),
            ("MUL", @"\*"),
            ("DIV",  @"/"),
            ("PAREND", @"\("),
            ("PARENI", @"\)"),
            ("ESP", @"[ \t\n]+"),
            ("ERR", @".")
        };

    private static readonly Regex MasterRegex =
        new Regex(string.Join("|",
            Tokens.ConvertAll(t => $"(?<{t.tipo}>{t.patron})")
        ));

    public static List<Token> Analyze(string input)
    {
        var resultado = new List<Token>();

        foreach (Match match in MasterRegex.Matches(input))
        {
            foreach (var token in Tokens)
            {
                if (match.Groups[token.tipo].Success)
                {
                    if (token.tipo == "WS")
                        break;

                    if (token.tipo == "ERROR")
                        throw new Exception($"Error léxico: token desconocido '{match.Value}'");

                    resultado.Add(new Token(token.tipo, match.Value));
                    break;
                }
            }
        }

        return resultado;
    }
}

class Program
{
    static void Main()
    {
        string[] tests =
        {
            "(110 * 10) + 1",
            "(5 + 3) * 2",
            "(102 + 1)",
            "(ABC - 9) / 3"
        };

        foreach (string test in tests)
        {
            Console.WriteLine($"\nEntrada: {test}");
            try
            {
                var tokens = Lexer.Analyze(test);

                foreach (var token in tokens)
                    Console.WriteLine(token);

                Console.WriteLine("Salida: Aceptada");
            }
            catch (Exception e)
            {
                Console.WriteLine("Salida: " + e.Message);
            }
        }
    }
}
