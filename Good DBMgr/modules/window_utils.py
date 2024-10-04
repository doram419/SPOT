

def position_window(parent, window):
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # 부모 창의 오른쪽에 창 배치
    x = parent_x + parent_width + 10
    y = parent_y + (parent_height - window_height) // 2 - 100

    # 화면 경계를 벗어나지 않도록 조정
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()

    if x + window_width > screen_width:
        # 오른쪽에 공간이 부족하면 왼쪽에 배치
        x = parent_x - window_width - 10

    if y + window_height > screen_height:
        y = screen_height - window_height

    window.geometry(f"+{x}+{y}")
