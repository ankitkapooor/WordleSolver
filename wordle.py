import operator

wordlist = []
altered_wordlist = []
final_wordlist = []
position_list = [0,1,2,3,4]
count = 0

#function to score the words for maximum probability of getting greens
def scoredlist(final_wordlist):
    alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
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

with open("assets/words.csv", 'r', encoding = 'utf-8') as f:
    for i in range(5757):
        wordlist.append(f.readline()[:5])

#continuous while loop allows guessing till either the algorithm runs out of answers
#or the game crosses 6 turns
while len(final_wordlist) !=0 or count < 6:
    final_wordlist = []
    word = input("\tinput the word: ")
    color_scheme = input("\tInput the color scheme(b/g/y): ")

    for key in wordlist:
        for color, letter, position in zip(color_scheme, word, position_list):
            if color == 'g' or color == 'G':
                if letter != key[position]:
                    if key not in altered_wordlist:
                        altered_wordlist.append(key)
            elif color == 'y' or color == 'Y':
                if letter not in key:
                    if key not in altered_wordlist:
                        altered_wordlist.append(key)
            elif color == 'b' or color == 'B':
                if letter in key:
                    if key not in altered_wordlist:
                        altered_wordlist.append(key)
    for i in range(len(altered_wordlist)):
        if wordlist[i] not in altered_wordlist:
            final_wordlist.append(wordlist[i])
    print(*scoredlist(final_wordlist))
    count += 1