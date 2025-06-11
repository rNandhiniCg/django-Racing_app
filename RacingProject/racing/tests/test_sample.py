def hello(name : str):
    return f"Hii {name}"

def test_hello_returns_string():
    result = hello('Nani')
    assert isinstance(result, str)