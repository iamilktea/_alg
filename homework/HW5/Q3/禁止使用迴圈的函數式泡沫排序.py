def my_map(func, lst):
    """無迴圈 map"""
    if not lst:
        return []
    return [func(lst[0])] + my_map(func, lst[1:])

def my_filter(func, lst):
    """無迴圈 filter"""
    if not lst:
        return []
    head = [lst[0]] if func(lst[0]) else []
    return head + my_filter(func, lst[1:])

def my_reduce(func, lst, initial=None):
    """無迴圈 reduce"""
    if not lst:
        return initial
    if initial is None:
        return my_reduce(func, lst[1:], lst[0])
    return my_reduce(func, lst[1:], func(initial, lst[0]))
