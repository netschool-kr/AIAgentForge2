from reflex.experimental import ClientStateVar
import reflex as rx

# "active_tab"이라는 이름으로 초기값이 0인 클라이언트 상태 변수 생성
active_tab = ClientStateVar.create("active_tab", 0)

def tab_component():
    tabs = ["Home", "Profile", "Settings"]
    return rx.hstack(
        rx.foreach(
            tabs,
            lambda tab_name, index: rx.button(
                tab_name,
                # 클릭 시 active_tab의 값을 해당 버튼의 인덱스로 즉시 변경
                on_click=active_tab.set_value(index),
                # active_tab의 현재 값(.value)에 따라 스타일을 동적으로 변경
                bg=rx.cond(active_tab.value == index, "blue.500", "gray.200"),
            )
        )
    )
