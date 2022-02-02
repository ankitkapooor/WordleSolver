import operator

wordlist = []
altered_wordlist = []
final_wordlist = []
position_list = [_ for _ in range(5)]
count = 0

#function to score the words for maximum probability of getting greens
def scoredlist(final_wordlist):
    alphabets = list(map(chr, range(97, 123)))
    scoredict = {}
    wordscoredict = {}
    sum = 0
    wse=0
    for alphabet in alphabets:
        for word in wordlist:
            for i in range(5):
                if alphabet == word[i]:
                    sum += 1
                score = sum / 5757
                scoredict.update({alphabet : score})

    for word in final_wordlist:
        for letter in word:
            wse =+ scoredict.get(letter)
        wordscoredict.update({word : wse})
    wordscoredict = dict(sorted(wordscoredict.items(), key=operator.itemgetter(1) ,reverse=True))
    return [*wordscoredict]

#function applys the game rule and eliminates redundant words from the word list
def game_logic(color_scheme, word, position_list, wordlist):
    for key in wordlist:
        for color, letter, position in zip(color_scheme, word, position_list):
            if color.lower() == 'g':
                if letter != key[position]:
                    if key not in altered_wordlist:
                        altered_wordlist.append(key)
            elif color.lower() == 'y':
                if letter not in key or letter == key[position]:
                    if key not in altered_wordlist:
                        altered_wordlist.append(key)
            elif color.lower() == 'b':
                if letter in key:
                    if key not in altered_wordlist:
                        altered_wordlist.append(key)
    for i in range(len(altered_wordlist)):
        if wordlist[i] not in altered_wordlist:
            final_wordlist.append(wordlist[i])
    return scoredlist(final_wordlist)[:5]

with open("assets/words.csv", 'r', encoding = 'utf-8') as f:
    for i in range(5757):
        wordlist.append(f.readline()[:5])

#continuous while loop allows guessing till either the algorithm runs out of answers
#or the game crosses 6 turns
while len(final_wordlist) !=0 or count < 6:
    final_wordlist = []
    word = input("\tinput the word: ")
    color_scheme = input("\tInput the color scheme(b/g/y): ")
    print("\tTop 5 options:", end = " ")
    print(*game_logic(color_scheme, word, position_list, wordlist), end = " ")
    print("\n")
    count += 1
