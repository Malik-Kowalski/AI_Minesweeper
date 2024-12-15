import pandas as pd
import ast

input_file = "game_log.csv"
output_file = "game_log_processed_data.csv"

data = pd.read_csv(input_file)

game_ids_with_win = data[data['Result'] == 'win']['GameID'].unique()
filtered_data = data[data['GameID'].isin(game_ids_with_win)]


def transform_row(row):
    matrix = ast.literal_eval(row['Adjacent3x3'])
    transformed_matrix = []

    for i in range(3):
        for j in range(3):
            value = matrix[i][j]
            if value is None:
                transformed_matrix.append(-3)
            elif value == 'F':
                transformed_matrix.append(-2)
            else:
                transformed_matrix.append(value)

    transformed_matrix[4] = -3

    if row['Result'] in ['win', 'safe']:
        label = 0
    elif row['Result'] == 'AI_flagged':
        label = 1
    else:
        return None

    return transformed_matrix + [label]


transformed_data = filtered_data.apply(transform_row, axis=1)

transformed_data = transformed_data.dropna()

columns = [f'Feature_{i}' for i in range(9)] + ['Label']
output_df = pd.DataFrame(transformed_data.tolist(), columns=columns)

output_df.to_csv(output_file, index=False)
print(f"Przetworzone dane zapisano do pliku: {output_file}")
