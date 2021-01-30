__dep_type: str
__is_enhanced: bool

def set_dep_type(dep_type):
    global __dep_type, __is_enhanced
    __dep_type = dep_type
    __is_enhanced = "enhanced" in __dep_type.lower()

def get_dep_type():
    global __dep_type
    return __dep_type

def get_is_enhanced():
    global __is_enhanced
    return __is_enhanced
