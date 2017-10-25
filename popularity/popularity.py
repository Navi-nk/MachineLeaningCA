# This function is to dedermine popularity based on n number of popularities of similar movies provided
# currently function returns 1 -> Low (rating <5) 2 -> Medium low (rating <15), 
#  3 -> Medium (rating <30), 4 -> High (rating <100), 5 -> super (rating > 100)
# popularity probability of movie provided in request


def popularity(n):
       
    length = len(n)
    
    if length == 0:
        return 0
    
    l = 0
    ml = 0
    m = 0
    h = 0
    s = 0
    
    # current dataset provides popularity index between 0 to 1000 
    # according to that there are below popularity segments calculated
    
    for i in range(0,len(n)):
        
       if n[i] < 5:
           
           l = l + 1    
           
       elif n[i] < 15:
           
           ml = ml + 1
           
       elif n[i] < 30:
           
           m = m + 1
           
       elif n[i] < 100:
           
           h = h + 1
           
       else:           
           s = s + 1
      
    # deciding maximum popularities falling under which category
    
    print(l,ml,m,h,s)
        
    maxval = max(l,ml,m,h,s);
    
    print(maxval)
    
    if maxval == l:
        
        return 1
    
    elif maxval == ml:
        
        return 2
    
    elif maxval == m:
        
        return 3
    
    elif maxval == h:
        
        return 4
    
    elif maxval == s:
        
        return 5
    
    else:
        return 0
        

# Remove calling function for TESTING

n = [1 ,2 , 3, 11, 12, 13, 20, 25, 28, 57, 78, 83, 99, 200, 800, 500]

result = popularity(n)
         
print(result);
            
            