from collections import defaultdict
from teacher_dashboard.Assignment.constants.constants import QuestionDashboradServiceConstants
from teacher_dashboard.Assignment.daos.assignment_student_question_dao import assignment_student_question_dao
from teacher_dashboard.Assignment.daos.assignment_student_dao import assignment_student_dao
from teacher_dashboard.Assignment.daos.assignment_class_dao import assignment_class_dao
from teacher_dashboard.Assignment.services.classroom_service import classroom_service
from teacher_dashboard.Assignment.services.reporting_service import reporting_service
from teacher_dashboard.models import Assignment, AssignmentQuestion, AssignmentClass, AssignmentStudent, AssignmentStudentQuestion
from teacher_dashboard.Assignment.daos.assignment_dao import assignment_dao
from teacher_dashboard.Assignment.schemas.assignment_schema import AllAssignmentStudentResponse, AllAssignmentTeacherResponse, AssignmentTopicsResponse, BasicAssignementDetailsStudentResponse, BasicAssignementDetailsTeacherResponse, ClassStudentsRequest, ClassStudentsResponse, CreateAssignmentRequest, StudentNextQuestionDetailsResponse, StudentQuestionCompleteResponse, UpdateAssignmentPublishStatusRequest, UpdateAssignmentRequest, AssignmentResponse, AssignmentTopicsRequest
from fastapi.exceptions import HTTPException
from teacher_dashboard.db_session import DatabaseSession
from teacher_dashboard.Assignment.services.question_dashboard_service import question_dashboard_service
from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum, QuestionStatusEnum
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.functions import user
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class AssignmentService:
    def __get_formatted_assignment(self, assignment_in_db):
        logger.debug("preparing formatted reponse for an assignment in db.")
        questions_in_db = assignment_in_db.questions
        topics = []
        for q in questions_in_db:
            if(len(topics) > 0 and topics[-1].topic_sequence_num == q.topic_sequence_num and topics[-1].topic_code == q.topic_code and topics[-1].cluster_id == q.cluster_id):
                logger.debug(
                    "question_id:{} added to the topic.".format(q.question_id))
                topics[-1].questions.append(AssignmentQuestion(
                    question_id=q.question_id,
                    sequence_num=q.sequence_num,
                    tutor_available=q.tutor_available
                ))
            else:
                logger.debug("new topic added in response. topic_id:{} cluster_id:{}".format(
                    q.topic_code, q.cluster_id))
                logger.debug("new question added in topic. topic_id:{} cluster_id:{} question_id:{}".format(
                    q.topic_code, q.cluster_id, q.question_id))
                topics.append(AssignmentTopicsResponse(
                    topic_code=q.topic_code,
                    topic_name=question_dashboard_service.get_topic_name(
                        q.topic_code),
                    topic_sequence_num=q.topic_sequence_num,
                    topic_tutor_available=q.topic_tutor_available,
                    cluster_id=q.cluster_id,
                    questions=[AssignmentQuestion(
                        question_id=q.question_id,
                        sequence_num=q.sequence_num,
                        tutor_available=q.tutor_available
                    )]
                ))
        return AssignmentResponse(
            id=assignment_in_db.id,
            teacher_id=assignment_in_db.teacher_id,
            title=assignment_in_db.title,
            classes=assignment_in_db.classes,
            is_published=assignment_in_db.is_published,
            submission_last_date=assignment_in_db.submission_last_date,
            last_modified_time=assignment_in_db.updated_at,
            topics=topics
        )

    def get_assignment(self, assignment_id: int, user_id: str):
        assignment_in_db = assignment_dao.find_by_id(assignment_id)

        if(assignment_in_db == None):
            logger.debug("assignment not found in db")
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        if(assignment_in_db.teacher_id != user_id):
            logger.debug("assignment teacher id and user id do not match. assignment_teacher_id:{} user_id:{}".format(
                assignment_in_db.teacher_id, user_id))
            raise HTTPException(
                401, detail="Not authorized to access the assignment.")

        return self.__get_formatted_assignment(assignment_in_db)

    def get_all_teacher_assignments(self, user_id: str):
        all_assignments_in_db = assignment_dao.find_by_teacher_id(user_id)

        published = []
        not_published = []

        logger.debug("recieved data from db. processing the data.")
        for assignment in all_assignments_in_db:

            logger.debug("processing assignment assignment_id:{}".format(assignment.id))
            completed_count = 0
            for student in assignment.students:
                if(student.status == AssignmentStatusEnum.COMPLETED):
                    completed_count += 1
            total_count = len(assignment.students)

            completetion_status = "{completed_count}/{total_count}".format(
                completed_count=completed_count, total_count=total_count)

            response_assignment = BasicAssignementDetailsTeacherResponse(id=assignment.id,
                                                                         title=assignment.title,
                                                                         classes_count=len(
                                                                             assignment.classes),
                                                                         students_count=len(
                                                                             assignment.students),
                                                                         completion_status=completetion_status,
                                                                         questions_count=len(
                                                                             assignment.questions),
                                                                         is_published=assignment.is_published,
                                                                         submission_last_date=assignment.submission_last_date,
                                                                         last_modified_time=assignment.updated_at,
                                                                         performance=0)
            if(response_assignment.is_published == True):
                logger.debug("calculating performance for the assignment.")
                performance = reporting_service.get_overview(
                    assignment.id).get("class_performance", 0)
                response_assignment.performance = performance
                published.append(response_assignment)
            else:
                not_published.append(response_assignment)

        logger.debug(
            "sorting the published assignmnets based on submission last date.")
        published.sort(key=lambda assign: assign.submission_last_date)

        logger.debug(
            "sorting the non-published data based on last modified time in reverse order.")
        not_published.sort(
            key=lambda assign: assign.last_modified_time, reverse=True)

        return AllAssignmentTeacherResponse(teacher_id=user_id,
                                            published=published,
                                            not_published=not_published)

    def create_assignment(self, assignment: CreateAssignmentRequest, user_id: str):
        # todo: add class validation
        # todo: add student validation
        # todo: assignment default deadline
        # todo: tesacher_id validation
        # todo: check if is_published=True & deadline!=None

        # assignment_question_list = [AssignmentQuestion(
        #     question_id=i.question_id, sequence_num=i.sequence_num) for i in assignment.questions]

        if(assignment.submission_last_date != None and assignment.submission_last_date.timestamp() < datetime.utcnow().timestamp()):
            logger.debug("not able to create assignment since Submission Last Date cannot be earlier than the current time. submission_last_date:{} current_time:{}".format(
                assignment.submission_last_date, datetime.utcnow()))
            raise HTTPException(
                401, detail="Submission Last Date cannot be earlier than the current time")

        assignment_question_list = []

        for topic in assignment.topics:
            for ques in topic.questions:
                assignment_question_list.append(AssignmentQuestion(
                    question_id=ques.question_id,
                    sequence_num=ques.sequence_num,
                    tutor_available=ques.tutor_available,
                    topic_code=topic.topic_code,
                    topic_sequence_num=topic.topic_sequence_num,
                    topic_tutor_available=topic.tutor_available,
                    cluster_id=topic.cluster_id
                ))
        logger.debug("AssignmentQuestion entities created.")

        assignment_classes_list = [AssignmentClass(class_id=i.class_id)
                                   for i in assignment.classes]
        logger.debug("AssignmentClass entities created.")

        assignment_students_list = []
        for class_item in assignment.classes:
            class_students = classroom_service.get_students(
                class_item.class_id)
            for student in class_students:
                assignment_students_list.append(
                    AssignmentStudent(
                        student_id=student["uuid"],
                        class_id=student["class_id"],
                        first_name=student["first_name"],
                        last_name=student["last_name"],
                        email=student["email"],
                        parents_email=student["parents_email"],
                        questions=[AssignmentStudentQuestion(
                            question_id=ques.question_id) for ques in assignment_question_list]
                    ))
        logger.debug("AssignmentStudent entities created.")

        assignment_in_db = Assignment(
            title=assignment.title,
            is_published=assignment.is_published,
            submission_last_date=assignment.submission_last_date,
            teacher_id=user_id,
            questions=assignment_question_list,
            classes=assignment_classes_list,
            students=assignment_students_list
        )
        logger.debug("Assignment entity created.")

        assignment_in_db = assignment_dao.save(assignment_in_db)
        logger.debug("complete assignment saved successfully.")

        return self.__get_formatted_assignment(assignment_in_db)

    def update_assignment(self, assignment: UpdateAssignmentRequest, user_id: str):

        assignment_in_db = assignment_dao.find_by_id(assignment.id)
        if(assignment_in_db == None):
            logger.debug("assignmnet_id not found in the db.")
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        if(assignment_in_db.teacher_id != user_id):
            logger.debug("assignment teacher id and user id do not match. assignment_teacher_id:{} user_id:{}".format(
                assignment_in_db.teacher_id, user_id))
            raise HTTPException(
                401, detail="Not authorized to update the assignment")

        assignment_classes_list, assignment_students_list = self.__update_assignment_classes(
            assignment.id, assignment_in_db.classes, assignment.classes)

        assignment_questions_list = self.__update_assignment_topics(
            assignment_in_db.questions, assignment.topics)

        self.__update_assignment_student_questions(
            assignment_students_list, assignment_questions_list)

        # assignment_students_list = self.__update_assignment_students(
        #     assignment_in_db.classes, assignment.classes)

        # assignment_question_list = [AssignmentQuestion(
        #     question_id=i.question_id, sequence_num=i.sequence_num) for i in assignment.questions]

        # assignment_classes_list = [AssignmentClass(class_id=i.class_id)
        #                            for i in assignment.classes]

        assignment_in_db.title = assignment.title
        assignment_in_db.is_published = assignment.is_published
        assignment_in_db.submission_last_date = assignment.submission_last_date
        assignment_in_db.questions = assignment_questions_list
        assignment_in_db.classes = assignment_classes_list
        assignment_in_db.students = assignment_students_list
        assignment_in_db = assignment_dao.save(assignment_in_db)

        return self.__get_formatted_assignment(assignment_in_db)

    def __update_assignment_topics(self, questions_in_db, topics_in_request):
        logger.debug("updating assignment topics")
        assignment_questions_list = []

        db_ques_mapping = defaultdict(list)
        for ques in questions_in_db:
            db_ques_mapping[(ques.question_id,
                             ques.topic_code,
                             ques.cluster_id)].append(ques)

        for topic in topics_in_request:
            for ques in topic.questions:
                ques_list_in_db = db_ques_mapping.get(
                    (ques.question_id, topic.topic_code, topic.cluster_id))
                if(ques_list_in_db == None or len(ques_list_in_db) == 0):
                    logger.debug("creating as new assignment question. question_id:{} topic_code:{} cluster_id:{}".format(
                        ques.question_id, topic.topic_code, topic.cluster_id))
                    assignment_questions_list.append(AssignmentQuestion(
                        question_id=ques.question_id,
                        sequence_num=ques.sequence_num,
                        tutor_available=ques.tutor_available,
                        topic_code=topic.topic_code,
                        topic_sequence_num=topic.topic_sequence_num,
                        cluster_id=topic.cluster_id,
                        topic_tutor_available=topic.tutor_available
                    ))
                else:
                    logger.debug("assignment question already exists in the db. question_id:{} topic_code:{} cluster_id:{}".format(
                        ques.question_id, topic.topic_code, topic.cluster_id))
                    ques_in_db = ques_list_in_db.pop()
                    ques_in_db.sequence_num = ques.sequence_num
                    ques_in_db.tutor_available = ques.tutor_available
                    ques_in_db.topic_sequence_num = topic.topic_sequence_num
                    ques_in_db.topic_tutor_available = topic.tutor_available
                    ques_in_db.cluster_id = topic.cluster_id
                    assignment_questions_list.append(ques_in_db)

        return assignment_questions_list

    def __update_assignment_classes(self, id, classes_in_db, classes_in_request):
        logger.debug("updating assignment classes")

        assignment_classes_list = []
        assignment_students_list = []

        db_class_map = {
            db_class.class_id: db_class for db_class in classes_in_db}

        for req_class in classes_in_request:
            current_class = db_class_map.get(req_class.class_id)
            if(current_class == None):
                logger.debug("assignment assigned to new class with class_id:{}".format(
                    req_class.class_id))
                assignment_classes_list.append(
                    AssignmentClass(class_id=req_class.class_id))
                db_students_map = {}
            else:
                logger.debug("assignment was already assigned to class_id:{}".format(
                    req_class.class_id))
                assignment_classes_list.append(current_class)
                students_in_db = assignment_student_dao.find_students_by_assignment_id_and_class_id(
                    id, req_class.class_id)
                db_students_map = {
                    student.student_id: student for student in students_in_db}

            logger.debug("fetching the students of the class class_id:{} from classroom service api.".format(
                req_class.class_id))
            all_class_students = classroom_service.get_students(
                req_class.class_id)

            for student in all_class_students:
                student_in_db = db_students_map.get(
                    student["uuid"], None)

                if(student_in_db != None):
                    logger.debug("assignment already assigned to the student. student_id:{} class_id:{}".format(
                        student_in_db.student_id, student_in_db.class_id))
                    assignment_students_list.append(student_in_db)
                else:
                    logger.debug("assignment assigning to a new student student_id:{} class_id:{}".format(
                        student["uuid"], student["class_id"]))
                    assignment_students_list.append(
                        AssignmentStudent(
                            student_id=student["uuid"],
                            class_id=student["class_id"],
                            first_name=student["first_name"],
                            last_name=student["last_name"],
                            email=student["email"],
                            parents_email=student["parents_email"],
                            questions=[]
                        ))

        # for req_class in classes_in_request:
        #     all_class_students = classroom_service.get_students(
        #         req_class.class_id)

        #     for db_class in classes_in_db:
        #         if(req_class.class_id == db_class.class_id):
        #             assignment_classes_list.append(db_class)
        #             current_class_students = assignment_student_dao.find_students_by_assignment_id_and_class_id(
        #                 id, req_class.class_id)

        #             assignment_students_list.extend(current_class_students)
        #             break
        #     else:
        #         assignment_classes_list.append(
        #             AssignmentClass(class_id=req_class.class_id))
        #         for student in all_class_students:
        #             assignment_students_list.append(
        #                 AssignmentStudent(
        #                     student_id=student["uuid"],
        #                     class_id=student["class_id"],
        #                     first_name=student["first_name"],
        #                     last_name=student["last_name"],
        #                     email=student["email"],
        #                     parents_email=student["parents_email"],
        #                     questions=[]
        #                 ))
        return assignment_classes_list, assignment_students_list

    def __update_assignment_student_questions(self, assignment_students_list, assignment_questions_list):
        logger.debug("updating assignment student questions.")

        for student in assignment_students_list:

            assignment_student_questions_list = []

            for questions_in_req in assignment_questions_list:
                for questions_in_db in student.questions:
                    if(questions_in_db.question_id == questions_in_req.question_id):
                        logger.debug("assignment student question already present in db. question_id:{}".format(
                            questions_in_req.question_id))
                        assignment_student_questions_list.append(
                            questions_in_db)
                        break
                else:
                    logger.debug("creating a new assignmnet student question. question_id:{}".format(
                        questions_in_req.question_id))
                    assignment_student_questions_list.append(
                        AssignmentStudentQuestion(question_id=questions_in_req.question_id))

            student.questions = assignment_student_questions_list

    def add_students(self, class_students: ClassStudentsRequest):
        logger.debug("adding new students.")
        assignment_updated = []
        studnets_added = []
        for student in class_students.students:
            class_id = student.class_id
            class_assignments = assignment_dao.find_assignment_by_class_id_and_submission_last_date_greater_than(
                class_id, datetime.utcnow())
            logger.debug("all active assignments for the class class_id:{} active_assignmnets:{}".format(
                class_id, [assign.id for assign in class_assignments]))
            for assignment in class_assignments:
                assignment.students.append(
                    AssignmentStudent(
                        student_id=student.student_id,
                        class_id=student.class_id,
                        first_name=student.first_name,
                        last_name=student.last_name,
                        email=student.email,
                        parents_email=student.parents_email,
                        questions=[AssignmentStudentQuestion(
                            question_id=ques.question_id) for ques in assignment.questions]
                    )
                )
                assignment_updated.append(assignment)
            studnets_added.append(student)
            logger.debug("active assignments assigned to the student student_id:{}".format(
                student.student_id))

        assignment_dao.save_all(assignment_updated)
        logger.debug("all students saved in db.")

        return ClassStudentsResponse(students=studnets_added)

    def delete_students(self, class_students: ClassStudentsRequest):
        logger.debug(
            "deleting students and assignments related to the students.")
        studnets_deleted = []
        for student in class_students.students:

            deleted_count = assignment_student_dao.delete_assignment_by_class_id_and_student_id_and_submission_last_date_greater_than(
                student.class_id, student.student_id, student.email, datetime.utcnow())

            if(deleted_count > 0):
                studnets_deleted.append(student)
                logger.debug("deleted {} assignment_students for student student_id:{}".format(
                    deleted_count, student.student_id))

        return ClassStudentsResponse(students=studnets_deleted)

    def delete_assignment(self, assignment_id: int, user_id: str):
        logger.debug("deleting assignment.")

        assignment_in_db = assignment_dao.find_by_id(assignment_id)

        if(assignment_in_db == None):
            logger.debug(
                "assignment not found in the db assignment_id:{}".format(assignment_id))
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        if(assignment_in_db.teacher_id != user_id):
            logger.debug("assignment teacher id and user id do not match. assignment_teacher_id:{} user_id:{}".format(
                assignment_in_db.teacher_id, user_id))
            raise HTTPException(401, detail="Not Authorized")

        assignment_dao.delete(assignment_id)
        logger.debug(
            "assignment deleted successfully. assignment_id:{}".format(assignment_id))

        return {"detail": "resource deleted successfully"}

    def copy_assignment(self, assignment_id: int, user_id: str):
        logger.debug("copying assignment")

        assignment_in_db = assignment_dao.find_by_id(assignment_id)

        if(assignment_in_db == None):
            logger.debug(
                "assignment not found in the db assignment_id:{}".format(assignment_id))
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        if(assignment_in_db.teacher_id != user_id):
            logger.debug("assignment teacher id and user id do not match. assignment_teacher_id:{} user_id:{}".format(
                assignment_in_db.teacher_id, user_id))
            raise HTTPException(401, detail="Not Authorized")

        new_assignment = assignment_dao.clone(assignment_in_db)
        logger.debug("assignment cloned successfully")

        return self.__get_formatted_assignment(new_assignment)

    def updateAssignmentStatus(self, updateAssignmentPublishStatusRequest: UpdateAssignmentPublishStatusRequest, user_id: str):
        logger.debug("update assignment status")

        assignment_in_db = assignment_dao.find_by_id(
            updateAssignmentPublishStatusRequest.id)

        if(assignment_in_db == None):
            logger.debug(
                "assignment not found in the db assignment_id:{}".format(updateAssignmentPublishStatusRequest.id))
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        if(assignment_in_db.teacher_id != user_id):
            logger.debug("assignment teacher id and user id do not match. assignment_teacher_id:{} user_id:{}".format(
                assignment_in_db.teacher_id, user_id))
            raise HTTPException(401, detail="Not Authorized")

        logger.debug("assignment current status. is_published:{}".format(
            assignment_in_db.is_published))
        logger.debug("assignment requested status. is_published:{}".format(
            updateAssignmentPublishStatusRequest.is_published))

        assignment_in_db.is_published = updateAssignmentPublishStatusRequest.is_published

        updated_assignment = assignment_dao.save(assignment_in_db)
        logger.debug("assignment status updated successfully")

        return self.__get_formatted_assignment(updated_assignment)

    # def get_all_student_assignments(self, user_id: str):
        logger.debug("gets all assignment students")
        all_assignments_student_in_db = assignment_student_dao.find_assignments_by_student_id_and_is_published(
            user_id)

        completed = []
        active = []

        for assignment_student in all_assignments_student_in_db:
            completed_count, total_count = self.__get_completed_count(
                assignment_student.questions)

            assignemnt_details = BasicAssignementDetailsStudentResponse(
                assignment_id=assignment_student.assignment_id,
                title=assignment_student.assignment.title,
                progress="{completed_count}/{total_count}".format(
                    completed_count=completed_count, total_count=total_count),
                due_date=assignment_student.assignment.submission_last_date,
                late=False,
                completed=(assignment_student.status ==
                           AssignmentStatusEnum.COMPLETED),
            )

            if(assignment_student.status == AssignmentStatusEnum.COMPLETED):
                completed.append(assignemnt_details)
            else:
                active.append(assignemnt_details)

        return AllAssignmentStudentResponse(
            student_id=user_id,
            active=active,
            completed=completed
        )

    def complete_question(self, assignment_id, question_id, user_id):
        logger.debug("completing a question")

        assignment_student = assignment_student_dao.find_assignment_student_by_assignment_id_and_student_id_and_is_published(
            assignment_id, user_id)

        if(assignment_student == None):
            logger.debug("student assigned to this assignment not found. assignment_id:{} student_id:{}".format(
                assignment_id, user_id))
            raise HTTPException(
                401, detail="Not able to find assignment assigned to the student")

        for ques in assignment_student.questions:
            if(ques.question_id == question_id):
                logger.debug("marking assignment question as complete. assignment_id:{} question_id:{}".format(
                    assignment_id, question_id))
                ques.completed = True
                ques.completed_at = datetime.utcnow()
                assignment_student_dao.save(assignment_student)
                break
        else:
            logger.debug("assignment question not found. assignment_id:{} question_id:{}".format(
                assignment_id, question_id))
            raise HTTPException(
                401, detail="Invalid Question Id")

    def get_all_student_active_assignments(self, user_id: str, all: bool):
        logger.debug("get all active assignments.")

        logger.debug("all={}".format(all))
        if(all == False):
            logger.debug("limiting the data retrival to 10 only")
            all_assignments_student_in_db = assignment_student_dao.find_assignments_by_student_id_and_is_published_and_is_not_completed_and_is_limited_order_by_submission_last_date(
                user_id, 0, 10)
        else:
            logger.debug("retriving all data from db.")
            all_assignments_student_in_db = assignment_student_dao.find_assignments_by_student_id_and_is_published_and_is_not_completed_order_by_submission_last_date(
                user_id)

        total_count = assignment_student_dao.count_assignments_by_student_id_and_is_published_and_is_not_completed_order_by_submission_last_date(
            user_id)

        logger.debug("formatting the assignments in the response.")
        all_assignments = self.get_formatted_assignments(
            all_assignments_student_in_db)

        return AllAssignmentStudentResponse(
            student_id=user_id,
            assignments=all_assignments,
            total_count=total_count
        )

    def get_all_student_completed_assignments(self, user_id: str, start: int, limit: int):
        logger.debug("get all completed assignments.")
        all_assignments_student_in_db = assignment_student_dao.find_assignments_by_student_id_and_is_published_and_is_completed_and_is_limited_order_by_submission_last_date(
            user_id, start, limit)

        logger.debug("formatting the assignments in the response.")
        all_assignments = self.get_formatted_assignments(
            all_assignments_student_in_db)

        logger.debug("counting the number of completed assignments.")
        total_count = assignment_student_dao.count_assignments_by_student_id_and_is_published_and_is_completed_order_by_submission_last_date(
            user_id)

        return AllAssignmentStudentResponse(
            student_id=user_id,
            assignments=all_assignments,
            total_count=total_count
        )

    def get_formatted_assignments(self, all_assignments_student_in_db):
        logger.debug("formatting the assignment.")
        all_assignments = []

        for assignment_student in all_assignments_student_in_db:
            completed_count, total_count = self.__get_completed_count(
                assignment_student.questions)

            late = datetime.utcnow() > assignment_student.assignment.submission_last_date

            has_started = (assignment_student.status !=
                           AssignmentStatusEnum.NOT_ATTEMPTED)

            nearby_day = self.__get_nearby_day(
                assignment_student.assignment.submission_last_date.date())

            if(nearby_day == None):
                due_date = assignment_student.assignment.submission_last_date.strftime(
                    "%b %d, %Y at %I:%M %p")
            else:
                due_date = assignment_student.assignment.submission_last_date.strftime(
                    "{} at %I:%M %p".format(nearby_day))

            assignment_details = BasicAssignementDetailsStudentResponse(
                assignment_id=assignment_student.assignment_id,
                title=assignment_student.assignment.title,
                progress="{completed_count}/{total_count}".format(
                    completed_count=completed_count, total_count=total_count),
                due_date=due_date,
                utc_due_time=assignment_student.assignment.submission_last_date,
                late=late,
                completed=(assignment_student.status ==
                           AssignmentStatusEnum.COMPLETED),
                has_started=has_started,
                nearby_day=nearby_day
            )
            all_assignments.append(assignment_details)

        return all_assignments

    def __get_completed_count(self, questions_list):
        logger.debug("get completed count")
        total_count = 0
        competed_count = 0
        for ques in questions_list:
            if(ques.status != QuestionStatusEnum.NOT_ATTEMPTED):
                competed_count += 1
            total_count += 1
        logger.debug("completed_count:{} total_count:{}".format(
            competed_count, total_count))
        return competed_count, total_count

    def __get_nearby_day(self, assignment_date):
        logger.debug(
            "getting nearby day from the date given. (i.e. Yesterday, Today, Tomorrow)")
        if(assignment_date == datetime.utcnow().date() + timedelta(days=0)):
            nearby_day = "Today"
        elif(assignment_date == datetime.utcnow().date() + timedelta(days=1)):
            nearby_day = "Tomorrow"
        elif(assignment_date == datetime.utcnow().date() + timedelta(days=-1)):
            nearby_day = "Yesterday"
        else:
            nearby_day = None
        logger.debug("current_time:{} narby_day:{}".format(
            datetime.utcnow().date(), nearby_day))
        return nearby_day

    def get_next_question(self, assignment_id, user_id):
        logger.debug("get next assignment question")
        assignment_student, student_questions, assignment_questions = self.__get_assignment_and_student_questions(
            assignment_id, user_id)

        ques_count = 0
        for ques_assign in assignment_questions:
            ques_student = student_questions.get(ques_assign.question_id)
            ques_count += 1

            if(ques_student == None or len(ques_student) == 0):
                logger.debug("question not assigned to the student. question_id:{}".format(
                    ques_assign.question_id))
                raise HTTPException(
                    401, detail="Some Issue ... question in assignment but not assigned to the student")

            question = ques_student.pop()

            if(question.status == QuestionStatusEnum.NOT_ATTEMPTED):

                logger.debug(
                    "updated assignment student status to IN_PROGRESS")
                assignment_student.status = AssignmentStatusEnum.IN_PROGRESS

                logger.debug(
                    "extracted question details fromm question_dashboard.")
                question = question_dashboard_service.get_question(
                    ques_assign.question_id)

                return StudentNextQuestionDetailsResponse(
                    student_id=assignment_student.student_id,
                    class_id=assignment_student.class_id,
                    assignment_id=assignment_student.assignment_id,
                    question_id=ques_assign.question_id,
                    question_str=question.get(
                        QuestionDashboradServiceConstants.Data.DESCRIPTION, None),
                    question_complete_data=question,
                    tutor_available=ques_assign.tutor_available,
                    current_seq_number=ques_count,
                    total_questions=len(assignment_questions),
                    assignment_complete=False
                )

        if(assignment_student.status != AssignmentStatusEnum.COMPLETED):
            logger.debug("updated assignment student status to COMPLETED")
            assignment_student.status = AssignmentStatusEnum.COMPLETED
            assignment_student.completed_at = datetime.utcnow()

        return StudentNextQuestionDetailsResponse(
            student_id=assignment_student.student_id,
            class_id=assignment_student.class_id,
            assignment_id=assignment_student.assignment_id,
            question_id=None,
            question_str=None,
            tutor_available=None,
            current_seq_number=None,
            total_questions=len(assignment_questions),
            assignment_complete=True
        )

    def __get_assignment_and_student_questions(self, assignment_id, user_id):
        logger.debug("get all questions of an assignment.")
        assignment_student = assignment_student_dao.find_assignment_student_by_assignment_id_and_student_id_and_is_published(
            assignment_id, user_id)

        if(assignment_student == None):
            logger.debug("assignment student not found")
            raise HTTPException(
                401, detail="Not able to find assignment assigned to the student")

        student_questions = defaultdict(list)
        for ques_student in assignment_student.questions:
            student_questions[ques_student.question_id].append(ques_student)

        assignment_questions = assignment_student.assignment.questions
        assignment_questions.sort()
        return assignment_student, student_questions, assignment_questions

    def complete_next_question(self, assignment_id, status, user_id):
        logger.debug("complete next question")
        assignment_student, student_questions, assignment_questions = self.__get_assignment_and_student_questions(
            assignment_id, user_id)

        ques_count = 0
        for ques_assign in assignment_questions:
            ques_count += 1
            ques_student = student_questions.get(ques_assign.question_id)

            if(ques_student == None or len(ques_student) == 0):
                logger.debug("question not assigned to the student. question_id:{}".format(
                    ques_assign.question_id))
                raise HTTPException(
                    401, detail="Some Issue ... question in assignment but not assigned to this student")

            question = ques_student.pop()

            if(question.status == QuestionStatusEnum.NOT_ATTEMPTED):
                question.status = status

                assignment_complete = (ques_assign == assignment_questions[-1])
                if(assignment_complete):
                    logger.debug("was last question. student_assignment_complete:{}".format(
                        assignment_complete))
                    assignment_student.status = AssignmentStatusEnum.COMPLETED
                    assignment_student.completed_at = datetime.utcnow()
                else:
                    logger.debug("student_assignment_complete:{}".format(
                        assignment_complete))
                    assignment_student.status = AssignmentStatusEnum.IN_PROGRESS

                assignment_student_dao.save(assignment_student)
                logger.debug("nxt question completed and saved successfully")

                return StudentQuestionCompleteResponse(
                    student_id=assignment_student.student_id,
                    class_id=assignment_student.class_id,
                    assignment_id=assignment_student.assignment_id,
                    question_id=ques_assign.question_id,
                    # completed=ques_student.completed,
                    status=question.status,
                    current_seq_number=ques_count,
                    total_questions=len(assignment_questions),
                    assignment_complete=(
                        ques_assign == assignment_questions[-1])
                )

        logger.debug("student assignment already complete.")
        return StudentQuestionCompleteResponse(
            student_id=assignment_student.student_id,
            class_id=assignment_student.class_id,
            assignment_id=assignment_student.assignment_id,
            question_id=None,
            completed=None,
            status=None,
            current_seq_number=None,
            total_questions=len(assignment_questions),
            assignment_complete=True
        )


assignment_service = AssignmentService()
