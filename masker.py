from flask import abort
def maskdigits(number):
    if number.isdigit == True or len(number) == 16:
     number=  f"{number[:3]}***{number[-3:]}"
    else:
       abort(400, description="Credentials provided have issues")    
    return number

