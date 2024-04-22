import pandas as pd
from tqdm import tqdm
from LLMConnection import getChatGPT35ResponseChatMode

def get_final_answers(context, subproblems, final_question):
    systemInstructions = "You are a bot that can answer reasoning questions based off board game sitations"
    responses = []

    prompt = f"Here is the context of the reasoning question: \n{context}"
    
    # Send the context to ChatGPT and get an initial response
    initial_response, messages = getChatGPT35ResponseChatMode(prompt=prompt, systemInstructions=systemInstructions, messages=None)
    print('\t\t should be short')
    print(sum(len(msg['content']) for msg in messages if 'content' in msg))
    responses.append(initial_response)

    #iterate over subproblems
    for subproblem in subproblems:
        prompt = f"Briefly answer this subproblem based on the context provided earlier: \n{subproblem}"
        chat_response, messages = getChatGPT35ResponseChatMode(prompt=prompt, messages=messages)
        responses.append(chat_response)

    final_prompt = f"Answer this question based on what we have discussed. Is the label of the question 'proved', 'disproved', or 'unknown'. \n{final_question}"
    
    # Finally, ask the main question and get the response
    final_answer, messages = getChatGPT35ResponseChatMode(prompt=final_prompt, messages=messages)

    print(sum(len(msg['content']) for msg in messages if 'content' in msg))

    return responses, final_answer

def main():

    dataPath = './Data Processing/output-chatgpt-subproblems-data.json'
    df = pd.read_json(dataPath, dtype=str)

    newDf = df.iloc[640:]

    FINAL_ANS_DIR = './final_answers_output_chatgpt_decomposer.json'
    saveDf = pd.read_json(FINAL_ANS_DIR, dtype=str)
    
    #iterate the rows of the dataframe, for each row call the get_final_asnwers function
    for index, row in tqdm(newDf.iterrows(), total=newDf.shape[0]):
        context = row['context']
        subproblems = row['chatgpt-subproblems'].split('||')
        final_question = row['question']
        
        subproblem_responses, final_answer = get_final_answers(context, subproblems, final_question)
        
    #whatever Dennis did lol
        
        if saveDf is None:
            saveDf = pd.DataFrame(columns=df.columns.tolist() + ['subproblem_responses', 'final_answer'])
            saveDf = saveDf.astype(str)
        else:
            saveDf = pd.read_json(FINAL_ANS_DIR, dtype=str)

        new_record = row.to_dict()
        new_record['subproblem_responses'] = "||".join(subproblem_responses)
        new_record['final_answer'] = final_answer

        temp_df = pd.DataFrame([new_record])
        saveDf = pd.concat([saveDf, temp_df], ignore_index=True)
        saveDf.to_json(FINAL_ANS_DIR, orient='records')



if __name__ == "__main__":
    main()