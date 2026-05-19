import re

def lex(content: str) -> list:
    tokens = []
    keywords = ["int", "void", "return"]
    token_matchers = [r"[a-zA-Z_]\w*\b", r"[0-9]+\b", r"\(", r"\)", r"{", r"}", r";"]
    token_types = ["ident", "constant", "int", "void", "return", "(", ")", "{", "}", ";"]
    while content != "":
        # trim whitespace
        whitespace = re.match(r"\s+", content)
        if whitespace:
            content = content[len(whitespace[0]):]
        else:
            startMatch = False
            for matcher in token_matchers:
                m = re.match(matcher, content)
                if m:
                    startMatch = True
                    if matcher == r"[a-zA-Z_]\w*\b":
                        if m[0] in keywords:
                            tokens.append((m[0]))
                        else:
                            tokens.append(("Identifier", m[0]))
                    elif matcher == r"[0-9]+\b":
                        tokens.append(("Constant", m[0]))
                    else:
                        tokens.append((m[0]))
                    content = content[len(m[0]):]
                    break

            if not startMatch:
                raise ValueError
            
    return tokens