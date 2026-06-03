import re

keywords = ["int", "void", "return"]
token_matchers = [r"[a-zA-Z_]\w*\b", r"[0-9]+\b", r"\(", r"\)", r"{", r"}",
                  r";", r"~", r"--", r"-", r"\*", r"\+", r"/", r"%",
                  r"&&", r"&", r"\|\|", r"\|", r"==", r"!=", r"<=", r">=", r"<", r">", r"=", r"!"]

def lex(content: str) -> list:
    tokens = []
    while (content := content.lstrip()) != "":
        longestMatch = None
        matchType = None
        for matcher in token_matchers:
            m = re.match(matcher, content)
            if m:
                # skip shorter matches
                if longestMatch and len(m[0]) <= len(longestMatch):
                    continue

                # matcher is for identifiers
                if matcher == r"[a-zA-Z_]\w*\b":
                    if m[0] in keywords:
                        longestMatch = m[0]
                    else:
                        longestMatch = m[0]
                        matchType = "Identifier"

                # matcher is for constants
                elif matcher == r"[0-9]+\b":
                    longestMatch = m[0]
                    matchType = "Constant"
                else:
                    longestMatch = m[0]
        
        if not longestMatch:
            raise ValueError
        
        if matchType:
            tokens.append((matchType, longestMatch))
        else:
            tokens.append(longestMatch)

        content = content[len(longestMatch):]
            
    return tokens