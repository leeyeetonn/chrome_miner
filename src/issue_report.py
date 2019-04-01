class IssueReport:
    def __init__(self, type, data):
        self.type = type    # type include RFE, BUG, REFAC
        self.data = data

    # get median time difference between upload and push
    def median_upush_timediff(self):
        series = self.data['upload_push_timediff']
        return series.median()

