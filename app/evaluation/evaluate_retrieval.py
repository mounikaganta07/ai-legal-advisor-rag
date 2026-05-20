from app.retrieval.hybrid_retriever import (
    hybrid_retrieve
)


test_questions = [

    # -------------------------------
    # Constitution
    # -------------------------------

    {
        "question": "What is Article 21?",
        "expected_type": "article",
        "expected_number": "21"
    },

    {
        "question": "Can the government take away personal liberty?",
        "expected_type": "article",
        "expected_number": "21"
    },

    {
        "question": "What are writs?",
        "expected_type": "article",
        "expected_number": "32"
    },

    {
        "question": "Can Article 21 be suspended during emergency?",
        "expected_type": "article",
        "expected_number": "359"
    },

    {
        "question": "Can Article 19 be suspended?",
        "expected_type": "article",
        "expected_number": "359"
    },

    # -------------------------------
    # Dowry Prohibition Act
    # -------------------------------

    {
        "question": "What is punishment for demanding dowry?",
        "expected_type": "section",
        "expected_number": "4"
    },

    {
        "question": "What are the charges for dowry?",
        "expected_type": "section",
        "expected_number": "3"
    },

    {
        "question": "What can a dowry prohibition officer do?",
        "expected_type": "section",
        "expected_number": "8B"
    },

    # -------------------------------
    # Domestic Violence Act
    # -------------------------------

    {
        "question": "Does verbal abuse come under domestic violence?",
        "expected_type": "section",
        "expected_number": "3"
    },

    {
        "question": "Can emotional abuse be domestic violence?",
        "expected_type": "section",
        "expected_number": "3"
    },

    {
        "question": "What protection can a woman get under domestic violence law?",
        "expected_type": "section",
        "expected_number": "9"
    }
]


correct_topk = 0
correct_top1 = 0
total_questions = len(test_questions)

print("\n" + "=" * 70)
print("LEGAL RAG RETRIEVAL EVALUATION")
print("=" * 70)


def get_doc_provision(doc):
    provision_type = str(
        doc.metadata.get("provision_type", "")
    ).lower()

    if provision_type == "article":
        number = str(
            doc.metadata.get("article_number", "")
        ).upper()

    elif provision_type == "section":
        number = str(
            doc.metadata.get("section_number", "")
        ).upper()

    else:
        number = "N/A"

    return provision_type, number


for index, item in enumerate(test_questions):

    question = item["question"]

    expected_type = item["expected_type"].lower()

    expected_number = item["expected_number"].upper()

    print(f"\nTest Case {index + 1}")
    print("-" * 50)
    print(f"Question: {question}")
    print(f"Expected: {expected_type.title()} {expected_number}")

    docs = hybrid_retrieve(question)

    retrieved = []

    for doc in docs:
        provision_type, number = get_doc_provision(doc)

        retrieved.append(
            f"{provision_type.title()} {number}"
        )

    print(f"Retrieved: {retrieved}")

    expected_label = (
        expected_type,
        expected_number
    )

    retrieved_labels = [
        get_doc_provision(doc)
        for doc in docs
    ]

    if expected_label in retrieved_labels:
        print("Top-K Result: CORRECT")
        correct_topk += 1
    else:
        print("Top-K Result: INCORRECT")

    if retrieved_labels:
        if retrieved_labels[0] == expected_label:
            print("Top-1 Result: CORRECT")
            correct_top1 += 1
        else:
            print("Top-1 Result: INCORRECT")


topk_accuracy = (
    correct_topk / total_questions
) * 100

top1_accuracy = (
    correct_top1 / total_questions
) * 100

print("\n" + "=" * 70)
print("FINAL EVALUATION RESULTS")
print("=" * 70)

print(f"Total Questions: {total_questions}")
print(f"Correct Top-K Retrievals: {correct_topk}")
print(f"Correct Top-1 Retrievals: {correct_top1}")
print(f"Top-K Retrieval Accuracy: {topk_accuracy:.2f}%")
print(f"Top-1 Retrieval Accuracy: {top1_accuracy:.2f}%")

if top1_accuracy >= 90:
    print("\nPerformance: EXCELLENT")
elif top1_accuracy >= 75:
    print("\nPerformance: GOOD")
elif top1_accuracy >= 50:
    print("\nPerformance: AVERAGE")
else:
    print("\nPerformance: NEEDS IMPROVEMENT")

print("\n" + "=" * 70)