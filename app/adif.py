from collections import OrderedDict
import os


class Adif:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.abs_path_to_file = os.path.abspath(path_to_file).replace("\\", '/')
        self.filename = os.path.basename(self.path_to_file)
        self.reports = []
        self.all_names = {}
        self.number_of_reports = 0

        # Read adif file
        file = open(self.path_to_file, 'r', errors='ignore')
        is_header = True
        for line in file:
            # Skip header
            if is_header:
                if '<eoh>' in line or '<EOH>' in line:
                    is_header = False
                continue

            # Read report line
            current_report = Report()
            line = line.split('<')[1:]
            for elem in line:
                # End of report
                if "eor>" in elem or "EOR" in elem:
                    current_report.eor()
                    self.reports.append(current_report)
                    break
                elem = elem.split('>')
                field_data = elem[1].strip()
                elem = elem[0].split(':')
                field_name = elem[0].lower()
                current_report.add_field(name=field_name, data=field_data)
        file.close()

        # Update variables
        self.number_of_reports = len(self.reports)
        self.update_vars()

    # Collect all field-names from the reports
    def update_vars(self):
        self.all_names = {}
        for report in self.reports:
            for name in report.names:
                if name not in self.all_names:
                    self.all_names[name] = 1
                else:
                    self.all_names[name] += 1

    # Change field-names for all reports
    def change_names(self, fields_to_rename):
        for field in fields_to_rename:
            for report in self.reports:
                report.rename_field(field, fields_to_rename[field])
        self.update_vars()

    # Delete fields of a certain name in all reports
    def del_fields(self, fields_to_del):
        for field in fields_to_del:
            for report in self.reports:
                report.del_field(field)
        self.update_vars()

    # Save adif file
    def save(self):
        # Remove old file (could be .txt)
        os.remove(self.path_to_file)

        # Start new file (is .adif)
        path = os.path.splitext(self.path_to_file)[0] + '.adif'
        file = open(path, 'w')
        file.write('<eoh>\n')
        for report in self.reports:
            file.write(report.get_adif() + '\n')
        file.close()
        return os.path.basename(path)


class Report:
    def __init__(self):
        self.fields = OrderedDict()
        self.names = None

    # Add a field
    def add_field(self, name, data):
        self.fields[name] = data

    # Change name of a field
    def rename_field(self, old_name, new_name):
        if old_name in self.fields:
            self.fields[new_name] = self.fields.pop(old_name)
        self.eor()

    # Delete a field of given name
    def del_field(self, name):
        if name in self.fields:
            del self.fields[name]
        self.eor()

    # Update variables at end of report
    def eor(self):
        self.names = self.fields.keys()

    # Get adif-line for this report
    def get_adif(self):
        ret_line = ''
        for name, value in self.fields.items():
            ret_line += '<' + name + ':' + str(int(len(value))) + '>' + value
        return ret_line + '<eor>'


# ---------- Testing ----------
if __name__ == '__main__':
    adif = Adif(r"C:\Users\Stefan Laptop\Desktop\logbuch_DL0YLM DA0YL_20170819 Karin.adif")
