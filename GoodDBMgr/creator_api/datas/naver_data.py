class NaverData():
    title : str
    address : str
    content : str
    link : str

    def __init__(self, title, address, content, link):
        self.title = title
        self.address = address
        self.content = content
        self.link = link

    def print_data(self):
        return "NaverData { title:" + self.title + "address:" + self.address + \
            "link:" + self.link + "content:" + self.content + " }"