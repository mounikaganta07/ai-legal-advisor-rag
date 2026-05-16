from app.retrieval.hybrid_retriever import (
    hybrid_retrieve
)

# -----------------------------------
# HARDER EVALUATION DATASET
# -----------------------------------

test_questions = [

    {
        "question": "What is Article 21?",
        "expected_article": "21"
    },

    {
        "question": "Can the government take away personal liberty?",
        "expected_article": "21"
    },

    {
        "question": "Which article protects life and liberty?",
        "expected_article": "21"
    },

    {
        "question": "Explain directive principles",
        "expected_article": "37"
    },

    {
        "question": "Which constitutional provisions guide welfare governance?",
        "expected_article": "37"
    },

    {
        "question": "Are directive principles enforceable in court?",
        "expected_article": "37"
    },

    {
        "question": "What is right to constitutional remedies?",
        "expected_article": "32"
    },

    {
        "question": "Which article allows citizens to approach Supreme Court directly?",
        "expected_article": "32"
    },

    {
        "question": "What gives Supreme Court power to issue writs?",
        "expected_article": "32"
    },

    {
        "question": "Who can make laws for international treaties?",
        "expected_article": "253"
    },

    {
        "question": "Which authority implements international agreements?",
        "expected_article": "253"
    },

    {
        "question": "What are obligations of states and union?",
        "expected_article": "256"
    },

    {
        "question": "Which article ensures states follow parliamentary laws?",
        "expected_article": "256"
    },

    {
        "question": "Can Article 21 be suspended during emergency?",
        "expected_article": "359"
    },

    {
        "question": "Which article discusses suspension of fundamental rights during emergency?",
        "expected_article": "359"
    }

]

# -----------------------------------
# EVALUATION VARIABLES
# -----------------------------------

correct_retrievals = 0

top1_correct = 0

total_questions = len(test_questions)

print("\n" + "="*60)
print("LEGAL RAG RETRIEVAL EVALUATION")
print("="*60)

# -----------------------------------
# TEST LOOP
# -----------------------------------

for index, item in enumerate(test_questions):

    question = item["question"]

    expected_article = (
        item["expected_article"]
    )

    print(f"\nTest Case {index+1}")
    print("-"*40)

    print(f"Question: {question}")

    docs = hybrid_retrieve(question)

    retrieved_articles = []

    for doc in docs:

        article_number = (
            doc.metadata.get(
                "article_number",
                "N/A"
            )
        )

        retrieved_articles.append(
            str(article_number)
        )

    print(
        f"Expected Article: "
        f"{expected_article}"
    )

    print(
        f"Retrieved Articles: "
        f"{retrieved_articles}"
    )

    # -----------------------------------
    # TOP-K ACCURACY
    # -----------------------------------

    if expected_article in retrieved_articles:

        print("Top-K Result: CORRECT")

        correct_retrievals += 1

    else:

        print("Top-K Result: INCORRECT")

    # -----------------------------------
    # TOP-1 ACCURACY
    # -----------------------------------

    if len(retrieved_articles) > 0:

        if retrieved_articles[0] == expected_article:

            print("Top-1 Result: CORRECT")

            top1_correct += 1

        else:

            print("Top-1 Result: INCORRECT")

# -----------------------------------
# FINAL METRICS
# -----------------------------------

topk_accuracy = (
    correct_retrievals
    / total_questions
) * 100

top1_accuracy = (
    top1_correct
    / total_questions
) * 100

print("\n" + "="*60)
print("FINAL EVALUATION RESULTS")
print("="*60)

print(
    f"\nTotal Questions: "
    f"{total_questions}"
)

print(
    f"Correct Top-K Retrievals: "
    f"{correct_retrievals}"
)

print(
    f"Correct Top-1 Retrievals: "
    f"{top1_correct}"
)

print(
    f"\nTop-K Retrieval Accuracy: "
    f"{topk_accuracy:.2f}%"
)

print(
    f"Top-1 Retrieval Accuracy: "
    f"{top1_accuracy:.2f}%"
)

# -----------------------------------
# PERFORMANCE ANALYSIS
# -----------------------------------

if top1_accuracy >= 90:

    print(
        "\nPerformance: EXCELLENT"
    )

elif top1_accuracy >= 75:

    print(
        "\nPerformance: GOOD"
    )

elif top1_accuracy >= 50:

    print(
        "\nPerformance: AVERAGE"
    )

else:

    print(
        "\nPerformance: NEEDS IMPROVEMENT"
    )

print("\n" + "="*60)