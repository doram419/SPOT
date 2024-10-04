import tkinter as tk

def button_click():
    print("버튼이 클릭되었습니다!")

# 메인 윈도우 생성
root = tk.Tk()
root.title("Tkinter 버튼 예제")
root.geometry("300x200")  # 윈도우 크기 설정

# 버튼 생성
button = tk.Button(root, text="클릭하세요", command=button_click)
button.pack(expand=True)

# 메인 이벤트 루프 실행
root.mainloop()