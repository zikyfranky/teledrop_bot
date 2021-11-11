import random


def askNum(text):
    """Retunrs an integer from input using 'text'. Loops until valid input given."""
    while True:
        try:
            return int(input(text))
        except ValueError:
            print("Please try again")

def calc(a,ops,b):
    """Returns integer operation result from using : 'a','ops','b'"""
    if   ops == "+": return a+b
    elif ops == "-": return a-b
    elif ops == "*": return a*b
    elif ops == "/": return a//b   # integer division
    else: raise ValueError("Unsupported math operation")


def captcha(cb_success, cb_fail):
    """
    Captcha challenge.
    Returns True if user input is correct, False if not.
    """
    nums = range(1,100)

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
    result = askNum("What is {} {} {} = ".format(a,ops,b))

    corr = calc(a,ops,b)
    if  result == corr:
        print("Correct")
        cb_success()
    else:
        print("Wrong. Correct solution is: {} {} {} = {}".format(a,ops,b,corr))
        cb_fail()