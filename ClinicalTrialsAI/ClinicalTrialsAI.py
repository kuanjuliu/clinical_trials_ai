# ------------------------------------------------------------------------------
# Fit the inclusion and exclusion criteria for clinical trials into a format
# that GPT 3.5 can parse in natural language and evaluate whether a person's
# age, gender, and medical history make them eligibile for certain trials (NCT ID)
# ------------------------------------------------------------------------------

# Example of a working list of criteria (Used only for testing)
criteria_list = [
    {
        "nct_id": "NCT05608694",
        "inclusion_criteria": [
            "Male age 18 and older",
            "No known history of prostate cancer",
            "No previous prostate resection or ablation (e.g. TURP, photovaporization)"
        ],
        "exclusion_criteria": [
            "Unable to tolerate MRI due to metal fragments or claustrophobia",
            "Lack of a rectum",
            "Hip arthroplasty"
        ]
    },
    {
        "nct_id": "NCT05608695",
        "inclusion_criteria": [
            "Male age 18 and older",
            "No known history of prostate cancer",
            "No previous prostate resection or ablation (e.g. TURP, photovaporization)"
        ],
        "exclusion_criteria": [
            "Unable to tolerate MRI due to metal fragments or claustrophobia",
            "Lack of a rectum",
            "Hip arthroplasty"
        ]
    },
    # Add more criteria for other NCT IDs
]

# Load the inclusion/exclusion criteria output by ClinicalTrialsETL
import pandas as pd
import re
df = pd.read_csv('inclusion_exclusion_criteria.csv', delimiter='`')
df.fillna('', inplace=True)


# Turn the inclusion_exclusion_criteria.csv into a usable list of lists to feed OpenAI
import json
df['inclusion_criteria'] = df['inclusion_criteria'].transform(lambda x: x.split('\n'))
df['exclusion_criteria'] = df['exclusion_criteria'].transform(lambda x: x.split('\n'))
criteria_list = json.loads(df.to_json(orient='records', lines=False))


# Set up OpenAI API key
import openai
import os
openai.api_key=os.environ.get("OPENAI_API_KEY"),

# Construct the ChatGBPT-style prompt
def construct_prompt(person, criteria):

    prompt = "I am evaluating potential participants for the below clinical trial."
    prompt += "\n\n"
    prompt += f"Could you please assess if a {person['age']}-year-old {person['gender']} with {', '.join(person['conditions'])} meets the inclusion criteria and does not match any exclusion criteria for the following clinical trial?"
    prompt += "That is, do the person's traits meet at least some of the inclusion criteria without contradicting any of them, while also not matching the exclusion criteria?"
    prompt += "The given characteristics of the prospective participant's are all you can know about them. Don't conclude they have any other traits."
    prompt += "Don't forget to check whether the participant's age lies between the trial's minimum and maximal acceptable ages."
    prompt += "Also, please do not take into account any future possibility of a participant developing a match to a criteria: only the known existing conditions matter."
    prompt += "Finally, please take into account whether the trial is looking for children or not: if the prospective volunteer is an adult, then they would be ineligible."
    prompt += "\n\n"
    prompt += "Please format your response in this manner:\n"
    prompt += "\n\n"
    # prompt += "• NCT ID\n"
    # prompt += "• URL\n"
    prompt += "• Whether the prospective participant is eligible, provisionally eligible, or ineligible for the trial\n"
    prompt += "• Explain how you determined eligibility\n"
    prompt += "\n\n"
    # for criteria in criteria_list:
    prompt += "NCT ID: " + criteria['nct_id'] + "\n"
    prompt += "URL: " + criteria['URL'] + "\n\n"
    prompt += "Minimum Age " + criteria['minimum_age'] + "\n\n"
    prompt += "Maximum Age: " + criteria['maximum_age'] + "\n\n"
    prompt += "Gender: " + criteria['gender'] + "\n\n"
    prompt += "Inclusion Criteria:\n\n" + "\n".join(criteria['inclusion_criteria']) + "\n"
    prompt += "Exclusion Criteria:\n\n" + "\n".join(criteria['exclusion_criteria']) + "\n\n"

    return prompt

# Gain a response for the prompted question from OpenAI's API
from openai import OpenAI
client = OpenAI()

def check_eligibility_with_openai(person, criteria):
    prompt = construct_prompt(person, criteria)
    response = client.completions.create(
        # model='gpt-4o-2024-05-13',
        # model='gpt-4-turbo',
        # model='gpt-3.5-turbo-0125',
        model='gpt-3.5-turbo-instruct',
        # model='text-davinci-003',
        prompt=prompt,
        max_tokens=400,
        n=10,
        stop="</s>",
        temperature=0.7,
    )
    return response.choices[0].text

# Test person
person = {
    "age": 49,
    "gender": "male",
    "conditions": ["no history of cancer"]
}



# Check eligibility for a few trials
print("----------------------------------------------------------------------------------------------------------------------------------------------------")
for criteria in criteria_list[0:10]:
    result = check_eligibility_with_openai(person, criteria)
    print("• NCT ID: " + criteria['nct_id'])
    print("• URL: " + criteria['URL'])
    print(result)
    print("----------------------------------------------------------------------------------------------------------------------------------------------------")

# print(construct_prompt(person, criteria))
#
# # Fine tune through better prompts
# response = client.completions.create(
#         # model='gpt-4o-2024-05-13',
#         # model='gpt-4-turbo',
#         # model='gpt-3.5-turbo-0125',
#         model='gpt-3.5-turbo-instruct',
#         # model='text-davinci-003',
#         # prompt="The prospective participant has never had cancer before so cannot have a peripheral lung tumor"
#         prompt="Why would you think he was a cancer survivor?"
#         # prompt="That's correct, all you have are the participant's age, gender, and no history of cancer. That implies he doesnt't have 'peripheral lung tumor'"
#         # prompt="Exactly. So why were you so sure he had a 'peripheral lung tumor'?"
#         # prompt="Can you try again with the last clinical trial?"
# )
# print (response)