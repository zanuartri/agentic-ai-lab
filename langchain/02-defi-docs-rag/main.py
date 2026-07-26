from dotenv import load_dotenv

load_dotenv()

from agent import ask

def main():
    print("Uniswap Docs Q&A - type 'exit' to quit\n")

    while True:
        question = input("> ")
        if question.lower() in ("exit", "quit"):
            break

        answer, sources = ask(question)
        print(f"\nAnswer:\n{answer}\n")
        print("Sources:")
        for source in sources:
            print(f"- {source}")
        print()

if __name__ == "__main__":
    main()