import re
date_field="41-03-2000"
if re.match("^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](20)\d\d$",date_field):
    print("YES")
else:
    print("No")