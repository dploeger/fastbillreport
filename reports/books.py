""" A monthly/quarterly/yearly report of incomes and expenses
"""

from reports import Report
import re


class Books(Report):

    description = "A monthly/quarterly/yearly report of incomes and " \
                  "expenses"

    special_args = True

    want_csv = True

    want_scope = True

    def report(self):

        # Create scope filter

        scope_filters = self.get_scope_filters()

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

                if invoice["IS_CANCELED"] == "1":

                    # Skip canceled invoices

                    continue

                name = " ".join([invoice["FIRST_NAME"], invoice["LAST_NAME"]])

                if "ORGANIZATION" in invoice and invoice["ORGANIZATION"] != "":

                    name = "%s (%s)" % (invoice["ORGANIZATION"], name)

                vat_sum = {

                }

                for vat_item in invoice["VAT_ITEMS"]:

                    if vat_item["VAT_PERCENT"] not in vat_sum:

                        vat_sum[vat_item["VAT_PERCENT"]] = 0

                    if vat_item["VAT_PERCENT"] not in income_vats:

                        income_vats.append(vat_item["VAT_PERCENT"])

                    vat_sum[vat_item["VAT_PERCENT"]] += vat_item["VAT_VALUE"]

                incomes.append({
                    "date": invoice["INVOICE_DATE"],
                    "paid_date": invoice["PAID_DATE"],
                    "name": name,
                    "title": invoice["INVOICE_TITLE"],
                    "subtotal": invoice["SUB_TOTAL"],
                    "total": invoice["TOTAL"],
                    "vat": vat_sum,
                    "note": invoice["NOTE"]
                })

            tmp = self.client.expense_get(filter=scope_filter)

            for expense in tmp["EXPENSES"]:

                vat_sum = {

                }

                for vat_item in expense["VAT_ITEMS"]:

                    if vat_item["VAT_PERCENT"] not in vat_sum:

                        vat_sum[vat_item["VAT_PERCENT"]] = 0

                    if vat_item["VAT_PERCENT"] not in expense_vats:

                        expense_vats.append(vat_item["VAT_PERCENT"])

                    vat_sum[vat_item["VAT_PERCENT"]] += float(
                        vat_item["VAT_VALUE"]
                    )

                expenses.append({
                    "date": expense["INVOICE_DATE"],
                    "paid_date": expense["PAID_DATE"],
                    "name": expense["ORGANIZATION"],
                    "title": "",
                    "subtotal": float(expense["SUB_TOTAL"]),
                    "total": float(expense["TOTAL"]),
                    "vat": vat_sum,
                    "note": expense["NOTE"]
                })

        # Output report

        # Incomes

        report = []

        report_data = {
            "INCOME": {
                "data": incomes,
                "vats": income_vats
            },
            "EXPENSES": {
                "data": expenses,
                "vats": expense_vats
            }
        }

        for key, data in report_data.iteritems():

            report.append(key)

            header = self.report_args["csv_delimiter"].join(
                ["date", "paid_date", "name", "title"] +
                data["vats"] +
                ["subtotal", "total", "note"]
            )

            report.append(header)

            data_sum = {
                "subtotal": 0,
                "total": 0
            }

            for row in data["data"]:

                columns = [
                    row["date"],
                    row["paid_date"],
                    row["name"],
                    row["title"]
                ]

                for vat in income_vats:

                    if not vat in data_sum:
                        data_sum[vat] = 0

                    if vat in row["vat"]:

                        data_sum[vat] += row["vat"][vat]
                        columns.append(str(self.moneyfmt(row["vat"][vat])))

                    else:

                        columns.append("0")

                columns.append(str(self.moneyfmt(row["subtotal"])))
                data_sum["subtotal"] += row["subtotal"]
                columns.append(str(self.moneyfmt(row["total"])))
                data_sum["total"] += row["total"]
                columns.append(row["note"])

                report.append(self.report_args["csv_delimiter"].join(columns))

            sum_row = [
                "",
                "",
                "",
                ""
            ]

            for vat in data["vats"]:

                sum_row.append(str(self.moneyfmt(data_sum[vat])))

            sum_row.append(str(self.moneyfmt(data_sum["subtotal"])))
            sum_row.append(str(self.moneyfmt(data_sum["total"])))
            sum_row.append("")

            report.append(self.report_args["csv_delimiter"].join(sum_row))

            report.append("")

        return report