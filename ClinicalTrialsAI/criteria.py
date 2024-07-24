import pandas as pd
import json

def load_and_process_criteria(file_path):
    df = pd.read_csv(file_path, delimiter='`')
    df.fillna('', inplace=True)
    df['inclusion_criteria'] = df['inclusion_criteria'].transform(lambda x: x.split('\n'))
    df['exclusion_criteria'] = df['exclusion_criteria'].transform(lambda x: x.split('\n'))
    return json.loads(df.to_json(orient='records', lines=False))
