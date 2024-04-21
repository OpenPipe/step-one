from openpipe import OpenAI
from typing import List
import ray
import instructor
from pydantic import BaseModel

client = instructor.from_openai(OpenAI())


class RestatedNeed(BaseModel):
    restated_need: str


def restate_need(need) -> str:
    completion = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {
                "role": "user",
                "content": f"""
Pretend you have the following need. State that need concisely in a single sentence from your perspective. The first word should be "I".

Need: {need}
""",
            },
        ],
        response_model=RestatedNeed,
    )

    return completion.restated_need


class GeneratedUserGroups(BaseModel):
    top_3_user_groups: List[str]


def generate_user_groups(need) -> List[str]:
    completion = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {
                "role": "user",
                "content": """
                List 7 user groups who have the following problem and a short reason why they have it.
                Then, list the top 3 groups who have the problem the most.
                """,
            },
            {"role": "user", "content": f"Problem: {need}"},
        ],
        response_model=GeneratedUserGroups,
    )
    return completion.top_3_user_groups


class SummarizedPost(BaseModel):
    summary: str


def summarize(post, need) -> str:
    try:
        post_content = post["selftext"] or "No content"
        if len(post_content) > 8000:
            post_content = post_content[:8000]
        completion = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {
                    "role": "user",
                    "content": f"""
                        Here is a reddit post I am interested in:
                        title: {post["title"]}
                        contents: {post_content}
                        Who is this person? What are they asking for? How does this post relate to the following need?
                        Need: {need}
                    """,
                },
            ],
            response_model=SummarizedPost,
        )
        return completion.summary.strip()
    except:
        return None


class DiscernApplicabilityResult(BaseModel):
    applicable: bool
    explanation: str


def discern_applicability(post, need) -> bool:
    post_content = post["selftext"] or "No content"
    if len(post_content) > 8000:
        post_content = post_content[:8000]

    try:
        completion = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {
                    "role": "user",
                    "content": f"""
                        Here is the title and content of a reddit post I am interested in:
                        title: {post["title"]}
                        content: {post_content}

                        Does the person writing this post explicitly mention that they have the following need?
                        {need}

                        Explain your reasoning before you answer. Answer true if the person has the need, or false otherwise. Label your true/false answer with "Answer:".
                    """,
                },
            ],
            response_model=DiscernApplicabilityResult,
        )

        return completion.applicable

    except:
        return False


class PostRelevanceScore(BaseModel):
    relevance_score: int


def score_post_relevance(post, need) -> int:
    try:
        completion = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {
                    "role": "user",
                    "content": f"""
                        Here is the title and summary of a reddit post I am interested in:
                        title: {post["title"]}
                        summary: {post["summary"]}

                        On a scale of 1 to 10, how likely is it that the person writing this post has the following need? If you are not sure, make your best guess, or answer 1.
                        Need: {need}

                        Answer one integer between 1 and 10.
                    """,
                },
            ],
            response_model=PostRelevanceScore,
        )

        return completion.relevance_score

    except:
        return 1


class SubredditRelevanceScore(BaseModel):
    relevance_score: int


@ray.remote
def score_subreddit_relevance(subreddit, need):
    formatted_score_subreddit_relevance_prompt = f"""
Here is a subreddit I am interested in: {subreddit["name"]}
Here is the description of the subreddit: {subreddit["description"]}

Please answer the following question. If you are not sure, answer 1:
On a scale of 1 to 10, how likely is it that anyone in this subreddit has the following need?

Need: {need}

Answer one integer between 1 and 10.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": formatted_score_subreddit_relevance_prompt},
        ],
        response_model=SubredditRelevanceScore,
    )

    relevance_score = response.relevance_score

    print(subreddit["name"])
    print(subreddit["description"])
    print(relevance_score)

    subreddit["score"] = relevance_score
    return subreddit
