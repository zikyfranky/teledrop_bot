import random


def calc(a,ops,b):
    """Returns integer operation result from using : 'a','ops','b'"""
    if   ops == "+": return a+b
    elif ops == "-": return a-b
    elif ops == "*": return a*b
    elif ops == "/": return a//b   # integer division
    else: raise ValueError("Unsupported math operation")


def captcha_gen():
    """
    Captcha challenge.
    Returns Equation and Solution.
    """
    nums = range(1,10)

    ops = random.choice("+-*/")
    a,b = random.choices(nums,k=2)

    # you only allow integer input - your division therefore is
    # limited to results that are integers - make sure that this
    # is the case here by rerolling a,b until they match
    while ops == "/" and (a%b != 0 or a<=b):
        a,b = random.choices(nums,k=2)

    # make sure not to go below 0 for -
    while ops == "-" and a<b:
        a,b = random.choices(nums,k=2)

    # as a formatted text 
    equation = ("{} {} {}".format(a,ops,b))

    result = calc(a,ops,b)

    return [equation, result]