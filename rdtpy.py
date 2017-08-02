import pandas as pd
import rpy2
from rpy2.robjects import r, pandas2ri

""" run R data.table expression on Pandas DataFrame

Example:
    df = pd.DataFrame({"x": [1,2,3], "y": ["a", "b", "c"]})
    result1 = rdt(df, 'y>"a", sum(x)')
    result2 = rdt(df, ', .(xs=sum(x)), by="y"')

Issues:
    rpy2 converts Pandas string type columns to factors, which breaks 
    behavior on them. Hence, this code does potentially expensive conversion 
    from factor columns to strings.
"""

# need to do this:
pandas2ri.activate()

def get_rdt_r_function():
    """ get R function to run a R data.table expression on R data.frame
    Returns:
        rpy2 function with arguments:
            df: R data.frame
            expr: expression that can be evaluated in data.table, 
                anything that fits in dt[ <EXPR> ] where dt is data.table.
        which returns:
            df converted to data.table and run with expr
    """
    # add to R namespace a function to fix a BUG in rpy2 in which string
    # columns are converted to factor columns
    rpy2.robjects.r("""
        fix_broken_column_types <- function(dt) {
            dt <- copy(dt)
            for( i in 1:ncol(dt) ) {
                if(is.factor( dt[[i]] )) {
                    dt[[i]] <- as.character( dt[[i]] )
                }
            }
            return( dt )
        }
    """)
    # create R function to run data.table expression on data.frame
    rdt_code = """
        function(df, expr) {
            # convert data.frame to data.table
            require(data.table)
            dt = as.data.table(df)
            # fix
            dt = fix_broken_column_types(dt)
            # create full expr to evaluate
            expr_full <- paste0("dt[", expr, "]")
            result <- eval(parse(text=expr_full))
            if("data.table" %in% class(result)) {
                result = as.data.frame(result)
            }
            return( result )
        }
    """
    return rpy2.robjects.r(rdt_code)

def get_df_to_r_dt_function():
    """ internal utility for debugging: function to return rpy2 data.table
    """
    code = """
        function(df) {
            # convert data.frame to data.table
            require(data.table)
            dt = as.data.table(df)
            return( dt )
        }
    """
    return rpy2.robjects.r(code)

def rdt(df, expr):
    """ execute R style expression on pandas DataFrame

    Args:
        df: pandas DataFrame
        expr: string expression such as 
        'region=="Europe", sales_fraction := sales / sum(sales), by="country"'
        which conforms to R data.table syntax data.table[WHERE, EXPR, GROUPBY]

    Returns:
        pandas DataFrame which is result of converting df to R data.table and
        running expr
        df[eval(parse(text=expr))]
        This result can be either:
            a scalar if expr such as ", sum(sales)" is used
            pandas DataFrame for more complicated operations
        Note that in contrast to R data.table operations, rdt operations are not in-place
    """
    # check input types
    if not type(df) is pd.core.frame.DataFrame:
        raise TypeError("df should be pandas DataFrame")
    if not type(expr) is str:
        raise TypeError("expr should be string expression")
    # get R function to run expr on df
    rdt_r_function = get_rdt_r_function()
    r_df = pandas2ri.py2ri(df)
    r_result = rdt_r_function(df, expr)
    # convert back to Python structure
    result = pandas2ri.ri2py(r_result)
    # convert array of length 1 to scalar to conform to R semantics
    if len(result) == 1 and not ( type(result) is pd.core.frame.DataFrame ):
        result = result[0]
    return result

