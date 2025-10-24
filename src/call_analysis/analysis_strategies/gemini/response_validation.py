from output_schema import CallAnalysisResult


def validate_call_data(data_dict: dict):
    call_analysis = CallAnalysisResult(**data_dict)
