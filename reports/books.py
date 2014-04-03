""" A monthly/quarterly/yearly report of incomes and expenses
"""

from reports import Report
import re
from datetime import date


class Books(Report):

    description = "A monthly/quarterly/yearly report of incomes and " \
                  "expenses"

    special_args = True

    scope = ""

    # The type of scope to report on

    scope_value = ""

    # The actual scope

    def get_args(self, parser):

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

        parser.add_argument(
            "-e",
            "--delimiter",
            dest="delimiter",
            default=",",
            help="CSV-Delimiter for report output"
        )

    def parse_args(self, args):
        super(Books, self).parse_args(args)

        if args.scope not in ["month", "quarter", "year"]:

            self.logger.error("Invalid scope specified (%s)" % args.scope)

            return False

        else:

            self.scope = args.scope

        if self.args.scopevalue == "_now":

            # Generate the current date

            now = date.today()

            if self.scope == "month":

                self.scope_value = "%d%d" % (now.year, now.month)

            elif self.scope == "quarter":

                self.scope_value = "%d%d" % (now.year, int(now.month/4) + 1)

            else:

                self.scope_value = str(now.year)

        else:

            if (
                self.scope == "month" and
                    not re.match("^[\d]{5,6}$", self.args.scopevalue)
            ) or (
                self.scope == "quarter" and
                    not re.match("^[\d]{5}$", self.args.scopevalue)
            ) or (
                self.scope == "year" and
                    not re.match("^[\d]{4}$", self.args.scopevalue)
            ):

                self.logger.error(
                    "Invalid scope value specified (%s) for "
                    "scope (%s)" % (
                        self.args.scopevale,
                        self.scope
                    )
                )

                return False

            else:

                self.scope_value = self.args.scopevalue

        return True

    def report(self):

        # Create scope filter

        scope_filters = []

        if self.scope == "year":

            scope_filters.append({ "YEAR": self.scope_value })

        elif self.scope == "month":

            interpreted_scope = re.match("^([\d]{4})([\d]*)$", self.scope_value)

            scope_filters.append({
                "YEAR": interpreted_scope.group(1),
                "MONTH": interpreted_scope.group(2)
            })

        elif self.scope == "quarter":

            interpreted_scope = re.match("^([\d]{4})([\d])$", self.scope_value)

            month_start = (int(interpreted_scope.group(2)) - 1) * 3 + 1
            month_end = (int(interpreted_scope.group(2))) * 3 + 1

            for month in range(month_start, month_end):

                scope_filters.append({
                    "YEAR": interpreted_scope.group(1),
                    "MONTH": str(month)
                })

        # Get invoices of current scope

        incomes = []
        income_vats = []
        expenses = []
        expense_vats = []

        for scope_filter in scope_filters:

            tmp = self.client.invoice_get(
                filter=scope_filter
            )

            for invoice in tmp["INVOICES"]:

                if invoice["IS_CANCELED"] == 1:

                    # Skip canceled invoices

                    continue

                name = " ".join([invoice["FIRST_NAME"], invoice["LAST_NAME"]])

                if "ORGANIZATION" in invoice:

                    name = "%s (%s)" % (invoice["ORGANIZATION"], name)

                vat_sum = {

                }

                for vat_item in invoice["VAT_ITEMS"]:

                    if vat_item["VAT_PERCENT"] not in vat_sum:

                        vat_sum[vat_item["VAT_PERCENT"]] = 0

                    if vat_item["VAT_PERCENT"] not in income_vats:

                        income_vats.append(vat_item["VAT_PERCENT"])

                    vat_sum[vat_item["VAT_PERCENT"]] += round(
                        vat_item["VAT_VALUE"],
                        2
                    )


                incomes.append({
                    "date": invoice["INVOICE_DATE"],
                    "paid_date": invoice["PAID_DATE"],
                    "name": name,
                    "title": invoice["INVOICE_TITLE"],
                    "subtotal": round(invoice["SUB_TOTAL"], 2),
                    "total": round(invoice["TOTAL"], 2),
                    "vat": vat_sum,
                    "note": invoice["NOTE"]
                })

            tmp = self.client.expense_get(filter=scope_filter)

            for expense in tmp["EXPENSES"]:

                vat_sum = {

                }

                for vat_item in invoice["VAT_ITEMS"]:

                    if vat_item["VAT_PERCENT"] not in vat_sum:

                        vat_sum[vat_item["VAT_PERCENT"]] = 0

                    if vat_item["VAT_PERCENT"] not in expense_vats:

                        expenses.append(vat_item["VAT_PERCENT"])

                    vat_sum[vat_item["VAT_PERCENT"]] += vat_item["VAT_VALUE"]

                expenses.append({
                    "date": invoice["INVOICE_DATE"],
                    "paid_date": invoice["PAID_DATE"],
                    "name": invoice["ORGANIZATION"],
                    "title": invoice["INVOICE_TITLE"],
                    "subtotal": invoice["SUB_TOTAL"],
                    "total": invoice["TOTAL"],
                    "vat": vat_sum,
                    "note": invoice["NOTE"]
                })

        # Output report

        # Incomes

        report = []

        header = self.args.delimiter.join(
            ["date", "paid_date", "name", "title"] +\
            income_vats +\
            ["subtotal", "total", "note"])

        report.append(header)

        for income in incomes:

            row = [
                income["date"],
                income["paid_date"],
                income["name"],
                income["title"]
            ]

            for vat in income_vats:

                if vat in income["vat"]:

                    row.append(str(income["vat"][vat]))

                else:

                    row.append("0")

            row.append(str(income["subtotal"]))
            row.append(str(income["total"]))
            row.append(income["note"])

            report.append(self.args.delimiter.join(row))

        report.append("")
        report.append("EXPENSES")

        return report