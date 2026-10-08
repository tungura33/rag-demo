from rag import generate_answer


# ---------------------------------------------------------
# Display application header
# ---------------------------------------------------------

def display_header():

    print()
    print("=" * 70)
    print("             COMPANY POLICY RAG ASSISTANT")
    print("=" * 70)

    print()
    print("Ask questions about the company policy.")
    print("The assistant will search the policy PDF")
    print("and provide an answer based on the document.")
    print()
    print("Type 'exit' or 'quit' to close the application.")
    print("=" * 70)


# ---------------------------------------------------------
# Process user question
# ---------------------------------------------------------

def process_question(question):

    try:

        print()
        print("Searching company policy...")

        answer = generate_answer(
            question
        )

        print()
        print("-" * 70)
        print("ASSISTANT")
        print("-" * 70)

        print()
        print(answer)

        print()
        print("-" * 70)

    except Exception as e:

        print()
        print("ERROR")
        print("-" * 70)

        print(
            f"Something went wrong: {e}"
        )

        print()
        print(
            "Please make sure you have run "
            "'python ingest.py' first."
        )


# ---------------------------------------------------------
# Main application
# ---------------------------------------------------------

def main():

    display_header()

    while True:

        print()

        question = input(
            "You: "
        ).strip()

        # -------------------------------------------------
        # Check for empty input
        # -------------------------------------------------

        if not question:

            print(
                "Please enter a question."
            )

            continue

        # -------------------------------------------------
        # Exit application
        # -------------------------------------------------

        if question.lower() in [
            "exit",
            "quit"
        ]:

            print()
            print(
                "Thank you for using "
                "Company Policy RAG Assistant."
            )

            print()

            break

        # -------------------------------------------------
        # Process question
        # -------------------------------------------------

        process_question(
            question
        )


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

if __name__ == "__main__":

    main()

