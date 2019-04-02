class IssueReport:
    def __init__(self, report_type, data):
        self.type = report_type    # type include RFE, BUG, REFAC
        self.data = data

    # get median time difference between upload and push
    def median_upush_timediff(self):
        series = self.data['upload_push_timediff']
        return series.median()

    # number of instances that were unittested
    def num_unittested(self):
        col = self.data['is_unittested']
        num = col.value_counts()[True]
        return num

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

    # number of lines modified
    def lines_modified(self):
        return self.data['lines_modified']

    # number of lines removed
    def lines_removed(self):
        return self.data['lines_removed']

    # number of lines added
    def lines_added(self):
        return self.data['lines_added']

    # number of comments
    def num_comments(self):
        return self.data['num_comments']

    def report_misclass(self, mapping):
        if self.type not in mapping:
            print('Error: assigned type not in mapping')
            return None, None

        # get the corresponding manual classification category
        man_cat = mapping[self.type]
        mis_class = self.data[self.data['final_category'] != man_cat]
        right_class = self.data[self.data['final_category'] == man_cat]

        return right_class, mis_class
