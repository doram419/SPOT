
"""
웹 크롤링을 통해서 Faiss DB를 만드는 프로그램
"""
import tkinter as tk
from application import Application
# from vectorMgr import saveToVDB, searchVDB
# from logger import vdb_logging
# from tools.metaMgr import print_meta

# def find(region : str = "데이터 크롤링 할 지역",
#          keyword : str = "크롤링 할 단어"):
#     """
#     정보를 찾고, 데이터를 만들어서 반환해주는 함수
#     """
#     infos = start_crawling(keyword=keyword, region=region)
#     infos = make_datas(infos)

#     return infos

# def save(datas : list = "SearchResult list를 주면 DB에 저장하는 함수"):
#     """
#     크롤링한 데이터를 저장하는 함수
#     """
#     for data in datas: 
#         saveToVDB(data=data)

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    app.run()