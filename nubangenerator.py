import random

def savingaccountgen():
  ran = random.randint(10000000, 99999999)
  return "03"+str(ran)

def currentaccountgen():
  ran = random.randint(10000000, 99999999)
  return "01"+str(ran)