import json
import base64
import re
s=['/m/htEE7jQzXSqpq7VWduQ==','9gCIDh74zVD/pcGXaal71Q==','I8HNl/rH0Cz2fIHBu7Uczg==','aJQ0u+/iTlDEWLLFV0YGFw==']
for i in s:
    tt=base64.b64decode(i)
    #tt=str(~tt)
    print(tt)
    for j in tt:
        print(j)
    
    #answer_numb=re.compile(r'\d+').findall(tt)