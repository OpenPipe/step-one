from reddit.search import search_posts_raw

posts = search_posts_raw(
    problem="I need help with my computer",
    subreddit="techsupport",
    num_posts_to_include=5,
)
