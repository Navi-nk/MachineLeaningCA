# This function is to determine popularity based on n number of popularities of similar movies provided
# currently function returns 1 -> Low (rating <5) 2 -> Medium low (rating <15), 
#  3 -> Medium (rating <30), 4 -> High (rating <100), 5 -> super (rating > 100)
# popularity probability of movie provided in request


def popularity(n):
    length = len(n)
    if length == 0:
        return 0
    l1 = ml = m = h = s = 0
    for i in range(0, len(n)):
        if n[i] < 5:
            l1 = l1 + 1
        elif n[i] < 15:
            ml = ml + 1
        elif n[i] < 30:
            m = m + 1
        elif n[i] < 100:
            h = h + 1
        else:
            s = s + 1
    max_val = max(l1, ml, m, h, s)
    if max_val == l1:
        return "Low"
    elif max_val == ml:
        return "Medium low"
    elif max_val == m:
        return "Medium"
    elif max_val == h:
        return "High"
    elif max_val == s:
        return "Very High"
    else:
        return 0
