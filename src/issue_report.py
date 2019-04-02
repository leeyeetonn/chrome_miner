import matplotlib.pyplot as plt


class IssueReport:
    def __init__(self, report_type, data):
        self.type = report_type    # type include RFE, BUG, REFAC
        self.data = data

    # get median time difference between upload and push
    def median_upush_timediff(self):
        series = self.data['upload_push_timediff']
        return series.median()

    # get the ratio of unit-tested commits
    def unittest_ratio(self):
        col = self.data['is_unittested']
        ratio = col.value_counts()[True] / col.size
        return round(ratio, 4)

    # get num_revisions
    def num_revisions(self):
        return self.data['num_revisions']

    # get time difference between upload and push
    def upush_timediff(self):
        return self.data['upload_push_timediff']
