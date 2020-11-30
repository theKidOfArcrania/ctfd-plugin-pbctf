import math

from CTFd.utils.modes import get_model
from CTFd.models import Solves, db
from CTFd.plugins.dynamic_challenges import DynamicValueChallenge

@classmethod
def calculate_value(cls, challenge):
    Model = get_model()

    solve_count = (
        Solves.query.join(Model, Solves.account_id == Model.id)
        .filter(
            Solves.challenge_id == challenge.id,
            Model.hidden == False,
            Model.banned == False,
        )
        .count()
    )

    # If the solve count is 0 we shouldn't manipulate the solve count to
    # let the math update back to normal
    if solve_count != 0:
        # We subtract -1 to allow the first solver to get max point value
        solve_count -= 1

    # It is important that this calculation takes into account floats.
    # Hence this file uses from __future__ import division
    # Changed in favor of a better decay formula
    value = ((challenge.initial - challenge.minimum) / 
            (1 + solve_count / challenge.decay)) + challenge.minimum

    value = math.ceil(value)

    if value < challenge.minimum:
        value = challenge.minimum

    challenge.value = value
    db.session.commit()
    return challenge

def load(app):
    DynamicValueChallenge.calculate_value = calculate_value
