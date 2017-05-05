def filter_restaurants(restaurants, name="", cuisine="", cost="", suburb="", rating=""):
    if name:
        restaurants = [r for r in restaurants if name.lower() in r.get_name().lower()]
    if cuisine:
        restaurants = [r for r in restaurants if cuisine.lower() in r.get_cuisine().lower()]
    if suburb:
        restaurants = [r for r in restaurants if suburb.lower() in r.get_suburb().lower()]
    return restaurants

def average(arr):  # Calculates average value of an array
    total = 0
    i = 0
    # Equivalent to for i = 0; i < len(arr); i++
    for i in range(len(arr)): 
        total += arr[i]
    if i == 0:
        return -1
    else:
        return round(total/i, 1)


