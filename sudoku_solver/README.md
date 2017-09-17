# soduku_solver

Solve soduku via DLX.

## Building

```console
$ make
```

## Usage

Usage: `./sudoku_sover [-v] [inputfile]`

Example:

```console
$ ./sudoku_solver -v hardest_sudoku.txt
input sudoku:
+-------+-------+-------+
| 8 0 0 | 0 0 0 | 0 0 0 |
| 0 0 3 | 6 0 0 | 0 0 0 |
| 0 7 0 | 0 9 0 | 2 0 0 |
+-------+-------+-------+
| 0 5 0 | 0 0 7 | 0 0 0 |
| 0 0 0 | 0 4 5 | 7 0 0 |
| 0 0 0 | 1 0 0 | 0 3 0 |
+-------+-------+-------+
| 0 0 1 | 0 0 0 | 0 6 8 |
| 0 0 8 | 5 0 0 | 0 1 0 |
| 0 9 0 | 0 0 0 | 4 0 0 |
+-------+-------+-------+
dlx_search return 60:
+-------+-------+-------+
| 8 1 2 | 7 5 3 | 6 4 9 |
| 9 4 3 | 6 8 2 | 1 7 5 |
| 6 7 5 | 4 9 1 | 2 8 3 |
+-------+-------+-------+
| 1 5 4 | 2 3 7 | 8 9 6 |
| 3 6 9 | 8 4 5 | 7 2 1 |
| 2 8 7 | 1 6 9 | 5 3 4 |
+-------+-------+-------+
| 5 2 1 | 9 7 4 | 3 6 8 |
| 4 3 8 | 5 2 6 | 9 1 7 |
| 7 9 6 | 3 1 8 | 4 5 2 |
+-------+-------+-------+
```

It can accept one line description of the sudoku input like this:

> 800000000003600000070090200050007000000045700000100030001000068008500010090000400


```console
$ echo "8000000000036000000700902000500070000000457000001000300010000680085000100900004"|./sudoku_solver -v
input sudoku:
+-------+-------+-------+
| 8 0 0 | 0 0 0 | 0 0 0 |
| 0 0 3 | 6 0 0 | 0 0 0 |
| 0 7 0 | 0 9 0 | 2 0 0 |
+-------+-------+-------+
| 0 5 0 | 0 0 7 | 0 0 0 |
| 0 0 0 | 0 4 5 | 7 0 0 |
| 0 0 0 | 1 0 0 | 0 3 0 |
+-------+-------+-------+
| 0 0 1 | 0 0 0 | 0 6 8 |
| 0 0 8 | 5 0 0 | 0 1 0 |
| 0 9 0 | 0 0 0 | 4 0 0 |
+-------+-------+-------+
dlx_search return 60:
+-------+-------+-------+
| 8 1 2 | 7 5 3 | 6 4 9 |
| 9 4 3 | 6 8 2 | 1 7 5 |
| 6 7 5 | 4 9 1 | 2 8 3 |
+-------+-------+-------+
| 1 5 4 | 2 3 7 | 8 9 6 |
| 3 6 9 | 8 4 5 | 7 2 1 |
| 2 8 7 | 1 6 9 | 5 3 4 |
+-------+-------+-------+
| 5 2 1 | 9 7 4 | 3 6 8 |
| 4 3 8 | 5 2 6 | 9 1 7 |
| 7 9 6 | 3 1 8 | 4 5 2 |
+-------+-------+-------+
```

or the inputfile like this:

> 800000000    
> 003600001    
> 070090200    
> 050007000    
> 000045700    
> 000100030    
> 001000068    
> 008500010    
> 090000400    

