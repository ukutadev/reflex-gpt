import reflex as rx
from . import routes

class NavState(rx.State):
    """State for the navigation component."""
    
    # Define any state variables here if needed
    def to_home(self):
        """Navigate to the home page. on click"""
        #print("clicked")
        return rx.redirect(routes.HOME_ROUTE)
    def to_about_us(self):
        """Navigate to the about page. on click"""
        
        return rx.redirect(routes.ABOUT_US_ROUTE)
    def to_chat(self):
        """Navigate to the chat page. on click"""
        
        return rx.redirect(routes.CHAT_ROUTE)

