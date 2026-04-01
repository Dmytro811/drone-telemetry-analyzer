from src.parser.ardupilot_parser import parse_log
import pandas as pd

def run_pipeline(file_path: str) -> dict:
    result = parse_log(file_path)
    return result