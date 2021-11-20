import aiomysql
import tokens


class Queries:
    def __init__(self, loop):
        self.pool_kwargs = {
            "db": tokens.DB_NAME,
            "host": tokens.HOST,
            "port": tokens.PORT,
            "user": tokens.USER,
            "password": tokens.PASSWORD,
            "loop": loop
        }

    async def execute(self, query: str, result=True, commit=False, args=None, as_dict=True):
        if as_dict:
            conn_args = (aiomysql.DictCursor,)
        else:
            conn_args = ()
        if not args:
            args = []
        r = None

        pool = await aiomysql.create_pool(**self.pool_kwargs)
        async with pool.acquire() as conn:
            async with conn.cursor(*conn_args) as cursor:
                await cursor.execute(query, args)
                if result:
                    r = await cursor.fetchall()
                if commit:
                    await conn.commit()
        pool.close()
        await pool.wait_closed()
        return r

    def __process_literals(self, optype, keyvals, literals):
        """ Processes literals and returns a tuple containing all data required for the query
        Args:
            keyvals (dict): Data to insert into the table
            literals (list): Datapoints that should not be escaped
            optype (str): Type of operation
        Returns (tuple):
            (Column names, Column Substitutions, Column Values, Literal Values, OnDuplicate)
        """
        column_names = []
        column_substituion = []
        column_values = []
        literal_values = []
        ondupe_out = []
        for key, value in keyvals.items():
            if type(value) is list and optype not in ["DELETE", "UPDATE"]:
                raise Exception("Unable to process a list in key %s" % key)
            column_names += [key]
            # Determine the type of data to insert
            sub_op = "%%s"
            if key in literals:
                sub_op = "%s"
            # Number of times to repeat
            num_times = 1
            if type(value) is list:
                num_times = len(value)
            column_substituion += [",".join(sub_op for _ in range(0, num_times))]
            # Add to the entries
            if key in literals:
                if type(value) is list:
                    literal_values += value
                else:
                    literal_values += [value]
            else:
                if type(value) is list:
                    column_values += value
                else:
                    column_values += [value]
        for key, value in keyvals.items():
            if optype == "ON DUPLICATE":
                tmp_value = "`%s` = %%s" % key
                if key in literals:
                    tmp_value = tmp_value % value
                else:
                    column_values += [value]
                ondupe_out += [tmp_value]
        return (column_names, column_substituion, column_values, literal_values, ondupe_out)

    async def insert(self, table, keyvals, literals=None, optype="ON DUPLICATE"):
        """ Auto-inserts into a table and handles all escaping
        optypes = ["INSERT", "REPLACE", "INSERT IGNORE", "ON DUPLICATE"]
        Args:
            table (str): Table to run the query against
            keyvals (dict): Data to insert into the table
            literals (list): Datapoints that should not be escaped
            optype (str): Type of operation.  Valid operations are ["INSERT", "REPLACE", "INSERT IGNORE",
                "ON DUPLICATE"]
        Returns (int):
            Primary key for the row
        """
        if literals is None:
            literals = []
        optype = optype.upper()
        parsed_literals = self.__process_literals(optype, keyvals, literals)
        (column_names, column_substituion, column_values, literal_values, ondupe_out) = parsed_literals
        ondupe_values = []
        inital_type = optype
        if optype == "ON DUPLICATE":
            inital_type = "INSERT"
        if inital_type in ["INSERT", "REPLACE"]:
            inital_type += " INTO"
        rownames = ",".join("`%s`" % k for k in column_names)
        rowvalues = ", ".join(k for k in column_substituion)
        query = "%s %s\n" \
                "(%s)\n" \
                "VALUES(%s)" % (inital_type, table, rownames, rowvalues) % tuple(literal_values)
        if optype == "ON DUPLICATE":
            dupe_out = ",\n".join("%s" % k for k in ondupe_out)
            query += "\nON DUPLICATE KEY UPDATE\n" \
                     "%s" % dupe_out
            column_values += ondupe_values

        await self.execute(query, args=column_values, result=False, commit=True)
