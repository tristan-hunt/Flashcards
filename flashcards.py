import argparse
import pandas as pd
import random
import time

class Deck:
	def __init__(self, num_cols, front, back):
		self.flashcards = []
		self.num_cols = num_cols
		self.front = front
		self.back = back

class Flashcard:
	def __init__(self, deck, front, back, column, row):
		self.deck = deck
		self.front = front
		self.back = back
		self.column = column
		self.row = row
		self.correct = False

	def show_front(self):
		r = "{}: {}".format(self.deck.front, self.front)
		return r

	def show_back(self):
		return "{}: {}".format(self.deck.back, self.back)

	def show_card(self):
		return "{}: {}, {}: {}".format(self.deck.front, self.front, self.deck.back, self.back)

	def show_reverse(self):
		return "{}: {}, {}: {}".format(self.deck.back, self.back, self.deck.front, self.front)


def create_deck(filename, num_cols):
	df = pd.read_excel(filename)
	front = df.columns.values[0]
	back = df.columns.values[1]

	deck = Deck(num_cols, front, back)
	for i in range(num_cols):
		front_column = "{}.{}".format(front, i) if i else front
		back_column = "{}.{}".format(back, i) if i else back
		for row in range(df[front_column].size):
			f = df[front_column][row]
			b = df[back_column][row]
			if not (pd.isnull(f) or pd.isnull(b)):	
				fc = Flashcard(deck, f.strip(), b.strip(), i, row)
				deck.flashcards.append(fc)
	
	return deck

def get_cards_from_deck(deck, first_letter, start_index, number_of_cards):
	flashcards = [fc for fc in deck.flashcards if fc.column == first_letter or first_letter == -1]
	return flashcards[start_index:number_of_cards+start_index]

def play_game(deck, mode, first_letter, start_index, number_of_cards):
	flashcards = get_cards_from_deck(deck, first_letter, start_index, number_of_cards)
	play_cards(mode, deck, flashcards)

def play_cards(mode, deck, cards):
	source = deck.front if mode%2 == 0 else deck.back
	target = deck.back if mode%2 == 0 else deck.front

	if mode >= 2:
		random.shuffle(cards)

	num_cards = len(cards)
	start_time = time.time()

	for i, fc in enumerate(cards):
		source_word = fc.front if mode%2==0 else fc.back
		target_word = fc.back if mode%2==0 else fc.front

		quiz(fc, source, source_word, target, target_word, i, num_cards)

	print("All Done!")
	correct = sum(fc.correct == True for fc in cards)
	incorrect = len(cards) - correct
	print("Correct: {}".format(correct))
	print("Incorrect: {}".format(incorrect))

	if (incorrect):
		incorrect_cards = [fc for fc in cards if not fc.correct]
		print("\n".join([fc.show_card() for fc in incorrect_cards]))
		again = input("review incorrect words (y/n): ")
		if again == 'y' or again == '1' or again == 'да':
			play_cards(mode, deck, incorrect_cards)
	else:
		finish_time = time.time()
		time_diff = time.gmtime(finish_time - start_time)
		avg_time = time.gmtime((finish_time - start_time) / num_cards)
		print("Total Time: {}".format(time.strftime("%H:%M:%S", time_diff)))
		print("Time per card: {}".format(time.strftime("%H:%M:%S", avg_time)))

def quiz(fc, source_language, source_word, target_language, target_word, i, number_of_cards):
		print("Card {}/{}".format(i+1, number_of_cards))
		print("{} word: {}".format(source_language, source_word))
		answer = input("Enter {} translation: ".format(target_language))
		
		if is_correct(answer, target_word):
			fc.correct = True
			print("Correct!")
		
		else:
			print("Incorrect! Correct answer was: {}".format(target_word))
			n = input("Enter {} translation for {}: ".format(target_language, source_word))


def is_correct(answer, target):
	return format_for_comparison(answer) == format_for_comparison(target)


def format_for_comparison(word):
	# strip whitespace and lowercase
	word = word.strip().lower()

	# pop off the declensions from the end
	word = word.split('(')

	# sort the list of meanings
	word[0] = word[0].split(', ')
	word[0].sort()

	# join the first part back together:
	word[0] = ', '.join(word[0])

	# now add the declensions back on
	word = '('.join(word)
	
	return word


def learn_words(deck, first_letter, start_index, number_of_cards):
	flashcards = get_cards_from_deck(deck, first_letter, start_index, number_of_cards)
	for i, card in enumerate(flashcards):
		print("Card {}/{}".format(i+1, number_of_cards))
		input("{}\nPractice: ".format(card.show_card()))
		input("{}\nPractice: ".format(card.show_front()))
		input("{}\nPractice: ".format(card.show_back()))
	
	print("Done! Review learned words:")
	for card in flashcards:
		print("{}".format(card.show_card()))

def main(filename, first_letter, start_index, number_of_cards, mode):
	num_cols = 9
	deck = create_deck(filename, num_cols)
	print("Welcome to The Flashcard Learner!")
	# print("Available Modes:")
	# print("0: Quiz - Given a word in {}, provide {} translation".format(deck.front.lower(), deck.back.lower()))
	# print("1: Quiz - Given a word in {}, provide {} translation".format(deck.back.lower(), deck.front.lower()))
	# print("2: Mode 0 with cards given in random order")
	# print("3: Mode 1 with cards given in random order")
	# print("4: Learning - Shown {} and {} side by side, practice typing both".format(deck.front.lower(), deck.back.lower()))
	# mode = int(input("Enter mode: "))
	
	print("Okay! Let's play!")
	if mode == 4:
		learn_words(deck, first_letter, start_index, number_of_cards)
	else:
		play_game(deck, mode, first_letter, start_index, number_of_cards)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Learn flashcards")
	parser.add_argument("filename", help="name of .xlsx file with vocab", default="RussianVocab.xlsx")
	parser.add_argument("category", type=int, help="e.g. which letter are you learning? (-1: all, 0:a, 1:б, 2:в, etc.)")
	parser.add_argument("start", type=int, help="start index (lists are 0-indexed)")
	parser.add_argument("num", type=int, help="number of cards you'd like to see")
	parser.add_argument("mode", type=int)
	args = parser.parse_args()
	main(args.filename, args.category, args.start, args.num, args.mode)

