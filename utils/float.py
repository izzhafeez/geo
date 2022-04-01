def check_float(s):
    try:
        float(s)
        return True
    except:
        return False

def check_all_float(*s):
    return all([check_float(x) for x in s])

def check_all_float_dict(d):
    return all([check_float(v) for k, v in d.items()])

def convert_all_float_dict(d):
    return {k: float(v) for k, v in d.items()}