class NaverData:
    content: str
    vectorized_content: str
    link: str
    ocr_results: list

    def __init__(self, content, link, ocr_results=None):
        self.content = content
        self.link = link
        self.ocr_results = ocr_results if ocr_results else []

    def print_data(self):
        return f"NaverData {{ link: {self.link}, content: {self.content}, ocr_results: {self.ocr_results} }}"
