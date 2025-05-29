import matplotlib.pyplot as plt
import re

text = "Two friends were met by a bear. One climbed a tree, abandoning the other. The other played dead, and the bear left him unharmed."

# Convert text to lower case
text = text.lower()

# Remove the unwanted characters
textList = re.split(', | |\. ', text)

textDict = {}

# Find the frequency of words
for txt in textList:
    if txt in textDict:
        textDict[txt] += 1
    else:
        textDict[txt] = 1

# Sort the word frequencies in descending order
wordFrequency = dict(
    sorted(textDict.items(), key=lambda x: x[1], reverse=True)
)

# Define lists for rank, frequency, and word labels
rank = []
frequency = []
words = []

# Assign ranks and collect frequencies and words
for i, (word, freq) in enumerate(wordFrequency.items(), start=1):
    rank.append(i)
    frequency.append(freq)
    words.append(word)
    print(f"Rank {i}: Word = '{word}', Frequency = {freq}")

# Plot the Zipf's Law curve
plt.figure(figsize=(12, 6))
plt.plot(rank, frequency, marker='o')

# Annotate each point with the word
for i in range(len(rank)):
    plt.annotate(words[i], (rank[i], frequency[i]), textcoords="offset points", xytext=(0, 5), ha='center')

# Labels and title
plt.xlabel('Rank (r)')
plt.ylabel('Frequency (f)')
plt.title("Zipf's Law - Word Frequency vs. Rank")
plt.grid(True)
plt.show()
print("Zipf's Analysis for your Text")
