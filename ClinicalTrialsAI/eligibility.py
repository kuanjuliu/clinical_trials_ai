import openai
import os

def setup_openai_api():
    """
    Set up the OpenAI API key from the environment variable.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")

def construct_prompt(participant, criteria):
    """
    Construct a ChatGPT-style prompt for evaluating clinical trial eligibility.

    Args:
    participant (object): An object containing participant information (age, gender, conditions).
    criteria (dict): A dictionary containing clinical trial criteria.

    Returns:
    str: A formatted prompt string for the OpenAI API.
    """
    prompt = "I am evaluating potential participants for the below clinical trial."
    prompt += "\n\n"
    prompt += f"Could you please assess if a {participant.age}-year-old {participant.gender} with {', '.join(participant.conditions)} meets the inclusion criteria and does not match any exclusion criteria for the following clinical trial?"
    prompt += "That is, do the participant's traits meet at least some of the inclusion criteria without contradicting any of them, while also not matching the exclusion criteria?"
    prompt += "The given characteristics of the prospective participant's are all you can know about them. Don't conclude they have any other traits."
    prompt += "Don't forget to check whether the participant's age lies between the trial's minimum and maximal acceptable ages."
    prompt += "Also, please do not take into account any future possibility of a participant developing a match to a criteria: only the known existing conditions matter."
    prompt += "Finally, please take into account whether the trial is looking for children or not: if the prospective volunteer is an adult, then they would be ineligible."
    prompt += "\n\n"
    prompt += "Please format your response in this manner:\n"
    prompt += "\n\n"
    prompt += "• Whether the prospective participant is eligible, provisionally eligible, or ineligible for the trial\n"
    prompt += "• Explain how you determined eligibility\n"
    prompt += "\n\n"
    prompt += "NCT ID: " + criteria['nct_id'] + "\n"
    prompt += "URL: " + criteria['URL'] + "\n\n"
    prompt += "Minimum Age " + criteria['minimum_age'] + "\n\n"
    prompt += "Maximum Age: " + criteria['maximum_age'] + "\n\n"
    prompt += "Gender: " + criteria['gender'] + "\n\n"
    prompt += "Inclusion Criteria:\n\n" + "\n".join(criteria['inclusion_criteria']) + "\n"
    prompt += "Exclusion Criteria:\n\n" + "\n".join(criteria['exclusion_criteria']) + "\n\n"

    return prompt

def check_eligibility_with_openai(client, participant, criteria, model='gpt-4o-mini', temperature=0.2):
    """
    Check eligibility for a clinical trial using OpenAI's API.

    Args:
    client (openai.OpenAI): An instance of the OpenAI client.
    participant (object): An object containing participant information.
    criteria (dict): A dictionary containing clinical trial criteria.
    model (str): The OpenAI model to use (default: 'gpt-4o-mini').
    temperature (float): The temperature setting for the API call (default: 0.2).

    Returns:
    str: The content of the API response.
    """
    prompt = construct_prompt(participant, criteria)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )

    return response.choices[0].message.content

def check_multiple_eligibility_with_openai(participant, criteria_list, model='gpt-4o-mini', temperature=0.2):
    """
    Check eligibility for one participant over multiple clinical trials using OpenAI's API.

    Args:
    participant (object): An object containing participant information.
    criteria_list (list): A list of dictionaries, each containing criteria for a clinical trial.
    model (str): The OpenAI model to use (default: 'gpt-4o-mini').
    temperature (float): The temperature setting for the API call (default: 0.2).

    Prints:
    The eligibility results for each trial.
    """
    client = openai.OpenAI()
    print("----------------------------------------------------------------------------------------------------------------------------------------------------")
    for criteria in criteria_list[0:10]:
        result = check_eligibility_with_openai(client, participant, criteria, 'gpt-4o-mini', 0.2)
        print("• NCT ID: " + criteria['nct_id'])
        print("• URL: " + criteria['URL'])
        print(result)
        print("----------------------------------------------------------------------------------------------------------------------------------------------------")
