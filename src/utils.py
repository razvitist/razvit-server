import random
import string


def amount(n):
  return (
    (
      (
        f'{str(n)[:-9]}.{str(n)[-9]}B'
        if n >= 1000000000
        else f'{str(n)[:-6]}.{str(n)[-6]}M'
      )
      if n >= 1000000
      else f'{str(n)[:-3]}.{str(n)[-3]}K'
    )
    if n >= 1000
    else n
  )


def genapikey():
  return ''.join(
    random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
    for _ in range(10)
  )
