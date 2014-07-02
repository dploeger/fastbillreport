""" Report about figures for the german UstVa tax report """

from reports import Report


class Ustva(Report):

    description = "Report about figures for the german UstVa tax report"

    special_args = True

    want_scope = True

    want_csv = True

    def report(self):

        # Create scope filter

        scope_filters = self.get_scope_filters()

        # Calculate figures

        ustva = {

            # 81 - Steuerpflichtige Umsaetze - 19%

            "81": 0,

            # 86 - Steuerpflichtige Umsaetze - 7%

            "86": 0,

            # 66 - Vorsteuerbetraege aus Rechnungen von anderen Unternehmern

            "66": 0,

            # 83 - Verbleibende Umsatzsteuer-Vorauszahlung / Verbleibender
            # Ueberschuss

            "83": 0

        }

        for scope_filter in scope_filters:

            # Figures from invoices

            tmp = self.client.invoice_get(
                filter=scope_filter
            )

            for invoice in tmp["INVOICES"]:

                if invoice["IS_CANCELED"] == "1":

                    # Skip canceled invoices

                    continue

                vat_sum = {
                    "19.00": 0,
                    "7.00": 0
                }

                for vat_item in invoice["VAT_ITEMS"]:

                    vat_sum[vat_item["VAT_PERCENT"]] += float(vat_item[
                        "VAT_VALUE"])

                ustva["81"] += vat_sum["19.00"]
                ustva["86"] += vat_sum["7.00"]

            tmp = self.client.expense_get(filter=scope_filter)

            for expense in tmp["EXPENSES"]:

                for vat_item in expense["VAT_ITEMS"]:

                    ustva["66"] += float(vat_item["VAT_VALUE"])

        ustva["83"] = ustva["81"] + ustva["86"] - ustva["66"]

        report = ["UstVa-Bericht"]

        for key, value in ustva.iteritems():

            report.append("Zeile %s: %s" % (key, self.moneyfmt(value)))

        return report