import random

# [1,0,-1,2,5,-2]
def test(list_t):
    res=[]
    list_t = list(set(sorted(list_t)))
    for i,v in enumerate(list_t):
        if v <0:
            for k in list_t[i:]:
                for m in list_t[::-1]:
                    if m <0:
                        pass
                    elif v+k+m==0 and m!=k:
                        
                        res.append([v,k,m])
        else:
            pass

    return res


if __name__ == "__main__":
    list_t = [1,0,-2,2,3,-1]
    print(test(list_t))
    