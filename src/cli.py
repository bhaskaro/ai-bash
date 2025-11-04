import runpy, sys
from src.loop import ai_turn

def main():
    print("🤖 AI Bash: type your task. Ctrl+C to exit.\n")
    while True:
        try:
            q = input("> ").strip()
            if q.lower() in {"exit", "quit", "bye", "q"}:
                print("👋 Exiting AI Bash — see you next time!")
                sys.exit(0)

            if not q:
                continue

            out = ai_turn(q)
            print(out.get("final", ""))
        except KeyboardInterrupt:
            print("\n👋 Exiting AI Bash — interrupted.")
            sys.exit(0)
        except EOFError:
            print("\n👋 Exiting AI Bash — EOF.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
