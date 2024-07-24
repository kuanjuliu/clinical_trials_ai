from participants import Participant
from criteria import load_and_process_criteria
from eligibility import setup_openai_api, check_multiple_eligibility_with_openai

def main():

    # Load and process criteria
    criteria_list = load_and_process_criteria('inclusion_exclusion_criteria.csv')

    # Setup OpenAI API
    setup_openai_api()

    # Define a prospective participant's characteristics
    participant = Participant(
        age=49,
        gender="Male",
        conditions=[
            "No known history of cancer"
        ]
    )

    # Check eligibility for a few trials
    check_multiple_eligibility_with_openai(participant, criteria_list, model = 'gpt-4o-mini', temperature = 0.2)


if __name__ == "__main__":
    main()
