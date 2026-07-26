from dotenv import load_dotenv

load_dotenv()

from agent import executor

def main():
    print("Persistent Memory Agent — type 'exit' to quit\n")
    thread_id = input("thread id (blank = 'default'): ").strip() or "default"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            break

        result = executor.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
        )
        reply = result["messages"][-1]
        print(reply.content, "\n")

if __name__ == "__main__":
    main()