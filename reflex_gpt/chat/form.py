import reflex as rx

from .state import ChatState

def chat_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.text_area(
                name="message",
                placeholder="Your Message",
                required=True,
                width="100",
            ),
            rx.button('Submit', type='submit'),
            rx.cond(
                ChatState.did_submit,
                rx.text("Form submitted successfully!"),
                #rx.text("Fill out the form and submit it.")
                rx.fragment()#for empty value,
            
            )
            ),
            on_submit=ChatState.handle_submit,
            reset_on_submit=True
        )
    