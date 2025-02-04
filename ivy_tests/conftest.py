# global
import os
import redis
from hypothesis import settings, HealthCheck
from hypothesis.database import (
    MultiplexedDatabase,
    ReadOnlyDatabase,
    DirectoryBasedExampleDatabase,
)
from hypothesis.extra.redis import RedisExampleDatabase


hypothesis_cache = os.getcwd() + "/.hypothesis/examples/"
redis_connect_dev = None
redis_connect_master = None
try:
    os.makedirs(hypothesis_cache)
except FileExistsError:
    pass


def is_db_available(master=False, credentials=None):
    global redis_connect_dev, redis_connect_master
    redis_connect_local = None
    if master:
        redis_connect_master = redis.Redis.from_url(
            url=credentials[0], password=credentials[1]
        )
        redis_connect_local = redis_connect_master
    else:
        redis_connect_dev = redis.Redis.from_url(
            url="redis://redis-17011.c259.us-central1-2.gce.cloud.redislabs.com:17011",
            username="general_use",
            password="Hypothesiscache@123",
            max_connections=2,
        )
        redis_connect_local = redis_connect_dev
    try:
        redis_connect_local.get("b")
    except redis.exceptions.ConnectionError:
        print("Fallback to DirectoryBasedExamples")
        return False
    return True


def pytest_addoption(parser):
    parser.addoption(
        "-N",
        "--num-examples",
        action="store",
        default=25,
        type=int,
        help="set max examples generated by Hypothesis",
    )
    parser.addoption(
        "--deadline",
        action="store",
        default=500000,
        type=int,
        help="set deadline for testing one example",
    )
    parser.addoption(
        "--ivy-tb",
        action="store",
        default="full",
        type=str,
        help="ivy traceback",
    )
    parser.addoption(
        "-D",
        "--deterministic",
        action="store_true",
        default=False,
        help=(
            "Use hash of the test function as a seed, "
            "disables Redis database if exists."
        ),
    )


def pytest_configure(config):
    profile_settings = {}
    getopt = config.getoption
    max_examples = getopt("--num-examples")
    deadline = getopt("--deadline")
    if (
        os.getenv("REDIS_URL", default=False)
        and os.environ["REDIS_URL"]
        and is_db_available(
            master=True,
            credentials=(os.environ["REDIS_URL"], os.environ["REDIS_PASSWD"]),
        )
    ):
        print("Update Database with examples !")
        profile_settings["database"] = RedisExampleDatabase(
            redis_connect_master, key_prefix=b"hypothesis-example:"
        )

    elif not os.getenv("REDIS_URL") and is_db_available():
        print("Use Database in ReadOnly Mode with local caching !")
        shared = RedisExampleDatabase(
            redis_connect_dev, key_prefix=b"hypothesis-example:"
        )
        profile_settings["database"] = MultiplexedDatabase(
            DirectoryBasedExampleDatabase(path=hypothesis_cache),
            ReadOnlyDatabase(shared),
        )

    else:
        print("Database unavailable, local caching only !")
        profile_settings["database"] = DirectoryBasedExampleDatabase(
            path=hypothesis_cache
        )

    if max_examples:
        profile_settings["max_examples"] = max_examples
    if deadline:
        profile_settings["deadline"] = deadline

    if config.getoption("deterministic"):
        profile_settings["database"] = None
        profile_settings["derandomize"] = True

    settings.register_profile(
        "ivy_profile",
        **profile_settings,
        suppress_health_check=(HealthCheck(3), HealthCheck(2), HealthCheck(1)),
        print_blob=True,
    )
    settings.load_profile("ivy_profile")
