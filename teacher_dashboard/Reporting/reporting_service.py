import logging
from teacher_dashboard.Reporting.reporting_request_schema import LogReport, ReportingResponse
from teacher_dashboard.Reporting.reporting_dao import reporting_dao
from operator import getitem
from fastapi import status
from teacher_dashboard.models import ReportLogs
from fastapi.exceptions import HTTPException
from teacher_dashboard.Reporting.reporting_util import reporting_util
from teacher_dashboard.Assignment.services.performance_v2 import performance_service
from teacher_dashboard.Assignment.services.classroom_service import classroom_service
from teacher_dashboard.Assignment.services.question_dashboard_service import question_dashboard_service
from teacher_dashboard.Reporting.reporting_request_schema import InsightsDownloadRequest, AssignmentClassOverviewRequest,  \
    InsightsRequest, AssignmentStudentsRequest, AssignmentQuestionsRequest
from teacher_dashboard.Reporting.reporting_response_schema import AssignmentClassOverviewResponse, \
    AssignmentQuestionBasicDetailsResponse, AssignmentStudentsResponse, InsightsAssignmentClassStudentsResponse, \
    InsightsClassResponse, InsightsClassStudentsResponse, InsightsResponse, AssignmentQuestionsResponse, \
    InsightsAssignmentClassResponse, InsightsAssignmentResponse, QuestionsResponse, StudentDetailsResponse, \
    StudentQuestionsResponse, StudentsResponse
from teacher_dashboard.Assignment.daos.assignment_dao import assignment_dao
from teacher_dashboard.Assignment.daos.assignment_question_dao import assignment_question_dao
from teacher_dashboard.Assignment.daos.assignment_class_dao import assignment_class_dao
from teacher_dashboard.Assignment.daos.assignment_student_dao import assignment_student_dao
from teacher_dashboard.Assignment.daos.assignment_student_question_dao import assignment_student_question_dao
from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum, QuestionStatusEnum, AssignmentStudentStatusEnum, TutorUsedEnum
from teacher_dashboard.Assignment.constants.constants import ClassroomServiceConstants, QuestionDashboradServiceConstants
from collections import defaultdict
from datetime import datetime
import pandas as pd
import io
from fastapi.responses import StreamingResponse


logger = logging.getLogger(__name__)


