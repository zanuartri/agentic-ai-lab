from dotenv import load_dotenv

load_dotenv()

from agent import executor

def main():
    print("DeFi Yield Scout — type 'exit' to quit\n")
    messages = []
    MAX_HISTORY = 10  # keep last 10 messages (~5 exchanges)

    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})
        result = executor.invoke({"messages": messages})
        reply = result["messages"][-1]
        print(reply.content, "\n")

        messages = result["messages"][-MAX_HISTORY:]

if __name__ == "__main__":
    main()
