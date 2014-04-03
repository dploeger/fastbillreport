""" Short description """


class Report(object):

    """ A base class for fastbill reports
    """

    description = ""

    # A descriptive text about this report

    client = None

    # The fastbill client wrapper

    logger = None

    # Logging class

    args = None

    # Parsed arguments from the command line

    special_args = False

    # Does this report need special arguments from the command line?

    def get_args(self, parser):

        """
        Fill an argparse Subparser with arguments needed for this report
        :param parser: The argparse subparser
        """

        pass

    def parse_args(self, args):

        """
        Check the args for sanity. Individual reports should call the super
        method or set self.args=args
        :param args: Arguments parsed
        :return: Wether the arguments are sane
        """

        self.args = args

        return True

    def report(self):

        """
        Execute the report
        :return: The report as a string
        """

        ""