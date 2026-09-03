from app.models.disorder import Disorder
from app.models.user import ROLE_ADMIN, User

DEFAULT_DISORDERS = [
    {
        "name": "Depression",
        "description": (
            "This study examines Google search interest relating to "
            "depression, a common mental health condition characterised by "
            "persistent low mood and loss of interest in activities."
        ),
        "search_term": "depression",
        "category": "Mental Health",
    },
    {
        "name": "Anxiety",
        "description": (
            "This study examines Google search interest relating to anxiety, "
            "encompassing generalised anxiety and related conditions."
        ),
        "search_term": "anxiety",
        "category": "Mental Health",
    },
    {
        "name": "OCD",
        "description": (
            "This study examines Google search interest relating to "
            "obsessive-compulsive disorder (OCD)."
        ),
        "search_term": "OCD",
        "category": "Mental Health",
    },
    {
        "name": "PTSD",
        "description": (
            "This study examines Google search interest relating to "
            "post-traumatic stress disorder (PTSD)."
        ),
        "search_term": "PTSD",
        "category": "Mental Health",
    },
    {
        "name": "Bipolar Disorder",
        "description": (
            "This study examines Google search interest relating to bipolar "
            "disorder."
        ),
        "search_term": "bipolar disorder",
        "category": "Mental Health",
    },
    {
        "name": "Eating Disorders",
        "description": (
            "This study examines Google search interest relating to eating "
            "disorders, including anorexia and bulimia."
        ),
        "search_term": "eating disorder",
        "category": "Mental Health",
    },
]


def seed_defaults(app):
    with app.app_context():
        if Disorder.count() == 0:
            for d in DEFAULT_DISORDERS:
                Disorder.create(**d)
            app.logger.info("Seeded %d default disorders.", len(DEFAULT_DISORDERS))

        if User.count() == 0 or not User.get_by_email(app.config["ADMIN_EMAIL"]):
            if not User.email_exists(app.config["ADMIN_EMAIL"]):
                User.create(
                    name=app.config["ADMIN_NAME"],
                    email=app.config["ADMIN_EMAIL"],
                    password=app.config["ADMIN_PASSWORD"],
                    role=ROLE_ADMIN,
                    institution="MindTrends UK",
                )
                app.logger.info(
                    "Seeded default administrator account: %s", app.config["ADMIN_EMAIL"]
                )
