import reflex as rx
from reflex_gpt.ui.navbar import base_navbar
from .footer import base_footer

def base_layout(*args,**kwargs) -> rx.Component:
    """Base layout for the app."""
    return rx.container(
        #rx.heading("Reflex GPT App", size="6")
        #base_navbar("Reflex to our GPT App", size="6"),
        base_navbar(),
        rx.fragment(
            *args,
            **kwargs
        ),
        base_footer()
        
        
    )