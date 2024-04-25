from reddit.configuration import Configuration
from reddit.search import search_posts_raw, search_subreddits

from step_one.filter import filter_by_need
from step_one.openAI import generate_user_groups


keyphrases = [
    "walk",
    "walking alone",
    "unsafe walking",
    "danger when walking",
    "walking around by myself",
    "walk by myself",
]

DEFAULT_NEED = "Forming new habits is hard"

TOTAL_POSTS_TO_SEARCH = 50

for i in range(len(keyphrases)):
    keyphrases[i] = keyphrases[i].lower()


def find_posts(
    need: str = DEFAULT_NEED, log=print, use_fine_tuned=False, openai_api_key=None
):

    user_groups = generate_user_groups(need=need)

    log("searching for reddits used by the following user groups:")
    for user_group in user_groups:
        log(user_group)

    subreddits = search_subreddits(need, user_groups)

    total_score = sum([subreddit["score"] ** 2 for subreddit in subreddits])

    first_round_posts = []
    log("Searching the following subreddits:")
    for subreddit in subreddits:
        log(f"r/{subreddit['name']}")
        # Bias toward the subreddits with the highest scores (most relevant).
        num_posts_to_include = (
            TOTAL_POSTS_TO_SEARCH * subreddit["score"] ** 2 // total_score
        )
        first_round_posts += search_posts_raw(
            need, subreddit["name"], num_posts_to_include
        )
    first_round_posts += search_posts_raw(need, None, 30)
    log(f"Checking {len(first_round_posts)} posts.")

    posts = filter_by_need(first_round_posts, need, use_fine_tuned, openai_api_key)
    log(f"Found {len(posts)} posts after filtering by need.")

    for post in posts:
        print(f"https://reddit.com{post['permalink']}")
        print(post["title"])
        if "summary" in post:
            print(post["summary"])
        # print(post)
        print()
    return posts
