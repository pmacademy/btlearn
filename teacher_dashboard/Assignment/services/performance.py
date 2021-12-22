from teacher_dashboard.Assignment.constants.constants import PerformanceConfigConstant
from teacher_dashboard.Assignment.daos.assignment_student_question_dao import assignment_student_question_dao
from teacher_dashboard.Assignment.daos.assignment_student_dao import assignment_student_dao


class PerformaceService:
    def calculate_performance_assignment_student_question(self, assignment_student_question):
        if(PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.INCORRECT_MIN_NUMBER <= assignment_student_question.incorrect_count <= PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.INCORRECT_MAX_NUMBER and
           PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.HINT_MIN_NUMBER <= assignment_student_question.hint_count <= PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.HINT_MAX_NUMBER and
           assignment_student_question.status == PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.STATUS and
           assignment_student_question.tutor_used in PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.TUTOR_USED):

            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.INCORRECT_MIN_NUMBER <= assignment_student_question.incorrect_count <= PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.INCORRECT_MAX_NUMBER and
             PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.HINT_MIN_NUMBER <= assignment_student_question.hint_count <= PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.HINT_MAX_NUMBER and
             assignment_student_question.status == PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.STATUS and
             assignment_student_question.tutor_used in PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.TUTOR_USED):

            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L2.LEVEL

        elif(assignment_student_question.status == PerformanceConfigConstant.AssignmentStudentQuestionConfig.L1.STATUS and
             assignment_student_question.tutor_used in PerformanceConfigConstant.AssignmentStudentQuestionConfig.L1.TUTOR_USED):

            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentQuestionConfig.L0.LEVEL

        # if not incorrect_count and not hint_count:
        #     problem_highlights[i]["performance"] = "green"
        # elif incorrect_count < 3 and hint_count < 3:
        #     problem_highlights[i]["performance"] = "yellow"
        # else:
        #     problem_highlights[i]["performance"] = "red"

    def calculate_performance_assignment_student_question_list(self, assignment_student_question_list):
        total_count = 0
        l3_count = 0
        l2_count = 0
        l1_count = 0
        l0_count = 0

        for question in assignment_student_question_list:
            question_performance = self.calculate_performance_assignment_student_question(
                question)

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

    def calculate_performance_assignment_student(self, assignment_student):
        assignment_student_questions_list = assignment_student.questions

        total_count = 0
        l3_count = 0
        l2_count = 0
        l1_count = 0

        # for question in assignment_student_questions:
        #     question_performance = self.calculate_performance_assignment_student_question(
        #         question)

        #     total_count += 1
        #     if(question_performance == PerformanceConfigConstant.AssignmentStudentQuestionConfig.Green.COLOR):
        #         green_count += 1
        #     elif(question_performance == PerformanceConfigConstant.AssignmentStudentQuestionConfig.Yellow.COLOR):
        #         yellow_count += 1
        #     elif(question_performance == PerformanceConfigConstant.AssignmentStudentQuestionConfig.Red.COLOR):
        #         red_count += 1

        total_count, l3_count, l2_count, l1_count, white_count = self.calculate_performance_assignment_student_question_list(
            assignment_student_questions_list)

        if(total_count == 0):
            return PerformanceConfigConstant.AssignmentStudentConfig.L0.LEVEL

        if(total_count == white_count):
            return PerformanceConfigConstant.AssignmentStudentConfig.L0.LEVEL

        l3_percent = l3_count/total_count
        l2_percent = l2_count/total_count
        l1_percent = l1_count/total_count

        if(PerformanceConfigConstant.AssignmentStudentConfig.L3.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L3.L3_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentConfig.L3.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L3.L2_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentConfig.L3.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L3.L1_MAX_PERCENT and
           assignment_student.status == PerformanceConfigConstant.AssignmentStudentConfig.STATUS):
            return PerformanceConfigConstant.AssignmentStudentConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentConfig.L2.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L2.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L2.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L2.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L2.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L2.L1_MAX_PERCENT and
             assignment_student.status == PerformanceConfigConstant.AssignmentStudentConfig.STATUS):
            return PerformanceConfigConstant.AssignmentStudentConfig.L2.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentConfig.L1.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L1.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L1.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentConfig.L1.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentConfig.L1.L1_MAX_PERCENT and
             assignment_student.status == PerformanceConfigConstant.AssignmentStudentConfig.STATUS):
            return PerformanceConfigConstant.AssignmentStudentConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentConfig.L0.LEVEL

    def calculate_performance_assignment_student_list(self, assignment_student_list):

        total_count = 0
        l3_count = 0
        l2_count = 0
        l1_count = 0
        l0_count = 0

        for assignment_student in assignment_student_list:
            if(assignment_student.status == PerformanceConfigConstant.AssignmentStudentListConfig.STATUS):
                assignment_student_questions = assignment_student.questions

                student_total_count, student_green_count, student_yellow_count, student_red_count, student_white_count = self.calculate_performance_assignment_student_question_list(
                    assignment_student_questions)

                total_count += student_total_count
                l3_count += student_green_count
                l2_count += student_yellow_count
                l1_count += student_red_count
                l0_count += student_white_count

        if(total_count == 0):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L0.LEVEL

        if((l1_count+l2_count+l3_count)/total_count < PerformanceConfigConstant.AssignmentStudentListConfig.DISABLED_MAX_PERCENT):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L0.LEVEL

        l3_percent = l3_count/total_count
        l2_percent = l2_count/total_count
        l1_percent = l1_count/total_count
        l0_percent = l0_count/total_count

        if(PerformanceConfigConstant.AssignmentStudentListConfig.L3.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L3.L3_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentListConfig.L3.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L3.L2_MAX_PERCENT and
           PerformanceConfigConstant.AssignmentStudentListConfig.L3.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L3.L1_MAX_PERCENT and
           l0_percent < 1):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListConfig.L2.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L2.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L2.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L2.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L2.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L2.L1_MAX_PERCENT and
             l0_percent < 1):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L2.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListConfig.L1.L3_MIN_PERCENT <= l3_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L1.L2_MIN_PERCENT <= l2_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListConfig.L1.L1_MIN_PERCENT <= l1_percent <= PerformanceConfigConstant.AssignmentStudentListConfig.L1.L1_MAX_PERCENT and
             l0_percent < 1):
            return PerformanceConfigConstant.AssignmentStudentListConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentListConfig.L0.LEVEL

    def calculate_performance_assignment_class(self, assignment_id, class_id):
        if(class_id != None):
            assignment_student_list = assignment_student_dao.find_students_by_assignment_id_and_class_id(
                assignment_id, class_id)
        else:
            assignment_student_list = assignment_student_dao.find_students_by_assignment_id(
                assignment_id)
        # for student in assignment.students:
        #     if(student.class_id in class_id_list):
        #         assignment_student_list.append(student)

        class_performance = self.calculate_performance_assignment_student_list(
            assignment_student_list)

        return class_performance

    def calculate_performance_assignment_id_and_class_id_and_question_id(self, assignment_id, class_id, question_id):
        if(class_id != None):
            assignment_student_question_list = assignment_student_question_dao.find_by_assignment_id_and_class_id_and_question_id_and_is_complete(
                assignment_id, class_id, question_id)
        else:
            assignment_student_question_list = assignment_student_question_dao.find_by_assignment_id_and_question_id_and_is_complete(
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
           PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L1_MIN_PERCENT <= red_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.L1_MAX_PERCENT and
           white_percent < 1):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L3.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L3_MIN_PERCENT <= green_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L2_MIN_PERCENT <= yellow_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L1_MIN_PERCENT <= red_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.L1_MAX_PERCENT and
             white_percent < 1):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L2.LEVEL

        elif(PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L3_MIN_PERCENT <= green_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L3_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L2_MIN_PERCENT <= yellow_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L2_MAX_PERCENT and
             PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L1_MIN_PERCENT <= red_percent <= PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.L1_MAX_PERCENT and
             white_percent < 1):
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L1.LEVEL

        else:
            return PerformanceConfigConstant.AssignmentStudentListQuestionConfig.L0.LEVEL


performance_service = PerformaceService()
