from teacher_dashboard.Assignment.constants.constants import PerformanceConfigConstant
from teacher_dashboard.Assignment.daos.assignment_student_question_dao import assignment_student_question_dao
from teacher_dashboard.Assignment.daos.assignment_student_dao import assignment_student_dao
from teacher_dashboard.Reporting.reporting_dao import reporting_dao
from collections import defaultdict


class PerformaceService:
    def calculate_performance_assignment_student_question(self, report_logs):
        step_hint_count = defaultdict(int)
        step_incorrect_count = defaultdict(int)
        is_complete = False

        for report_row in report_logs:
            if report_row.interaction_type == "EXPLICIT_HINT":
                step_hint_count[report_row.step_number] += 1
            if report_row.is_correct == False:
                step_incorrect_count[report_row.step_number] += 1
            if report_row.is_complete:
                is_complete = True

        # if not is_complete:
        #     return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L0.LEVEL

        max_step_hint_count = max(step_hint_count.values(), default=0)
        max_step_incorrect_count = max(
            step_incorrect_count.values(), default=0)

        max_incorrect_with_hint_count = max_step_hint_count + max_step_incorrect_count

        if(PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.INCORRECT_WITH_HINT_MIN_NUMBER <= max_incorrect_with_hint_count <= PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.INCORRECT_WITH_HINT_MAX_NUMBER):
            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.INCORRECT_WITH_HINT_MIN_NUMBER <= max_incorrect_with_hint_count <= PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.INCORRECT_WITH_HINT_MAX_NUMBER):
            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentQuestionConfig.L1.INCORRECT_WITH_HINT_MIN_NUMBER <= max_incorrect_with_hint_count <= PerformanceConfigConstant.AssignmentStudentQuestionConfig.L1.INCORRECT_WITH_HINT_MAX_NUMBER):
            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L0.LEVEL

    def calculate_performance_assignment_student_question_list(self, report_logs):

        question_reports = defaultdict(list)

        for report_row in report_logs:
            question_reports[(report_row.assignment_id,
                              report_row.student_id,
                              report_row.class_id,
                              report_row.question_id)].append(report_row)

        total_count = 0
        l3_count = 0
        l2_count = 0
        l1_count = 0
        l0_count = 0

        for assignment_id, student_id, class_id, question_id in question_reports:
            question_performance = self.calculate_performance_assignment_student_question(
                question_reports[(assignment_id, student_id, class_id, question_id)])

            total_count += 1
            if(question_performance == PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.LEVEL):
                l3_count += 1
            elif(question_performance == PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.LEVEL):
                l2_count += 1
            elif(question_performance == PerformanceConfigConstant.AssignmentStudentQuestionConfig.L1.LEVEL):
                l1_count += 1
            else:
                l0_count += 1

        return (total_count, l3_count, l2_count, l1_count, l0_count)

    def calculate_performance_assignment_student(self, report_logs):

        total_count, l3_count, l2_count, l1_count, white_count = self.calculate_performance_assignment_student_question_list(
            report_logs)

        if(total_count == 0):
            return PerformanceConfigConstant.AssignmentStudentConfig.L0.LEVEL

        if(total_count == white_count):
            return PerformanceConfigConstant.AssignmentStudentConfig.L0.LEVEL

        l3_percent = l3_count/total_count
        l2_percent = l2_count/total_count
        l1_percent = l1_count/total_count

        if(PerformanceConfigConstant.AssignmentStudentConfig.L3.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L3.L3_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentConfig.L3.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L3.L2_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentConfig.L3.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L3.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentConfig.L2.L3_MIN_PERCENT <= l3_percent < PerformanceConfigConstant.AssignmentStudentConfig.L2.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L2.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L2.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L2.L1_MIN_PERCENT <= l1_percent < PerformanceConfigConstant.AssignmentStudentConfig.L2.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentConfig.L2.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentConfig.L1.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L1.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L1.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L1.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L1.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentConfig.L0.LEVEL

    def calculate_performance_assignment_student_list(self, report_logs):

        student_reports = defaultdict(list)

        for report_row in report_logs:
            student_reports[(report_row.assignment_id,
                             report_row.student_id)].append(report_row)

        total_count = 0
        l3_count = 0
        l2_count = 0
        l1_count = 0
        l0_count = 0

        for assignment_id, student_id in student_reports:
            student_total_count, student_green_count, student_yellow_count, student_red_count, student_white_count = self.calculate_performance_assignment_student_question_list(
                student_reports[(assignment_id, student_id)])

            total_count += student_total_count
            l3_count += student_green_count
            l2_count += student_yellow_count
            l1_count += student_red_count
            l0_count += student_white_count

        if(total_count == 0):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L0.LEVEL

        if((l1_count+l2_count+l3_count)/total_count < PerformanceConfigConstant.AssignmentStudentListConfig.DISABLED_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L0.LEVEL

        if(total_count == l0_count):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L0.LEVEL

        l3_percent = l3_count/total_count
        l2_percent = l2_count/total_count
        l1_percent = l1_count/total_count
        l0_percent = l0_count/total_count

        if(PerformanceConfigConstant.AssignmentStudentListConfig.L3.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L3.L3_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentListConfig.L3.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L3.L2_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentListConfig.L3.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L3.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListConfig.L2.L3_MIN_PERCENT <= l3_percent < PerformanceConfigConstant.AssignmentStudentListConfig.L2.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L2.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L2.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L2.L1_MIN_PERCENT <= l1_percent < PerformanceConfigConstant.AssignmentStudentListConfig.L2.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L2.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListConfig.L1.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L1.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L1.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L1.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentListConfig.L0.LEVEL

    def calculate_performance_assignment_id(self, assignment_id):
        report_logs = reporting_dao.find_by_assignment_id(assignment_id)

        class_performance = self.calculate_performance_assignment_student_list(
            report_logs)

        return class_performance

    def calculate_performance_assignment_id_and_class_id(self, assignment_id, class_id):
        if(class_id != None):
            report_logs = reporting_dao.find_by_assignment_id_and_class_id(
                assignment_id, class_id)
        else:
            report_logs = reporting_dao.find_by_assignment_id(assignment_id)

        class_performance = self.calculate_performance_assignment_student_list(
            report_logs)

        return class_performance

    def calculate_performance_assignment_id_and_studnet_id(self, assignment_id, student_id):
        report_logs = reporting_dao.find_by_assignment_id_and_studnet_id(
            assignment_id, student_id)

        class_performance = self.calculate_performance_assignment_student(
            report_logs)

        return class_performance

    def calculate_performance_assignment_id_and_class_id_and_question_id(self, assignment_id, class_id, question_id):
        if(class_id != None):
            assignment_student_question_list = reporting_dao.find_by_assignment_id_and_class_id_and_question_id(
                assignment_id, class_id, question_id)
        else:
            assignment_student_question_list = reporting_dao.find_by_assignment_id_and_class_id(
                assignment_id, question_id)

        total_count, l3_count, l2_count, l1_count, l0_count = self.calculate_performance_assignment_student_question_list(
            assignment_student_question_list)

        if(total_count == 0):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L0.LEVEL

        if(total_count == l0_count):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L0.LEVEL

        
        green_percent = l3_count/total_count
        yellow_percent = l2_count/total_count
        red_percent = l1_count/total_count
        white_percent = l0_count/total_count

        if(PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L3_MIN_PERCENT <= green_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L3_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L2_MIN_PERCENT <= yellow_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L2_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L1_MIN_PERCENT <= red_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L3_MIN_PERCENT <= green_percent < PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L2_MIN_PERCENT <= yellow_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L1_MIN_PERCENT <= red_percent < PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L3_MIN_PERCENT <= green_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L2_MIN_PERCENT <= yellow_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L1_MIN_PERCENT <= red_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L1_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L0.LEVEL

    def calculate_performance_assignment_id_and_class_id_and_studnet_id_and_question_id(self, assignment_id, class_id, student_id, question_id):
        report_logs = reporting_dao.find_by_assignment_id_and_class_id_and_studnet_id_and_question_id(
            assignment_id, class_id, student_id, question_id)

        class_performance = self.calculate_performance_assignment_student_question(
            report_logs)

        return class_performance

    @staticmethod
    def calculate_performance_of_question(red_students, yellow_students, green_students):
        performance = 0
        if red_students + yellow_students + green_students == 0:
            return performance
        red_students_per = (red_students / (red_students + yellow_students + green_students)) * 100
        green_students_per = (green_students / (red_students + yellow_students + green_students)) * 100
        if green_students_per >= 90:
            performance = 3
        elif green_students_per < 90 and red_students_per < 30:
            performance = 2
        elif red_students_per >= 30:
            performance = 1
        return performance


performance_service = PerformaceService()
