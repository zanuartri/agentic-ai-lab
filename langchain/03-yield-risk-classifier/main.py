from dotenv import load_dotenv

load_dotenv()

from agent import executor

def main():
    print("Yield Risk Classifier — type 'exit' to quit\n")

    while True:
        question = input("> ")
        if question.lower() in ("exit", "quit"):
            break

        result = executor.invoke({"messages": [{"role": "user", "content": question}]})
        assessments = result["structured_response"]
        print(assessments.model_dump_json(indent=2))
        print()

if __name__ == "__main__":
    main()