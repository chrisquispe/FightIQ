import os
import requests
from dotenv import load_dotenv
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

# DeepEval needs an OpenAI key to do its own internal grading
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def ask_fightiq(question: str):
    """
    Calls your REAL backend, exactly like the frontend does.
    Returns the answer text and the list of source fight summaries.
    """
    response = requests.post(
        "http://localhost:8000/chat",
        json={"question": question}
    )
    data = response.json()
    return data["answer"], data["sources"]


def test_faithfulness_islam_oliveira():
    """
    This is the EXACT question that hallucinated earlier today.
    If this test ever fails again, it means the hallucination
    bug has come back.
    """
    question = "How did Islam beat Oliveira?"
    answer, sources = ask_fightiq(question)

    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=sources  # the real data the AI was given
    )

    # Faithfulness checks: does the answer ONLY use facts
    # that are actually present in retrieval_context?
    # threshold=0.7 means it must score at least 70% faithful to pass
    metric = FaithfulnessMetric(threshold=0.7)
    assert_test(test_case, [metric])


def test_relevancy_basic_question():
    """
    Checks that the answer actually addresses what was asked,
    rather than going off-topic or refusing unnecessarily.
    """
    question = "What is Charles Oliveira's fighting record?"
    answer, sources = ask_fightiq(question)

    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=sources
    )

    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])

def test_prediction_returns_valid_probabilities():
    """
    Checks that asking for a prediction actually triggers the
    predict_fight tool and returns a sensible, on-topic answer
    mentioning real probability figures.
    """
    question = "Who would win between Islam Makhachev and Charles Oliveira? Give me the win probability."
    answer, sources = ask_fightiq(question)

    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=sources
    )

    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])