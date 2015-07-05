""" Short description """

from datetime import date
import re
from decimal import Decimal
import locale


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

    report_args = {}

    # Report-Arguments

    want_scope = False

    # Does this report want "scope"-arguments?

    want_csv = False

    # Does this report want "csv" arguments?

    def get_args(self, parser):

        """
        Fill an argparse Subparser with arguments needed for this report

        The superclass method also reacts to want_scope and want_csv and
        automatically adds these parameters to the argument parser.

        :param parser: The argparse subparser
        """

        if self.want_csv:

            self.get_args_csv(parser)

        if self.want_scope:

            self.get_args_scope(parser)

        pass

    def parse_args(self, args):

        """
        Check the args for sanity. Individual reports should call the super
        method or set self.args=args

        The superclass method also checks for scope and csv arguments,
        if needed.

        These arguments are afterwards available in self.report_args.

        :param args: Arguments parsed
        :return: Wether the arguments are sane
        """

        if self.want_csv:

            if not self.parse_args_csv(args):

                return False

        if self.want_scope:

            if not self.parse_args_scope(args):

                return False

        self.args = args

        return True

    def report(self):

        """
        Execute the report
        :return: The report as a string
        """

        pass

    def get_args_scope(self, parser):

        """
        Helper for the "scope"-argument component

        Adds self.report_args["scope"] and ["scope_value"], if the arguments
        can be parsed.
        """

        parser.add_argument(
            "-s",
            "--scope",
            dest="scope",
            default="month",
            help="Scope for the report (month, quarter, year)"
        )

        parser.add_argument(
            "-d",
            "--scopevalue",
            dest="scopevalue",
            default="_now",
            help="Value of scope (for example 20149, 20142, 2014"
                 "for month/quarter/year scopes)"
        )

    def get_args_csv(self, parser):

        """
        Helper for the CSV-argument component. Adds self.report_args[
        "csv_delimiter"] once parsed.

        :param parser:
        :return:
        """

        parser.add_argument(
            "-e",
            "--delimiter",
            dest="delimiter",
            default=",",
            help="CSV-Delimiter for report output"
        )

    def parse_args_scope(self, args):

        """
        Sanity check for scope arguments

        :param args:
        :return:
        """

        if args.scope not in ["month", "quarter", "year"]:

            self.logger.error("Invalid scope specified (%s)" % args.scope)

            return False

        else:

            self.report_args["scope"] = args.scope

        if args.scopevalue == "_now":

            # Generate the current date

            now = date.today()

            if self.report_args["scope"] == "month":

                self.report_args["scope_value"] = "%d%d" % (now.year, now.month)

            elif self.report_args["scope"] == "quarter":

                self.report_args["scope_value"] = "%d%d" % (
                    now.year,
                    int(now.month/4) + 1
                )

            else:

                self.report_args["scope_value"] = str(now.year)

        else:

            if (
                self.report_args["scope"] == "month" and
                    not re.match("^[\d]{5,6}$", args.scopevalue)
            ) or (
                self.report_args["scope"] == "quarter" and
                    not re.match("^[\d]{5}$", args.scopevalue)
            ) or (
                self.report_args["scope"] == "year" and
                    not re.match("^[\d]{4}$", args.scopevalue)
            ):

                self.logger.error(
                    "Invalid scope value specified (%s) for "
                    "scope (%s)" % (
                        args.scopevalue,
                        self.report_args["scope"]
                    )
                )

                return False

            else:

                self.report_args["scope_value"] = args.scopevalue

        return True

    def parse_args_csv(self, args):

        """
        Sanity check for csv arguments

        :param args:
        :return:
        """

        self.report_args["csv_delimiter"] = args.delimiter

        return True

    def get_scope_filters(self):

        """
        Calculate the scope filters for the API based on the given scope
        arguments

        :return:
        """

        scope_filters = []

        if self.report_args["scope"] == "year":

            scope_filters.append({"YEAR": self.report_args["scope_value"]})

        elif self.report_args["scope"] == "month":

            interpreted_scope = re.match(
                "^([\d]{4})([\d]*)$",
                self.report_args["scope_value"]
            )

            scope_filters.append({
                "YEAR": interpreted_scope.group(1),
                "MONTH": interpreted_scope.group(2)
            })

        elif self.report_args["scope"] == "quarter":

            interpreted_scope = re.match(
                "^([\d]{4})([\d])$",
                self.report_args["scope_value"]
            )

            month_start = (int(interpreted_scope.group(2)) - 1) * 3 + 1
            month_end = (int(interpreted_scope.group(2))) * 3 + 1

            for month in range(month_start, month_end):

                scope_filters.append({
                    "YEAR": interpreted_scope.group(1),
                    "MONTH": str(month)
                })

        return scope_filters

    def moneyfmt(self, value):

        """ Return a locale correct currency formated value """

        locale.setlocale(locale.LC_ALL, "")
        return locale.currency(value, symbol=True, grouping=True, international=True)