class ReportingService:

    def log_reports(self, report: LogReport):
        report_in_db = ReportLogs(
            is_correct=report.is_correct,
            is_partially_correct=report.is_partially_correct,
            is_complete=report.is_complete,
            student_input_dict=report.student_input_dict,
            step_number=report.step_number,
            question_session_id=report.question_session_id,
            mode=report.mode,
            hint_code=report.hint_code,
            question_id=report.question_id,
            student_id=report.student_id,
            assignment_id=report.assignment_id,
            class_id=report.class_id,
            interaction_type=report.interaction_type,
            main_cat=report.problem_type,
            sub_cat=report.subtype1
        )
        report_in_db = reporting_dao.save(report_in_db)

        self.update_assignment_student_question(report_in_db)

        return self.__get_logged_report(report_in_db)

    @staticmethod
    def __get_logged_report(report_in_db):
        return ReportingResponse(
            id=report_in_db.id,
            is_correct=report_in_db.is_correct,
            is_partially_correct=report_in_db.is_partially_correct,
            is_complete=report_in_db.is_complete,
            student_input_dict=report_in_db.student_input_dict,
            step_number=report_in_db.step_number,
            question_session_id=report_in_db.question_session_id,
            mode=report_in_db.mode,
            hint_code=report_in_db.hint_code,
            question_id=report_in_db.question_id,
            student_id=report_in_db.student_id,
            assignment_id=report_in_db.assignment_id,
            class_id=report_in_db.class_id,
            interaction_type=report_in_db.interaction_type,
            main_cat=report_in_db.main_cat,
            sub_cat=report_in_db.sub_cat
        )

    def get_assignment_kg(self, assignment_id: int):
        kg_description = reporting_dao.get_kg_desc(assignment_id=assignment_id)
        logger.info('kgs for assignment_id %r = %r', assignment_id, kg_description)
        kg_dict = {}
        m_code_details = {}
        logger.info('iterating over all the kgs')
        for kg in kg_description:
            logger.info('kg code = %r', kg["m_code"])
            logger.info('kg desc = %r', kg["m_desc"])
            logger.info('student_id facing kg %r = %r', kg["m_code"], kg["student_id"])
            if not kg["m_code"] in kg_dict:
                kg_dict[kg["m_code"]] = {"kg_desc": kg["m_desc"], "students": [], "questions": []}
                m_code_details[kg["m_code"]] = {"student_ids": [], "question_ids": []}

            if kg["student_id"] not in m_code_details[kg["m_code"]]["student_ids"]:
                current_student_dict = {"student_id": kg["student_id"], "display_name": kg["display_name"]}
                m_code_details[kg["m_code"]]["student_ids"].append(kg["student_id"])
                kg_dict[kg["m_code"]]["students"].append(current_student_dict)
                kg_dict[kg["m_code"]]["student_count"] = len(kg_dict[kg["m_code"]]["students"])

            if kg["question_id"] not in m_code_details[kg["m_code"]]["question_ids"]:
                current_question_dict = {"question_id": kg["question_id"], "ques_desc": kg["ques_desc"]}
                m_code_details[kg["m_code"]]["question_ids"].append(kg["question_id"])
                kg_dict[kg["m_code"]]["questions"].append(current_question_dict)
                kg_dict[kg["m_code"]]["question_count"] = len(kg_dict[kg["m_code"]]["questions"])

        kg_list = sorted(kg_dict.items(), key=lambda x: getitem(x[1], 'student_count'), reverse=True)
        logger.info('kg_list = %r', kg_list)
        return kg_list

    def get_performance(self, assignment_id, question_ids, question_students, problem_highlights, student_details_dict):
        for i in range(len(question_ids)):
            ques_id = question_ids[i]
            red = 0
            green = 0
            yellow = 0
            student_details_list = []
            for student_id in question_students[ques_id]:
                logger.info('finding performance of student_id %r on ques_id %r', student_id, ques_id)
                needed_help_dict = {}
                student_logs = reporting_dao.get_student_logs(question_id=ques_id, assignment_id=assignment_id,
                                                              student_id=student_id)
                logger.info('student_logs = %r', student_logs)
                student_performance = performance_service.calculate_performance_assignment_student_question(report_logs=
                                                                                                            student_logs)
                logger.info('performance of student_id %r on ques_id %r = %r', student_id, ques_id, student_performance)
                if student_performance == 3:
                    green += 1
                elif student_performance == 2:
                    yellow += 1
                    needed_help_dict["uuid"] = student_id
                    needed_help_dict["display_name"] = student_details_dict[student_id]
                elif student_performance == 1:
                    red += 1
                    needed_help_dict["uuid"] = student_id
                    needed_help_dict["display_name"] = student_details_dict[student_id]
                if len(needed_help_dict):
                    student_details_list.append(needed_help_dict)
            ques_performance = performance_service.calculate_performance_of_question(red_students=red,
                                                                                     yellow_students=yellow,
                                                                                     green_students=green)
            logger.info('avg performance of students on ques_id %r = %r', ques_id, ques_performance)
            problem_highlights[i]["performance"] = ques_performance
            problem_highlights[i]["needed_help_count"] = len(student_details_list)
            problem_highlights[i]["student_details"] = student_details_list
        return problem_highlights

    def get_problem_highlights(self, assignment_id):
        question_details = reporting_dao.get_assignment_questions(assignment_id=assignment_id)
        problem_highlights = {}
        question_ids_visited = []
        question_students = {}
        student_details_dict = {}
        ph_keys = [0]
        ques_no = 1
        logger.info('all questions in assignment %r (with_details) = %r', assignment_id, question_details)
        logger.info('iterating over all the questions')
        for i in range(len(question_details)):
            ques_id = question_details[i]['question_id']
            student_id = question_details[i]['student_id']
            student_name = question_details[i]["display_name"]
            logger.info('ques_id = %r', question_details[i]['question_id'])
            if ques_id not in question_ids_visited:
                question_ids_visited.append(ques_id)
                ques_topic = question_details[i]['name']
                ques_difficulty = question_details[i]['ques_difficulty']
                ques_desc = question_details[i]['ques_desc']
                logger.info('name of ques_id %r = %r', ques_id, ques_topic)
                logger.info('ques_difficulty of ques_id %r = %r', ques_id, ques_difficulty)
                logger.info('ques_desc of ques_id %r = %r', ques_id, ques_desc)
                problem_highlights[ph_keys[-1]] = {"index": ques_no, "ques_id": ques_id, "topic": ques_topic,
                                                   "difficulty": ques_difficulty, "ques_desc": ques_desc}
                ques_no += 1
                ph_keys.append(ph_keys[-1] + 1)
                question_students[ques_id] = [student_id]
            else:
                question_students[ques_id].append(student_id)
            student_details_dict[student_id] = student_name
        logger.info('problem highlights dict without performance = %r', problem_highlights)
        problem_highlights = self.get_performance(assignment_id=assignment_id, question_ids=question_ids_visited,
                                                  question_students=question_students,
                                                  problem_highlights=problem_highlights,
                                                  student_details_dict=student_details_dict)
        logger.info('final problem highlights dict = %r', problem_highlights)
        return problem_highlights

    def get_term_code_details(self, term_code):
        result = reporting_dao.get_term_code(term_code)
        description = result[0].text_def
        video_url = result[0].trimmed_video_link
        examples = []
        if result[0].example_1:
            examples.append(result[0].example_1)
        if result[0].example_2:
            examples.append(result[0].example_2)
        if result[0].example_3:
            examples.append(result[0].example_3)
        response = {"description": description, "examples": examples, "video_url": video_url}
        return response


    def get_insights(self, insights_request: InsightsRequest):
        logger.debug("get insights of all the assignments.")

        if (insights_request.class_id == None and insights_request.assignment_id == None):
            logger.debug("class_id and assignment_id both are None")
            raise HTTPException(
                401, detail="Insufficient parameters to fetch data")

        assignments_list = []
        if (insights_request.assignment_id != None):
            assignments_list.append(insights_request.assignment_id)
            logger.debug("filtering for a specific assignment_id:{}".format(
                insights_request.assignment_id))

        else:
            assignment_in_db_list = assignment_class_dao.find_by_class_id(
                insights_request.class_id)
            for assignment_in_db in assignment_in_db_list:
                assignments_list.append(assignment_in_db.assignment_id)

            logger.debug("filtering for all assignments of the class class_id:{} assignment_id_list:{}".format(
                insights_request.class_id, assignments_list))

        classes_list = []
        if (insights_request.class_id != None):
            classes_list.append(insights_request.class_id)
            logger.debug("filtering for a specific class_id:{}".format(
                insights_request.class_id))
        else:
            assignment_classes_in_db_list = assignment_class_dao.find_by_assignment_id(
                insights_request.assignment_id)
            for assignment_class in assignment_classes_in_db_list:
                classes_list.append(assignment_class.class_id)

            logger.debug("filtering for all classes of assignment assignment_id:{} class_id_list:{}".format(
                insights_request.assignment_id, classes_list))

        classes_response = []
        for class_id in classes_list:
            class_students = classroom_service.get_students(class_id)
            class_students_response = []
            for student in class_students:
                class_students_response.append(
                    InsightsClassStudentsResponse(
                        student_id=student.get(ClassroomServiceConstants.UUID),
                        first_name=student.get(
                            ClassroomServiceConstants.FIRST_NAME),
                        last_name=student.get(
                            ClassroomServiceConstants.LAST_NAME)
                    )
                )
            class_students_response.sort(key = lambda s: (s.last_name.lower(),s.first_name.lower()) )
            
            classes_response.append(
                InsightsClassResponse(
                    class_id=class_id,
                    class_students=class_students_response
                )
            )
            logger.debug(
                "collected all student details of class class_id:{}".format(class_id))

        assignments_response = []
        for assingment_id in assignments_list:
            assignment_in_db = assignment_dao.find_by_id(assingment_id)

            if (assignment_in_db == None):
                logger.error(
                    "not able to retrive data for assignment assignment_id:{}".format(assingment_id))
                raise HTTPException(
                    401, detail="No assignment exists for the given assignment_id")

            if (assignment_in_db.is_published == False or assignment_in_db.teacher_id != insights_request.user_id):
                logger.error(
                    "no permission to view the assignment details. either the assignment is not published or the the teacher_id does not matches. assignment_id:{}".format(assingment_id))
                continue

            logger.debug("finding assignment_studnets by assignmnet and class assignmnet_id:{} class_id:{}".format(
                assingment_id, classes_list))
            assignment_students = assignment_student_dao.find_by_assignment_id_and_class_id_list_order_by_class_id(
                assingment_id, classes_list)

            assignment_classes_response = []
            prev_class_id = None
            assignment_total_questions_count = len(assignment_in_db.questions)
            show_class_performance = False

            for student in assignment_students:
                logger.debug("finding the score of the assignment_studnet student_id:{} assignment_id:{}".format(
                    student.student_id, student.assignment_id))
                completed_questions_count, total_questions_count = reporting_util.student_assignment_score(
                    student.questions)

                assignment_student_late = ((student.status == AssignmentStatusEnum.COMPLETED and student.completed_at >
                                            assignment_in_db.submission_last_date) or (
                    datetime.utcnow() > assignment_in_db.submission_last_date))

                student_performance = 0

                if(student.status == AssignmentStatusEnum.COMPLETED):
                    logger.debug(
                        "student assignment is complete ... so performance would be calculated.")
                    logger.debug("calculating assignmnet student performance")
                    student_performance = performance_service.calculate_performance_assignment_id_and_studnet_id(
                        student.assignment_id, student.student_id)
                    show_class_performance = True

                logger.debug("creating assignment_class_student response. student_id:{} class_id:{}".format(
                    student.student_id, student.class_id))

                insights_assignment_class_students_response = InsightsAssignmentClassStudentsResponse(
                    student_id=student.student_id,
                    completed=(student.status ==
                               AssignmentStatusEnum.COMPLETED),
                    late=assignment_student_late,
                    questions_completed=completed_questions_count,
                    total_questions=total_questions_count,
                    student_performance=student_performance,
                )

                if (student.class_id == None or student.class_id != prev_class_id):
                    logger.debug("student class_id does not matches the previous class_id. adding new class. previous_class_id:{} student.class_id:{}".format(
                        prev_class_id, student.class_id))

                    prev_class_id = student.class_id

                    assignment_classes_response.append(InsightsAssignmentClassResponse(
                        class_id=student.class_id,
                        class_performance=0,
                        class_students=[]
                    ))

                logger.debug("adding student insights to class.")
                assignment_classes_response[-1].class_students.append(
                    insights_assignment_class_students_response
                )

                class_performance = 0
                if(show_class_performance == True and assignment_classes_response[-1].class_performance == 0):
                    logger.debug("calculating class performance assignment_id:{} class_id:{}".format(
                        assingment_id, class_id))
                    class_performance = performance_service.calculate_performance_assignment_id_and_class_id(
                        student.assignment_id, student.class_id)
                    assignment_classes_response[-1].class_performance = class_performance

            logger.debug("adding performance of assignment. assignment_id:{}".format(
                assignment_in_db.id))
            assignments_response.append(InsightsAssignmentResponse(
                assignment_id=assignment_in_db.id,
                assignment_title=assignment_in_db.title,
                due_date=assignment_in_db.submission_last_date,
                total_questions_count=assignment_total_questions_count,
                classes=assignment_classes_response
            ))

        assignments_response.sort(key = lambda o: o.due_date, reverse=True)
        return InsightsResponse(
            teacher_id=insights_request.user_id,
            class_id=insights_request.class_id,
            assignment_id=insights_request.assignment_id,
            classes=classes_response,
            assignments=assignments_response
        )

    def download_insights(self, insightsDownloadRequest: InsightsDownloadRequest):
        logger.debug("download insights")

        logger.debug("making request to get insights data.")
        insightsRequest = InsightsRequest(
            assignment_id=insightsDownloadRequest.assignment_id,
            class_id=insightsDownloadRequest.class_id,
            user_id=insightsDownloadRequest.user_id,
            auth_token=insightsDownloadRequest.auth_token
        )

        logger.debug("getting insights data.")
        data = self.get_insights(insightsRequest)

        class_data = data.classes
        assignment_data = data.assignments

        student_info = {}
        for assignment_class in class_data:
            for student in assignment_class.class_students:
                logger.debug("adding students basic details in the dict for creating table. dictionary key:{}".format(
                    student.student_id))
                student_info[student.student_id] = student.dict()

        for assignment in assignment_data:
            for assignment_class in assignment.classes:
                for student in assignment_class.class_students:
                    student_row = student_info.get(student.student_id)
                    if(student_row != None):
                        logger.debug(
                            "preparing to add insights data for student.")
                        late = "Late=True" if(
                            student.late == True) else "Late=False"
                        completed = "Completed=True" if(
                            student.completed == True) else "Completed=False"
                        performance = "Performance={}".format(
                            student.student_performance) if(student.completed == True) else ""
                        score = "Score={}/{}".format(student.questions_completed, student.total_questions) if(
                            student.completed == True) else ""
                        key = [assignment.assignment_title, str(
                            assignment.due_date), "{} Problems".format(assignment.total_questions_count)]
                        student_row["\n".join(key)] = "\n".join(
                            [late, completed, performance, score])

                        # student_row[assignment.assignment_id] = "\n".join([late, completed, performance, score])

        logger.debug("transposing the dataframe")
        df = pd.DataFrame(student_info).transpose()

        logger.debug("removing the student_id field from the dataframe")
        df.drop("student_id", axis=1, inplace=True)

        logger.debug("converting dataframe to csv and send as response")

        stream = io.StringIO()
        df.to_csv(stream, index=False)

        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv")

        response.headers["Content-Disposition"] = "attachment; filename=insights.csv"

        return response

    def get_assignment_class_overview(self, assignment_class_overview_request: AssignmentClassOverviewRequest):
        logger.debug("get assignment_class basic overview")

        logger.debug("get assignment from db. assignment_id:{}".format(
            assignment_class_overview_request.assignemnt_id))

        assignment_in_db = assignment_dao.find_by_id(
            assignment_class_overview_request.assignemnt_id)

        if (assignment_in_db == None):
            logger.error("assignment not found in db.")
            raise HTTPException(
                401, detail="No assignment exists for the given assignment_id")

        if (assignment_in_db.is_published == False):
            logger.error("assignment not published.")
            raise HTTPException(
                401, detail="No reporting for unpublished assignments")

        if (assignment_in_db.teacher_id != assignment_class_overview_request.user_id):
            logger.error(
                "assignment teacher_id does not match with the current user_id.")
            raise HTTPException(
                401, detail="No access to view this assignment")

        logger.debug(
            "calculating total student count and assignment completed count for the assignment.")
        completed_students_count, total_students_count = reporting_util.assignment_score(
            assignment_in_db.id, assignment_class_overview_request.class_id)

        logger.debug("getting mapping for the question_id and sequence_number")
        question_id_seuqence_map = reporting_util.get_question_id_sequence_mapping(
            assignment_in_db.id)

        seq_num = 1
        question_sequnce = []

        for question in assignment_in_db.questions:
            logger.debug(
                "getting the sequence number of the given question_id")
            seq_num = question_id_seuqence_map.get(
                question.question_id, None)

            if(seq_num == None):
                logger.error("question_id not in the question_id_seuqence_map mapping. question_id:{}".format(
                    question.question_id))

            question_sequnce.append(AssignmentQuestionBasicDetailsResponse(
                question_id=question.question_id,
                question_sequence_number=seq_num
            ))

        logger.debug("sorting questions based on sequernce number.")
        question_sequnce.sort(
            key=lambda question: question.question_sequence_number)

        show_class_performance = False
        for student in assignment_in_db.students:
            if(student.status == AssignmentStatusEnum.COMPLETED):
                show_class_performance = True
        logger.debug("show_class_performance:{}".format(
            show_class_performance))

        class_performance = 0
        if(show_class_performance == True):
            class_performance = performance_service.calculate_performance_assignment_id_and_class_id(
                assignment_in_db.id, assignment_class_overview_request.class_id)
        logger.debug("class_performance calculated.")

        return AssignmentClassOverviewResponse(
            teacher_id=assignment_class_overview_request.user_id,
            class_id=assignment_class_overview_request.class_id,
            assignment_id=assignment_class_overview_request.assignemnt_id,
            assignment_title=assignment_in_db.title,
            total_questions=len(assignment_in_db.questions),
            completed_students_count=completed_students_count,
            total_students_count=total_students_count,
            class_performance=class_performance,
            assignment_questions=question_sequnce
        )

    def get_assignment_students(self, assignment_students_request: AssignmentStudentsRequest):
        logger.debug("get assignment students reports")

        logger.debug("finding assignment by id.")
        assignment_in_db = assignment_dao.find_by_id(
            assignment_students_request.assignment_id)

        if (assignment_in_db == None):
            logger.error("assignment not found in the db.")
            raise HTTPException(
                401, detail="No assignment exists for the given assignment_id")

        if (assignment_in_db.is_published == False):
            logger.error("assignment is not published.")
            raise HTTPException(
                401, detail="No reporting for unpublished assignments")

        if (assignment_in_db.teacher_id != assignment_students_request.user_id):
            logger.debug(
                "assignment teacher_id does not matches with the current user_id. teacher_id:{}".format(assignment_in_db.teacher_id))
            raise HTTPException(
                401, detail="No access to view this assignment")

        if (assignment_students_request.class_id != None):
            logger.debug("finding assignment students specific to class_id. class_id:{}".format(
                assignment_students_request.class_id))
            assignment_students = assignment_student_dao.find_students_by_assignment_id_and_class_id(
                assignment_students_request.assignment_id, assignment_students_request.class_id)
        else:
            logger.debug(
                "finding all assignment studnets to whom the assignment was assigned.")
            assignment_students = assignment_in_db.students

        logger.debug("get question_id and sequence number mapping.")
        question_id_seuqence_map = reporting_util.get_question_id_sequence_mapping(
            assignment_in_db.id)

        students_response_list = []
        for student in assignment_students:
            if (
                (assignment_students_request.status == AssignmentStudentStatusEnum.COMPLETE and reporting_util.student_assignment_complete(student)) or
                (assignment_students_request.status == AssignmentStudentStatusEnum.INCOMPLETE and reporting_util.student_assignment_incomplete(student)) or
                (assignment_students_request.status == AssignmentStudentStatusEnum.STRUGGLING and reporting_util.student_assignment_struggling(student)) or
                    (assignment_students_request.status == AssignmentStudentStatusEnum.ALL)):
                logger.debug("student satisfies the requested status. assignment_students_request_status:{} student_id:{}".format(
                    assignment_students_request.status, student.student_id))
                pass
            else:
                logger.debug("student does not satisfies the requested status. assignment_students_request_status:{} student_id:{}".format(
                    assignment_students_request.status, student.student_id))
                continue

            student_questions = student.questions

            logger.debug(
                "calculating score for the student for the assignment.")
            completed_questions_count, total_questions_count = reporting_util.student_assignment_score(
                student_questions)

            student_progress = None

            if(assignment_students_request.progress == True):
                logger.debug(
                    "was requested to show the student progress. calculating student progress.")
                student_progress = self.student_assignment_questions(
                    student.assignment_id,
                    student.class_id,
                    student.student_id,
                    student_questions,
                    question_id_seuqence_map)

            student_performance = 0
            if(student.status == AssignmentStatusEnum.COMPLETED):
                logger.debug(
                    "student has completed the assignment. student's complete performance would be calculated.")
                student_performance = performance_service.calculate_performance_assignment_id_and_studnet_id(
                    student.assignment_id, student.student_id)

            logger.debug("adding reporting details of the student. student_id:{}".format(
                student.student_id))
            students_response_list.append(StudentDetailsResponse(
                student_id=student.student_id,
                class_id=student.class_id,
                first_name=student.first_name,
                last_name=student.last_name,
                completed_questions_count=completed_questions_count,
                total_questions_count=total_questions_count,
                assignment_complete=(
                    student.status == AssignmentStatusEnum.COMPLETED),
                performance=student_performance,
                progress=student_progress))

        students_response_list.sort(key = lambda s: (s.performance, s.completed_questions_count, s.last_name.lower(), s.first_name.lower()))
        
        return AssignmentStudentsResponse(
            teacher_id=assignment_students_request.user_id,
            assignment_id=assignment_students_request.assignment_id,
            class_id=assignment_students_request.class_id,
            status=assignment_students_request.status,
            students=students_response_list,
            start=-1,
            limit=-1,
            total_count=-1
        )

    def student_assignment_questions(self,
                                     assignment_id,
                                     class_id,
                                     student_id,
                                     student_questions,
                                     question_id_seuqence_map):
        logger.debug("calculating student progress. assignment_id:{} class_id:{} student_id:{}".format(
            assignment_id,
            class_id,
            student_id))

        questions_list = []
        for question in student_questions:
            logger.debug("calculating for student_id:{} question_id:{}".format(
                student_id, question.question_id))
            questions_list.append(
                StudentQuestionsResponse(
                    question_id=question.question_id,
                    question_sequence_num=question_id_seuqence_map.get(
                        question.question_id),
                    tutor_used=(question.tutor_used ==
                                TutorUsedEnum.USED),
                    question_status=question.status,
                    question_performance=performance_service.calculate_performance_assignment_id_and_class_id_and_studnet_id_and_question_id(
                        assignment_id,
                        class_id,
                        student_id,
                        question.question_id)
                )
            )
        return questions_list

    def get_assignment_questions(self, assignment_questions_request: AssignmentQuestionsRequest):
        logger.debug("get assignment questions reports")

        logger.debug("finding assignment in db by id.")
        assignment_in_db = assignment_dao.find_by_id(
            assignment_questions_request.assignment_id)

        if (assignment_in_db == None):
            logger.error("assignment not found in db.")
            raise HTTPException(
                401, detail="No assignment exists for the given assignment_id")

        if (assignment_in_db.is_published == False):
            logger.error("assignment not published.")
            raise HTTPException(
                401, detail="No reporting for unpublished assignments")

        if (assignment_in_db.teacher_id != assignment_questions_request.user_id):
            logger.error("assignment teacher_id and current user_id does not match. teacher_id:{}".format(
                assignment_in_db.teacher_id))
            raise HTTPException(
                401, detail="No access to view this assignment")

        if (assignment_questions_request.class_id != None):
            logger.debug("finding all students of the given class_id and assignment_id. assignment_id:{} class_id:{}".format(
                assignment_questions_request.assignment_id, assignment_questions_request.class_id))
            assignment_students = assignment_student_dao.find_students_by_assignment_id_and_class_id(
                assignment_questions_request.assignment_id, assignment_questions_request.class_id)
        else:
            logger.debug("finding all students of the given assignment_id. assignment_id:{}".format(
                assignment_questions_request.assignment_id))
            assignment_students = assignment_in_db.students

        if (assignment_questions_request.question_id != None):
            logger.debug("finding all assignment questions by assignment_id and question_id. assignment_id:{} question_id:{}".format(
                assignment_questions_request.assignment_id, assignment_questions_request.question_id))

            assignment_questions = assignment_question_dao.find_questions_by_assignment_id_and_question_id(
                assignment_questions_request.assignment_id, assignment_questions_request.question_id)
            assignment_questions_total_count = len(assignment_questions)
        else:
            logger.debug("finding all assignment questions by assignment_id. assignment_id:{}".format(
                assignment_questions_request.assignment_id))

            assignment_questions = assignment_question_dao.find_questions_by_assignment_id_and_is_limited_order_by_sequence_number(
                assignment_questions_request.assignment_id, assignment_questions_request.start,
                assignment_questions_request.limit)
            assignment_questions_total_count = assignment_question_dao.count_questions_by_assignment_id(
                assignment_questions_request.assignment_id)

        logger.debug(
            "separated the students based on tutor_used, students_complete, students_incomplete factors.")

        assignment_questions_ids = set(
            question.question_id for question in assignment_questions)

        students_status = {"tutor_used": defaultdict(list),
                           "students_complete": defaultdict(list),
                           "students_incomplete": defaultdict(list)}
        for student in assignment_students:
            for student_question in student.questions:
                if (student_question.question_id in assignment_questions_ids):
                    if (student_question.status == QuestionStatusEnum.NOT_ATTEMPTED):
                        students_status["students_incomplete"][student_question.question_id].append(
                            StudentsResponse(
                                student_id=student.student_id,
                                first_name=student.first_name,
                                last_name=student.last_name,
                            ))
                    else:
                        students_status["students_complete"][student_question.question_id].append(
                            StudentsResponse(
                                student_id=student.student_id,
                                first_name=student.first_name,
                                last_name=student.last_name,
                            ))

                    if (student_question.tutor_used == TutorUsedEnum.USED):
                        students_status["tutor_used"][student_question.question_id].append(
                            StudentsResponse(
                                student_id=student.student_id,
                                first_name=student.first_name,
                                last_name=student.last_name,
                            ))

        logger.debug(
            "getting complete details of all the questions in the assignment")
        questions_response_list = []
        question_sequence_num = 1
        for question in assignment_questions:
            if (question.question_id not in assignment_questions_ids):
                logger.error("question_id not in assignment questions list. question_id:{} assignment_questions_ids:{}".format(
                    question.question_id, assignment_questions_ids))
                continue

            logger.debug("fetching question details from question dashboard")
            complete_question = question_dashboard_service.get_question(
                question.question_id)

            logger.debug("appending the details of the question")
            questions_response_list.append(QuestionsResponse(
                question_id=complete_question.get(
                    QuestionDashboradServiceConstants.Data.ID),
                question_desc=complete_question.get(
                    QuestionDashboradServiceConstants.Data.DESCRIPTION),
                question_difficulty=complete_question.get(
                    QuestionDashboradServiceConstants.Data.DIFFICULTY),
                topic_name=complete_question.get(
                    QuestionDashboradServiceConstants.Data.TOPIC),
                question_sequence_number=question_sequence_num,
                performance=performance_service.calculate_performance_assignment_id_and_class_id_and_question_id(assignment_questions_request.assignment_id,
                                                                                                                 assignment_questions_request.class_id,
                                                                                                                 question.question_id),
                students_tutor_used_count=len(
                    students_status["tutor_used"][question.question_id]),
                students_tutor_used=students_status["tutor_used"][question.question_id],
                students_incomplete_count=len(
                    students_status["students_incomplete"][question.question_id]),
                students_incomplete=students_status["students_incomplete"][question.question_id],
                students_complete_count=len(
                    students_status["students_complete"][question.question_id]),
                students_complete=students_status["students_complete"][question.question_id]
            ))
            question_sequence_num += 1

        return AssignmentQuestionsResponse(
            teacher_id=assignment_questions_request.user_id,
            assignment_id=assignment_questions_request.assignment_id,
            class_id=assignment_questions_request.class_id,
            question_id=assignment_questions_request.question_id,
            questions=questions_response_list,
            start=assignment_questions_request.start,
            size=len(questions_response_list),
            total_count=assignment_questions_total_count
        )

    def update_assignment_student_question(self, report_in_db):
        assignment_studnet_question = assignment_student_question_dao.find_by_assignment_id_and_student_id_and_question_id(
            report_in_db.assignment_id, report_in_db.student_id, report_in_db.question_id)

        if(assignment_studnet_question == None):
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail="Not able to find the combination of assignment_id, student_id, question_id in "
                                       "the assignment db.")

        assignment_studnet_question = reporting_util.update_incorrect_count(
            report_in_db, assignment_studnet_question)
        assignment_studnet_question = reporting_util.update_hint_count(
            report_in_db, assignment_studnet_question)
        assignment_studnet_question = reporting_util.update_question_complete(
            report_in_db, assignment_studnet_question)
        assignment_studnet_question = reporting_util.update_tutor_used(
            report_in_db, assignment_studnet_question)
        # assignment_studnet_question = reporting_util.update_assignment_student_status(
        #     assignment_studnet_question)

        assignment_student_question_dao.save(assignment_studnet_question)


reporting_service = ReportingService()
