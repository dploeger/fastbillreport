""" fastbillreport

A financial report generator out of Fastbill income and expenses as a basis for
monthly/quarterly/yearly reports, the german USTvA report and the german EueR

"""

from fastbill import FastbillWrapper
from argparse import ArgumentParser
import reports
import logging
import os


def load_reports():

    """ Load all reports and return the report objects in a dict "name" =>
    object
    :return: The report objects
    """

    import pkgutil
    import inspect

    loaded_reports = {}

    for importer, modname, ispkg in pkgutil.iter_modules(reports.__path__):

        report_loader = importer.find_module(modname, reports.__path__)
        report_module = report_loader.load_module(report_loader.fullname)
        report_class = modname.capitalize()

        for (name, obj) in inspect.getmembers(report_module):

            if name == report_class:

                loaded_reports[modname] = obj()

    return loaded_reports


if __name__ == '__main__':

    # Parse arguments

    parser = ArgumentParser(
        description="Fastbill Report Generator"
    )

    parser.add_argument(
        '-a',
        '--api',
        dest="api",
        default="https://my.fastbill.com/api/1.0/api.php",
        help="Fastbill-API-URL (defaults to "
             "https://my.fastbill.com/api/1.0/api.php)"
    )

    parser.add_argument(
        '-u',
        '--user',
        required=True,
        dest="user",
        help="Username"
    )

    parser.add_argument(
        '-k',
        '--key',
        required=True,
        dest="key",
        help="Fastbill API Key"
    )

    parser.add_argument(
        '-q',
        '--quiet',
        action="store_true",
        dest="quiet",
        help="Be quiet doing things"
    )

    parser.add_argument(
        '-d',
        '--debug',
        dest="debug",
        help="Debugging mode"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="Verbose mode"
    )

    # Add subparsers for reports

    subparser = parser.add_subparsers(
        help="Report to run",
        dest="report"
    )

    loaded_reports = load_reports()

    for (name, obj) in loaded_reports.iteritems():

        if obj.special_args:

            report_parser = subparser.add_parser(name, help=obj.description)

            obj.get_args(report_parser)

    args = parser.parse_args()

    # Interpret arguments

    # Set up logging

    if args.quiet:
        logging.basicConfig(level=logging.NOTSET)

    elif args.verbose:
        logging.basicConfig(level=logging.INFO)

    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)

    else:
        logging.basicConfig(level=logging.ERROR)

    loaded_reports[args.report].logger = logging.getLogger(args.report)

    # Parse report arguments

    if not loaded_reports[args.report].parse_args(args):

        parser.print_help()

        exit(1)

    # Connect to fastbill

    client = FastbillWrapper(args.user, args.key, args.api)

    loaded_reports[args.report].client = client

    # Start report

    print os.linesep.join(loaded_reports[args.report].report())