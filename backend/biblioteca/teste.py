from biblioteca import Biblioteca

bib = Biblioteca(
    "https://biblioteca.barbacena.ifsudestemg.edu.br",
    conectar=True,
)

for livro in bib.buscar(titulo="java", limite=5):
    print(livro)