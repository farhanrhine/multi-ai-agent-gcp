import sys

class CustomException(Exception):
    def __init__(self, message: str, error_detail: Exception = None):
        self.error_message = self.get_detailed_error_message(message, error_detail)
        super().__init__(self.error_message)

    @staticmethod
    def get_detailed_error_message(message, error_detail):
        _, _, exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown File"
        line_number = exc_tb.tb_lineno if exc_tb else "Unknown Line"
        
        error_str = f"{message}"
        if error_detail:
            error_str += f" | Error: {str(error_detail)}"
        error_str += f" | File: {file_name} | Line: {line_number}"
        
        return error_str

    def __str__(self):
        return self.error_message