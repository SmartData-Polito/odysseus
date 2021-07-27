def get_idx_col_from_value(df, value):
    """ Get index positions of value in dataframe """
    list_of_pos = list()
    result = df.isin([value])
    series_obj = result.any()
    column_names = list(series_obj[series_obj].index)
    for col in column_names:
        rows = list(result[col][result[col]].index)
        for row in rows:
            list_of_pos.append((row, col))
    return list_of_pos
