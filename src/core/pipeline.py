from src.parser.ardupilot_parser import parse_log

def parse_log(file_path: str, use_mock=True) -> pd.DataFrame:
    if use_mock:
        return generate_mock()
    else:
        return real_parse(file_path)

df = parse_log("fake.bin")
print(df.head())
print(df.shape)