# Wordle Solver

The following code is a simple way of tackling the popular game, **Wordle[https://www.powerlanguage.co.uk/wordle/]**. It uses a fairly simple way of solving the words by a combination of deduction and guessing. It is a very basic solution which doesn't use automation, but instead depends on user input for operation. It works in these simple steps:

**Steps:**
* **Step 1:** Type in whatever word you want in the actual game and copy the word into the prompt given when the program is run.
* **Step 2:** Type in the color combination of the outcome: say you got no letters correct, type in "bbbbb".
* **Step 3:** The program will output a list of valid words, any of which you can choose and write in the next line.
* **Step 4:** Repeat these steps till either you get the answer or you run out of turns.

This **YouTube[https://youtu.be/UVlnRTjWnVc]** video shows the algorithm in action:

<iframe width="560" height="315" src="https://www.youtube.com/embed/UVlnRTjWnVc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

The solver has been coded in python and is fairly simple:

~~~python
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
~~~

The following snippet of code instructs the algorithm which words to eliminate based on the color scheme input by the user. It takes two inputs from the user: **word** and **color scheme**.

~~~python
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
~~~

The following function, **scoredlist** ranks the outputs based on the probability of getting maximum greens. It does this by ranking each word by how probable it is to appear. A normalized score of each letter in the alphabet is calculated based on how frequently it appears in a given position in the entire dataset. These rankings are then compounded to find out the ranking of each word in the **final_wordlist**. These words paired with their ranking are stored in a dictionary, **wordscoredict**, where they are sorted from highest to lowest rank to maximize the probability of winning the game in as few rounds as possible.

![an image of the algorithm in action](assets/sample.png)

This is a very simple solution and more advanced ways to solve the puzzle do exist. The code is pretty first draft so clone the repository and have fun for yourself! 
