
# rdtpy: run R data.table expression on Python Pandas DataFrame

This module enables runs R data.table style expressions on Python DataFrames.
Why?
Perhaps you love succinct R data.table syntax and fail to navigate syntax of
Pandas DataFrame in which obviously simple can get
[complicated](https://stackoverflow.com/questions/23377108/pandas-percentage-of-total-with-groupby)
(answers miss the best solution, which in itself tells about Pandas syntax).

This module defines a function `rdt` with two arguments:

  * Pandas DataFrame which can be converted to R data.frame.
  * Any string expression `<EXPR>` that you can give to R data.table `dt`
    like `dt[ <EXPR> ] `.

## Examples

Pandas DataFrame `df` has columns region, country, and sales.
Calculate percentage of total sales by country grouped by region:

    result = rdt(df, ', of_total := sales/sum(sales), by="region"')

Self-contained example:

    import pandas as pd
    from rdtpy import rdt
    df = pd.DataFrame({"x": [1,2,3], "y": ["a", "b", "c"]})
    result1 = rdt(df, 'y>"a", sum(x)')
    result2 = rdt(df, ', .(xs=sum(x)), by="y"')

How to define new R function to use in expressions:

    import rpy2
    rpy2.robjects.r("fun <- function(x) {median(x)}")
    result3 = rdt(df, ', fun(x)')

## Installation

## Reason not to use this module

  * `rdtpy` depends on `rpy2` which depends on `R`.
    Both need to be installed and maintained.
  * `rdt` conversion of Pandas DataFrame to R data.table is not super 
    efficient, so with humongous data sets you may face issues.

