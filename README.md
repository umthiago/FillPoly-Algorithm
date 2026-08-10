# FillPoly — Computação Gráfica

Implementação do algoritmo **FillPoly** utilizando o método **Scanline Fill** para preenchimento de polígonos.

O projeto foi desenvolvido como parte da disciplina de **Computação Gráfica**.

## Integrantes

* Thiago Oliveira Dupim
* Pedro Michalski

## Sobre o projeto

A aplicação permite criar e manipular polígonos em uma interface gráfica.

O preenchimento dos polígonos é realizado por uma implementação própria do algoritmo Scanline Fill, utilizando:

* Edge Table (ET);
* Active Edge Table (AET);
* cálculo das interseções das arestas com as scanlines;
* ordenação das interseções;
* regra Odd-Even;
* aritmética incremental para atualização das coordenadas X.

O preenchimento não utiliza funções prontas de preenchimento de polígonos do Pygame.

## Requisitos

* Windows 10 ou Windows 11
* Python 3.12 ou compatível
* Pygame Community Edition

## Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
```

Entre na pasta do projeto:

```bash
cd SEU-REPOSITORIO
```

Opcionalmente, crie um ambiente virtual:

```bash
python -m venv .venv
```

No Windows PowerShell, ative o ambiente virtual:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

Execute:

```bash
python main.py
```

A aplicação será aberta em uma janela gráfica.

## Controles

| Ação                       | Controle                  |
| -------------------------- | ------------------------- |
| Adicionar vértice          | Clique esquerdo           |
| Finalizar polígono         | ENTER                     |
| Cancelar desenho           | ESC                       |
| Selecionar polígono        | Clique dentro do polígono |
| Excluir polígono           | DELETE                    |
| Mostrar/ocultar arestas    | `Opção`                       |
| Limpar todos os polígonos  | `C`                       |

## Estrutura

```text
.
├── main.py
├── requirements.txt
└── README.md
```

## Algoritmo

O preenchimento é realizado percorrendo a imagem através de scanlines horizontais.

Para cada scanline, as arestas ativas são armazenadas na Active Edge Table. As interseções entre as arestas e a scanline são ordenadas da esquerda para a direita. Os pixels entre cada par de interseções são então preenchidos.

A posição X das interseções é atualizada de forma incremental através de:

```text
x = x + dx
```

evitando o recálculo completo da interseção a cada scanline.

## Disciplina

**Computação Gráfica**

Trabalho acadêmico — Implementação de algoritmo de preenchimento de polígonos.
