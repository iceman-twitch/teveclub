import base64

class icon:
    def Get(self):
        ICON__BASE64 = ICON_BASE64 = """AAABAAEAEBAQAAEABAAoAQAAFgAAACgAAAAQAAAAIAAAAAEABAAAAAAAAAAAAEgAAABIAAAAEAAAAAAAAAD///8Aub2+AF2InQAGUXoAL3GPAIGfrAD38+8A/Pn3AKa3wAAMcKEA7+zvANTV1wAMfbYAGIzKAPf//wAMiscAASIiM0VnAAB4kzJJMqcAALtDFyNWAAAAEVNXg1ZwAAChgyYTJnAAAKETQiNKdwAAckzNlMKOAAACzd3d3MHgAAXN3d3d9BWHCk3c3E3UmZgAud3ItNncwgBy/UoBmdyVAAKcSgZJWIEAC5kgtDzFugAAtaBln8NXAAAAAAYkKqcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"""
        return ICON_BASE64
        
        
def test_icon():
    with open("icon.ico", "rb") as icon_file:
        base64_icon = base64.b64encode(icon_file.read()).decode("utf-8")

    print(f'ICON_BASE64 = """{base64_icon}"""')

if __name__ == "__main__":
    test_icon()