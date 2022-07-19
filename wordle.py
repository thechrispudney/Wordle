import rich
import random
import time
import json
from cryptography.fernet import Fernet

PASSWORD = b'fgKg91px1HYs5jeBOWfEvV0cPhXY__kDcPems61fEG4='
algo = Fernet(PASSWORD)

def clear():
  print("\033[A                                   \033[A")

def save(guesses, solution, history, results):
  checkpoint = {"guesses": guesses, "solution": solution, "history": history, "results": results}
  json_data = json.dumps(checkpoint)
  encrypted_data = algo.encrypt(str.encode(json_data))
  with open("savegame", "w+") as f:
    f.write(encrypted_data.decode('UTF-8'))

def load():
  try:
    with open("savegame") as f:
      encrypted_data = f.read()
      decrypted_bytes = algo.decrypt(str.encode(encrypted_data))
      json_data = decrypted_bytes.decode('UTF-8')
      checkpoint = json.loads(json_data)
      guesses = checkpoint["guesses"]
      solution = checkpoint["solution"]
      history = checkpoint["history"]
      results = checkpoint["results"]
      return guesses, solution, history, results
  except FileNotFoundError as err:
    return [], "", [], []

# indexes is a function returning a list of indexes where "want_character" appears in "word"
def indexes(word, want_character):
  _indexes = []
  for index, got_character in enumerate(word):
    if got_character == want_character:
      _indexes.append(index)
  return _indexes

def evaluate_guess(guess, solution):

  # if it matches, then we don't need to do any work
  if guess == solution:
    rich.print("[green]" + guess + "[/green]")
    return True

  # create a list containing all the hints
  answer = []

  # create a dictionary, mapping each character to how many times it appears in the solution
  letter_counts = {c: solution.count(c) for c in solution}

  # create a dictionary, mapping each character to the indexes where it appears in the solution
  mapping = {c: indexes(solution, c) for c in solution}

  # go through each letter in the user's guess, printing a hint for each
  for index, letter in enumerate(guess):
    
    # if the letter is not in the mapping dictionary, then it does not exist in the solution
    if letter not in mapping:
      answer.append(letter)

    # if the letters count is 0, then the user has entered more instances of the letter than exists in the solution - therefore, we print it's not in the word
    elif letter_counts[letter] == 0:
      answer.append(letter)

    # if the index is in mapping[letter], then it means they've put the letter in a position matching the position
    elif index in mapping[letter]:
      answer.append("[green]" + letter + "[/green]")

      # update the count for how many more times the user can enter this letter
      letter_counts[letter] -= 1

    else:
      answer.append("[yellow]" + letter + "[/yellow]")

      # update the count for how many more times the user can enter this letter
      letter_counts[letter] -= 1

  rich.print("".join(answer))

  return False
    

def read_words():
  with open("wordle.txt", 'r') as f:
    words = f.read().upper().split("\n")
  return words

def pick_word():
  words = read_words()
  return words[random.randint(0, len(words) - 1)]

def guess_word():
  valid = False
  while not valid:
    word = input("").upper()
    if word == "DEEZ NUTS":
      clear()
      rich.print("nice. :peanuts:")
      time.sleep(1)
      clear()
      rich.print("got em")
      time.sleep(1)
      clear()
      continue
    if len(word) != 5:
      clear()
      rich.print("[red]:warning:  Not the right length")
      time.sleep(1)
      clear()
      continue
    if not word.isalpha():
      clear()
      rich.print("[red]:warning:  Type a word")
      time.sleep(1)
      clear()
      continue
    if word not in read_words():
      clear()
      rich.print("[red]:warning:  Enter a valid word")
      time.sleep(1)
      clear()
      continue
    valid = True
  return word

def leaderboard(results):
  
  one = 0
  two = 0
  three = 0
  four = 0
  five = 0
  six = 0
  failed = 0
  
  for amount in results:
    if amount == 0:
      failed += 1
    elif amount == 1:
      one += 1
    elif amount == 2:
      two += 1
    elif amount == 3:
      three += 1
    elif amount == 4:
      four += 1
    elif amount == 5:
      five += 1
    elif amount == 6:
      six += 1

  if one == 1:
    print("\nYou have guessed the answer in one try once!")
  else:
    print("\nYou have guessed the answer in one try", one, "times!")
  if two == 1:
    print("You have guessed the answer in two tries once!")
  else:
    print("You have guessed the answer in two tries", two, "times!")
  if three == 1:
    print("You have guessed the answer in three tries once!")
  else:
    print("You have guessed the answer in three tries", three, "times!")
  if four == 1:
    print("You have guessed the answer in four tries once!")
  else:
    print("You have guessed the answer in four tries", four, "times!")
  if five == 1:
    print("You have guessed the answer in five tries once!")
  else:
    print("You have guessed the answer in five tries", five, "times!")
  if six == 1:
    print("You have guessed the answer in six tries once!")
  else:
    print("You have guessed the answer in six tries", six, "times!")
  if failed == 1:
    print("You have failed to guess the answer once!")
  else:
    print("You have failed to guess the answer", failed, "times!")


rich.print("[bold underline]WORDLE\n")

guesses, solution, history, results = load()
if solution == "":
  # Random word (hidden)
  solution = pick_word()
  while solution in history:
    solution = pick_word()

for saved_guess in guesses:
  evaluate_guess(saved_guess, solution)

# 6 attempts
end = False
while len(guesses) < 6 and not end:

  # Ask the user for their input
  guess = guess_word()

  guesses.append(guess)

  clear()
  
  # Tell them matching character
  end = evaluate_guess(guess, solution)

  save(guesses, solution, history, results)
  
history.append(solution)
if not end:
  results.append(0)
  rich.print("\n[bold]" + solution)
else:
  results.append(len(guesses))
save([], "", history, results)
leaderboard(results)