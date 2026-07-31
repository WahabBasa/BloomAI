"""Lazy construction of the OpenAI client shared by the three agents.

The client used to be built at import time inside each agent module, so
importing anything that reached `recall_service` -- which Django does when it
loads `views.py` -- required an API key. Building it on demand keeps
`manage.py` usable on a machine that has never seen a key.
"""

import functools
import os

import instructor
import openai

MISSING_KEY_MESSAGE = (
    "OPENAI_API_KEY is not set. Add it to Backend/.env (see Backend/.env.example) "
    "before uploading a document or submitting an answer."
)


def require_api_key() -> str:
    """Return the OpenAI API key, raising only when a key is actually needed."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(MISSING_KEY_MESSAGE)
    return api_key


@functools.lru_cache(maxsize=1)
def get_client() -> instructor.Instructor:
    """Return the instructor-wrapped OpenAI client.

    Caching this is safe and deliberate: the client holds a connection pool but
    no per-request state. The *agents* are the stateful part and are built fresh
    per request -- see the factories in this package.
    """
    return instructor.from_openai(openai.OpenAI(api_key=require_api_key()))
