
from profanity_check import predict
import csv
import sys
sys.path.append("..")
from detect_hate import filter_levels, call_gpt
import secret_values

strictness = sys.argv[1]

filter_level = filter_levels[int(strictness)]
print(filter_level)
gpt_key = secret_values.GPT_KEY

input_file = open('data.csv', 'r')

reader = csv.reader(input_file)

false_positives = 0
false_negatives = 0
true_positives = 0
true_negatives = 0

hateful_messages = 0
non_hateful_messages = 0

i = 0
for row in reader:
  print("doing row #" + str(i))
  prediction = call_gpt(row[3], gpt_key, filter_level)
  
  if prediction == 1 and row[4] == 'hate':
    true_positives += 1
  elif prediction == 1 and row[4] == 'nothate':
    false_positives += 1
  elif prediction == 0 and row[4] == 'hate':
    false_negatives += 1
  elif prediction == 0 and row[4] == 'nothate':
    true_negatives += 1

  if row[4] == 'hate':
    hateful_messages += 1
  elif row[4] == 'nothate':
    non_hateful_messages += 1
  
  i += 1
  if i > 100:
    break #TODO: remove this


outfile = open(f'gpt-profanity-check-strict-{strictness}-results.txt', 'a')

outfile.write("\n")
outfile.write(f"Run of {i} messages\n")
outfile.write(f"true positives: {true_positives}\n")
outfile.write(f"true negatives: {true_negatives}\n")
outfile.write(f"false positives: {false_positives}\n")
outfile.write(f"false negatives: {false_negatives}\n")
outfile.write(f"accuracy: {(true_positives + true_negatives) / i * 100}%\n")
outfile.write(f"coverage: {(true_positives / hateful_messages) * 100}%\n")


