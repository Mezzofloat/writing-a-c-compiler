import re

keywords = ["int", "void", "return"]
token_matchers = [r"[a-zA-Z_]\w*\b", r"[0-9]+\b", r"\(", r"\)", r"{", r"}",
                  r";", r"~", r"--", r"-", r"\*", r"\+", r"/", r"%"]

def lex(content: str) -> list:
    tokens = []
    while (content := content.lstrip()) != "":
        startMatch = False
        for matcher in token_matchers:
            m = re.match(matcher, content)
            if m:
                startMatch = True

                # matcher is for identifiers
                if matcher == r"[a-zA-Z_]\w*\b":
                    if m[0] in keywords:
                        tokens.append((m[0]))
                    else:
                        tokens.append(("Identifier", m[0]))

                # matcher is for constants
                elif matcher == r"[0-9]+\b":
                    tokens.append(("Constant", m[0]))
                else:
                    tokens.append((m[0]))
                content = content[len(m[0]):]

                # break from the for loop into the while loop
                break

        if not startMatch:
            raise ValueError
            
    return tokens