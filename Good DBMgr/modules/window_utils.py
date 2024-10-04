def position_window(parent, window):
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()

    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()

    # 부모 창의 오른쪽에 창 배치
    x = parent_x + parent_width + 10
    y = parent_y  # 부모 창과 같은 높이에 배치

    # 화면 경계를 벗어나지 않도록 조정
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()

    if x + window_width > screen_width:
        # 오른쪽에 공간이 부족하면 왼쪽에 배치
        x = parent_x - window_width - 10

    if y + window_height > screen_height:
        y = screen_height - window_height

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")