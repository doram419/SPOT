class Data():
    title : str
    desc : list
    summary : str = "생성되지 않음"

    def __init__(self, title, chunked_desc, summary) -> None:
        self.title = title
        self.desc = chunked_desc
        self.summary = summary

    def print_data(self):
        return "Data { title:" + self.title + "desc:" + str(self.desc[0]) + "summary:" + str(self.summary[0]) 
