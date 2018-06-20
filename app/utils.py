import math

def custom_paginator(current_page,num_page,max_page):
    middle = math.ceil(max_page/2)
    if num_page<=max_page:
        start =1
        end = num_page
    elif current_page<=middle:
        start=1
        end = max_page
    elif middle < current_page < num_page - middle+1:
        start =current_page -middle
        end = current_page +middle -1
    else:
        start = num_page -max_page +1
        end = num_page
    return start,end










