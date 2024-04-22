import re

import pandas as pd

df = pd.read_json('./chatgpt-cot.json')

df['label'].value_counts()

d = {'proved': 0, 'disproved': 0, 'unknown': 0}
k = len(df)
LABEL_COL = 'chatgpt-guess-label-cot'
df[LABEL_COL] = ''
unsure = 0
for index, row in df.iterrows():
    text = row['chat-gpt-3.5-turbo-ans'].lower()
    proved = re.search(r'\bproved\b(?!disproved)', text)
    disproved = re.search(r'disproved', text)
    unknown = re.search(r'unknown', text)

    proven = re.search(r'proven', text)
    doesNot = re.search(r'does not', text)
    w = (proved and not ((proved and doesNot) or (proven and doesNot)))

    if (w and disproved) or (w and unknown) or (disproved and unknown) or (not w and not disproved and not unknown):
        unsure += 1
        isFixed = False
        
        while not isFixed:
            print(f'Proved: {proved}, Disproved: {disproved}, Unknown: {unknown}, {k} left')
            print('######################################################################')
            print(row['question'].split('Based on the game state and the rules and preferences,',1)[-1])
            print(text)
            userInput = input('Proved (1), disproved (2), unknown (3): ')
            try:
                userInt = int(userInput)
                if userInt <= 0 or userInt >= 4:
                    raise ValueError()
                isFixed = True
                
                if userInt == 1:
                    proved, disproved, unknown = True, False, False
                elif userInt == 2:
                    proved, disproved, unknown = False, True, False
                elif userInt == 3:
                    proved, disproved, unknown = False, False, True
            except ValueError:
                print(f'Bad value entered ({userInput} w as entered), try again')
    if proved:
        d['proved'] += 1
        df.at[index, LABEL_COL] = 'proved'
    elif disproved:
        d['disproved'] += 1
        df.at[index, LABEL_COL]  = 'disproved'
    elif unknown:
        d['unknown'] += 1
        df.at[index, LABEL_COL]  = 'unknown'
    k -= 1
df.to_json('./chatgpt-guess-label-cot-2.json', orient='records')
print(d, unsure)
