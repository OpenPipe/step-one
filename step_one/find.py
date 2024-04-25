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


def find_posts(need: str = DEFAULT_NEED, log=print):
    # need_from_user_perspective = restate_need(need)
    # log("restated need:", need_from_user_perspective)

    user_groups = generate_user_groups(need)
    log("searching for reddits used by the following user groups:")
    for user_group in user_groups:
        log(user_group)

    subreddits = search_subreddits(need, user_groups)

    # args = {
    #     "verbose": True,
    #     "limit": 2,
    #     "sort": "relevance",
    #     "make_hard_links": True,
    #     "subreddit": subreddit_names,
    #     "search": need_from_user_perspective,
    # }

    # config = Configuration()
    # config.process_arguments(args)

    # first_round_posts = search_posts(config)

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

    # for post in first_round_posts:
    #     print(f"https://reddit.com{post['permalink']}")
    #     print(post["title"])
    #     print(post["selftext"][:1000])

    #     print("\n\n")

    # first_round_posts = search_subreddits(config, relevance_question)
    # print(f"Found {len(first_round_posts)} posts after filtering by need (round 1).")

    # subreddit = filter_subreddits(first_round_posts, subreddit_relevance_question)

    # print("subreddits: ", subreddit)
    # config.subreddit = subreddit
    # config.limit = 100

    # second_round_posts = search_subreddits(config, definite_question)

    posts = filter_by_need(first_round_posts, need)
    log(f"Found {len(posts)} posts after filtering by need.")

    for post in posts:
        print(f"https://reddit.com{post['permalink']}")
        print(post["title"])
        if "summary" in post:
            print(post["summary"])
        # print(post)
        print()
    return posts


# def search_subreddits(config: Configuration, question: str):
#     original_posts = search_posts(config)

#     most_relevant_posts = original_posts[:NUM_POSTS_INCLUDED_PURELY_BY_RELEVANCE]
#     less_relevant_posts = original_posts[NUM_POSTS_INCLUDED_PURELY_BY_RELEVANCE:]

#     less_relevant_posts = filter_by_keyphrase(less_relevant_posts, keyphrases)
#     print(f"Found {len(less_relevant_posts)} posts after filtering by keyphrase.")

#     # Add the most relevant posts to the list, even if they don't contain the keyphrase
#     posts = most_relevant_posts + less_relevant_posts

#     return filter_by_need(posts, question)
