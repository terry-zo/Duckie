class channelId(object):
    """A class to organize discord channels."""

    def __init__(self):
        self.channels = {
            "hqTrivia": {
                "451558169773211648"
            },
            "csTrivia": {
                "451558147686006785"
            }
        }


class crowdsourceInformation(object):
    """A class used to provide information to a function ready to fetch answers."""

    def __init__(self, triviaGame, triviaQuestion, triviaRound, triviaAnswers):
        self.triviaGame = triviaGame
        self.triviaQuestion = triviaQuestion
        self.triviaRound = triviaRound
        self.triviaAnswers = {str(counter): {'triviaAnswers': value, 'triviaCount': 0} for counter, value in enumerate(triviaAnswers, 1)}
